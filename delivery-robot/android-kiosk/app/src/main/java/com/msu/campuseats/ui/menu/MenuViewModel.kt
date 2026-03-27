package com.msu.campuseats.ui.menu

import androidx.lifecycle.ViewModel
import com.msu.campuseats.data.MockDataSource
import com.msu.campuseats.data.models.MenuItem
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class MenuViewModel : ViewModel() {
    private val _selectedCategory = MutableStateFlow("Popular")
    val selectedCategory: StateFlow<String> = _selectedCategory.asStateFlow()

    fun setCategory(category: String) {
        _selectedCategory.value = category
    }

    fun categoriesForVendor(vendorId: String): List<String> {
        val categories = MockDataSource.getMenuForVendor(vendorId).map { it.category }.distinct()
        return if ("Popular" in categories) categories else listOf("Popular") + categories
    }

    fun menuForVendor(vendorId: String): List<MenuItem> = MockDataSource.getMenuForVendor(vendorId)
}
