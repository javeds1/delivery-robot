package com.msu.campuseats.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val LightColors = lightColorScheme(
    primary = Color(0xFF0F766E),
    secondary = Color(0xFF2A9D8F),
    tertiary = Color(0xFFFF6F00),
    surface = Color.White,
    background = Color(0xFFF9FAFB)
)

private val DarkColors = darkColorScheme(
    primary = Color(0xFF70C1B3),
    secondary = Color(0xFF4AAE9B),
    tertiary = Color(0xFFFFB74D)
)

@Composable
fun CampusEatsTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = LightColors,
        typography = MaterialTheme.typography,
        content = content
    )
}
