package com.msu.campuseats

import android.graphics.Color
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsControllerCompat
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.compose.runtime.collectAsState
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.msu.campuseats.navigation.AppNavGraph
import com.msu.campuseats.ui.theme.CampusEatsTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val green = Color.parseColor("#0F766E")
        WindowCompat.setDecorFitsSystemWindows(window, true)
        window.statusBarColor = green
        window.navigationBarColor = green
        WindowInsetsControllerCompat(window, window.decorView).apply {
            isAppearanceLightStatusBars = false
            isAppearanceLightNavigationBars = false
        }
        setContent {
            CampusEatsTheme {
                val cartViewModel: CartViewModel = viewModel()
                val sessionViewModel: SessionViewModel = viewModel()
                val isAuthenticated = sessionViewModel.isAuthenticated.collectAsState().value
                val isLoading = sessionViewModel.isLoading.collectAsState().value
                val error = sessionViewModel.error.collectAsState().value
                if (isAuthenticated) {
                    AppNavGraph(cartViewModel = cartViewModel)
                } else if (isLoading) {
                    Column(
                        modifier = Modifier.fillMaxSize().padding(24.dp),
                        verticalArrangement = Arrangement.Center,
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        CircularProgressIndicator()
                        Text("Connecting kiosk service...", modifier = Modifier.padding(top = 12.dp))
                    }
                } else {
                    Column(
                        modifier = Modifier.fillMaxSize().padding(24.dp),
                        verticalArrangement = Arrangement.Center,
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(
                            text = error ?: "Service unavailable",
                            style = MaterialTheme.typography.titleMedium,
                            color = MaterialTheme.colorScheme.error
                        )
                    }
                }
            }
        }
    }
}
