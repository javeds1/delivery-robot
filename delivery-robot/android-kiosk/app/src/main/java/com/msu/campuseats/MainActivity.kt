package com.msu.campuseats

import android.graphics.Color
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsControllerCompat
import androidx.lifecycle.viewmodel.compose.viewModel
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
                AppNavGraph(cartViewModel = cartViewModel)
            }
        }
    }
}
