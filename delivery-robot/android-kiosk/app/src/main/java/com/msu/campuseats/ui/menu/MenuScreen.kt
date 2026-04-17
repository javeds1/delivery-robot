package com.msu.campuseats.ui.menu

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.msu.campuseats.CartViewModel
import com.msu.campuseats.data.MockDataSource
import com.msu.campuseats.ui.components.CartFab
import com.msu.campuseats.ui.components.MenuItemCard

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MenuScreen(
    vendorId: String,
    cartViewModel: CartViewModel,
    onBack: () -> Unit,
    onCartClick: () -> Unit
) {
    val menuViewModel: MenuViewModel = viewModel()
    val selectedCategory by menuViewModel.selectedCategory.collectAsState()
    val vendor = MockDataSource.getVendor(vendorId) ?: return
    val allItems = menuViewModel.menuForVendor(vendorId)
    val categories = menuViewModel.categoriesForVendor(vendorId)
    val items = allItems.filter { it.category == selectedCategory }
    val cartItems by cartViewModel.cartItems.collectAsState()
    val total by cartViewModel.total.collectAsState(0.0)

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(vendor.name) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        },
        floatingActionButton = {
            CartFab(
                itemCount = cartItems.sumOf { it.quantity },
                total = total,
                onClick = onCartClick
            )
        }
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            item {
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Text(text = vendor.name, style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold)
                    Text(text = "${vendor.cuisine} • ${vendor.estimatedTime}", style = MaterialTheme.typography.bodyMedium)
                    Text(text = vendor.description, style = MaterialTheme.typography.bodySmall)
                }
            }
            item {
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    categories.forEach { category ->
                        FilterChip(
                            selected = selectedCategory == category,
                            onClick = { menuViewModel.setCategory(category) },
                            label = { Text(category) }
                        )
                    }
                }
            }
            items(items) { menuItem ->
                val qty = cartViewModel.quantityFor(menuItem.id)
                MenuItemCard(
                    menuItem = menuItem,
                    quantityInCart = qty,
                    onAdd = { cartViewModel.addItem(menuItem) },
                    onIncrement = { cartViewModel.addItem(menuItem) },
                    onDecrement = { cartViewModel.removeItem(menuItem) }
                )
            }
        }
    }
}
