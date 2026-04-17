package com.msu.campuseats.ui.home

import androidx.lifecycle.ViewModel
import com.msu.campuseats.data.MockDataSource
import com.msu.campuseats.data.models.Vendor
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class HomeViewModel : ViewModel() {
    private val _vendors = MutableStateFlow(MockDataSource.vendors)
    val vendors: StateFlow<List<Vendor>> = _vendors.asStateFlow()
}
