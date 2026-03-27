package com.msu.campuseats.ui.home

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
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
import com.msu.campuseats.ui.components.CartFab
import com.msu.campuseats.ui.components.VendorCard

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    cartViewModel: CartViewModel,
    onVendorClick: (String) -> Unit,
    onCartClick: () -> Unit
) {
    val homeViewModel: HomeViewModel = viewModel()
    val vendors by homeViewModel.vendors.collectAsState()
    val cartItems by cartViewModel.cartItems.collectAsState()
    val total by cartViewModel.total.collectAsState(0.0)

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("Campus Eats", fontWeight = FontWeight.Bold)
                        Text("\uD83C\uDF93")
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
                OutlinedTextField(
                    value = "",
                    onValueChange = {},
                    readOnly = true,
                    leadingIcon = { Icon(Icons.Default.Search, contentDescription = null) },
                    placeholder = { Text("Search restaurants or items") },
                    modifier = Modifier.fillMaxWidth()
                )
            }
            item {
                Text(
                    text = "Restaurants & Vendors",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold
                )
            }
            items(vendors) { vendor ->
                VendorCard(
                    vendor = vendor,
                    onClick = { onVendorClick(vendor.id) }
                )
            }
        }
    }
}
