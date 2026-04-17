package com.msu.campuseats.navigation

import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.msu.campuseats.CartViewModel
import com.msu.campuseats.data.MockDataSource
import com.msu.campuseats.ui.cart.CartScreen
import com.msu.campuseats.ui.confirmation.OrderConfirmationScreen
import com.msu.campuseats.ui.home.HomeScreen
import com.msu.campuseats.ui.menu.MenuScreen
import java.net.URLDecoder
import java.net.URLEncoder
import java.nio.charset.StandardCharsets

object AppRoutes {
    const val HOME = "home"
    const val MENU = "menu/{vendorId}"
    const val CART = "cart"
    const val CONFIRMATION = "confirmation/{location}"
}

@Composable
fun AppNavGraph(cartViewModel: CartViewModel) {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = AppRoutes.HOME) {
        composable(AppRoutes.HOME) {
            HomeScreen(
                cartViewModel = cartViewModel,
                onVendorClick = { vendorId -> navController.navigate("menu/$vendorId") },
                onCartClick = { navController.navigate(AppRoutes.CART) }
            )
        }

        composable(
            route = AppRoutes.MENU,
            arguments = listOf(navArgument("vendorId") { type = NavType.StringType })
        ) { backStack ->
            val vendorId = backStack.arguments?.getString("vendorId").orEmpty()
            MenuScreen(
                vendorId = vendorId,
                cartViewModel = cartViewModel,
                onBack = { navController.popBackStack() },
                onCartClick = { navController.navigate(AppRoutes.CART) }
            )
        }

        composable(AppRoutes.CART) {
            CartScreen(
                cartViewModel = cartViewModel,
                onBack = { navController.popBackStack() },
                onBrowseMenu = { navController.popBackStack() },
                onPlaceOrder = { location ->
                    val encoded = URLEncoder.encode(location, StandardCharsets.UTF_8.toString())
                    navController.navigate("confirmation/$encoded")
                }
            )
        }

        composable(
            route = AppRoutes.CONFIRMATION,
            arguments = listOf(navArgument("location") { type = NavType.StringType })
        ) { backStack ->
            val items by cartViewModel.cartItems.collectAsState()
            val total by cartViewModel.total.collectAsState(0.0)
            val location = URLDecoder.decode(
                backStack.arguments?.getString("location").orEmpty(),
                StandardCharsets.UTF_8.toString()
            )
            val vendorName = MockDataSource.getVendor(cartViewModel.cartVendorName())?.name ?: "Campus Eats"
            OrderConfirmationScreen(
                vendorName = vendorName,
                items = items,
                total = total,
                location = location,
                onBackHome = {
                    cartViewModel.clearCart()
                    navController.navigate(AppRoutes.HOME) {
                        popUpTo(AppRoutes.HOME) { inclusive = true }
                        launchSingleTop = true
                    }
                }
            )
        }
    }
}
