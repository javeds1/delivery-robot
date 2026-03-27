package com.msu.campuseats.data.models

data class MenuItem(
    val id: String,
    val vendorId: String,
    val name: String,
    val description: String,
    val price: Double,
    val category: String
)
