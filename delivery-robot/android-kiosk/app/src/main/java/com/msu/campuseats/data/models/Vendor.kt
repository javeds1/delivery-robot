package com.msu.campuseats.data.models

data class Vendor(
    val id: String,
    val name: String,
    val cuisine: String,
    val estimatedTime: String,
    val isOpen: Boolean,
    val emoji: String,
    val description: String
)
