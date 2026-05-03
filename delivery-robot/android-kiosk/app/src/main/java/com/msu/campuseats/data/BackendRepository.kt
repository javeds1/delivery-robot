package com.msu.campuseats.data

import com.msu.campuseats.BuildConfig
import com.msu.campuseats.data.models.CartItem
import com.msu.campuseats.data.models.MenuItem
import com.msu.campuseats.data.models.Vendor
import com.msu.campuseats.data.remote.ApiClient
import com.msu.campuseats.data.remote.CreateOrderItemRequest
import com.msu.campuseats.data.remote.CreateOrderRequest
import com.msu.campuseats.data.remote.SessionStore
import com.msu.campuseats.data.remote.refreshAccessTokenBlocking
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

object BackendRepository {
    private val api = ApiClient.api

    suspend fun bootstrapKioskSession(): Boolean {
        val refreshed = synchronized(SessionStore.lock) { refreshAccessTokenBlocking() }
        if (refreshed) return true
        return login(BuildConfig.KIOSK_USERNAME, BuildConfig.KIOSK_PASSWORD)
    }

    suspend fun login(username: String, password: String): Boolean = withContext(Dispatchers.IO) {
        runCatching {
            val response = api.login(mapOf("username" to username, "password" to password))
            synchronized(SessionStore.lock) {
                SessionStore.accessToken = response.access
                SessionStore.refreshToken = response.refresh
            }
            true
        }.getOrElse { false }
    }

    fun logout() {
        synchronized(SessionStore.lock) {
            SessionStore.clear()
        }
    }

    fun isAuthenticated(): Boolean = synchronized(SessionStore.lock) {
        !SessionStore.accessToken.isNullOrBlank()
    }

    suspend fun getVendors(): List<Vendor> = withContext(Dispatchers.IO) {
        api.getVendors().map { dto ->
            Vendor(
                id = dto.id.toString(),
                backendId = dto.id,
                name = dto.name,
                cuisine = dto.locationLabel,
                estimatedTime = "Delivery ETA shown at checkout",
                isOpen = dto.isActive && !dto.intakePaused,
                emoji = "\uD83C\uDF7D",
                description = dto.locationLabel
            )
        }
    }

    suspend fun getMenuForVendor(vendorId: Int, vendorName: String): List<MenuItem> = withContext(Dispatchers.IO) {
        api.getMenuItems()
            .filter { it.vendor == vendorId && it.isAvailable }
            .map { dto ->
                MenuItem(
                    id = dto.id.toString(),
                    backendId = dto.id,
                    vendorId = dto.vendor.toString(),
                    vendorBackendId = dto.vendor,
                    vendorName = vendorName,
                    name = dto.name,
                    description = dto.description,
                    price = dto.price.toDoubleOrNull() ?: 0.0,
                    category = "Menu"
                )
            }
    }

    suspend fun placeOrder(
        cartItems: List<CartItem>,
        location: String,
        studentName: String,
        phone: String,
        email: String
    ): Int? = withContext(Dispatchers.IO) {
        val vendorId = cartItems.firstOrNull()?.menuItem?.vendorBackendId ?: return@withContext null
        // Backend Order.phone max_length is 20 — must fit or Postgres/Django raises (often surfacing as 500).
        val normalizedPhone = when {
            phone.isNotBlank() -> phone.trim().take(20)
            email.isNotBlank() -> {
                val e = email.trim()
                val prefix = "E:"
                val maxBody = (20 - prefix.length).coerceAtLeast(4)
                if (e.length <= maxBody) "$prefix$e" else prefix + e.take(maxBody - 3) + "..."
            }
            else -> "KIOSK-UNKNOWN"
        }
        val normalizedName = studentName.ifBlank { "Kiosk Guest" }
        val items = cartItems.map { item ->
            CreateOrderItemRequest(menuItemId = item.menuItem.backendId, quantity = item.quantity)
        }
        runCatching {
            api.createOrder(
                CreateOrderRequest(
                    studentName = normalizedName,
                    phone = normalizedPhone,
                    vendorId = vendorId,
                    deliveryLocation = location,
                    items = items
                )
            ).id
        }.getOrNull()
    }
}

