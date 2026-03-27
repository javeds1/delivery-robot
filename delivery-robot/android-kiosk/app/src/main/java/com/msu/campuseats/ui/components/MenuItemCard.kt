package com.msu.campuseats.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.defaultMinSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.msu.campuseats.data.models.MenuItem

@Composable
fun MenuItemCard(
    menuItem: MenuItem,
    quantityInCart: Int,
    onAdd: () -> Unit,
    onIncrement: () -> Unit,
    onDecrement: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 3.dp)
    ) {
        Row(
            modifier = Modifier.padding(12.dp),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(56.dp)
                    .background(Color(0xFFFFE0B2), RoundedCornerShape(8.dp))
            )
            Column(modifier = Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(text = menuItem.name, style = MaterialTheme.typography.titleSmall)
                Text(
                    text = menuItem.description,
                    style = MaterialTheme.typography.bodySmall,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
                Text(text = "$${"%.2f".format(menuItem.price)}", style = MaterialTheme.typography.labelLarge)
            }

            if (quantityInCart <= 0) {
                Button(
                    onClick = onAdd,
                    modifier = Modifier.defaultMinSize(minHeight = 48.dp),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Text("+ Add")
                }
            } else {
                QuantityStepper(
                    quantity = quantityInCart,
                    onDecrement = onDecrement,
                    onIncrement = onIncrement
                )
            }
        }
        Spacer(modifier = Modifier.height(4.dp))
    }
}
