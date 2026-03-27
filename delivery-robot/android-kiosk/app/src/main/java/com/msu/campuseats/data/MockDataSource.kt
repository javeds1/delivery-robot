package com.msu.campuseats.data

import com.msu.campuseats.data.models.MenuItem
import com.msu.campuseats.data.models.Vendor

object MockDataSource {
    val vendors = listOf(
        Vendor("hawks", "The Hawk's Nest Deli", "Deli", "15-20 min", true, "\uD83E\uDD6A", "Fresh deli classics made fast."),
        Vendor("grill", "Campus Grill", "American Grill", "20-25 min", true, "\uD83C\uDF54", "Burgers, fries, and comfort favorites."),
        Vendor("green", "Green Bowl", "Healthy", "10-15 min", true, "\uD83E\uDD57", "Salads, bowls, and lighter options."),
        Vendor("brew", "Brew & Bites Cafe", "Cafe", "12-18 min", false, "\u2615", "Coffee, pastries, and quick bites.")
    )

    private val vendorMenus: Map<String, List<MenuItem>> = mapOf(
        "hawks" to listOf(
            MenuItem("hawks-1", "hawks", "Italian Hero", "Salami, ham, provolone, peppers", 9.49, "Popular"),
            MenuItem("hawks-2", "hawks", "Turkey Club", "Turkey, bacon, lettuce, tomato", 8.99, "Mains"),
            MenuItem("hawks-3", "hawks", "Roast Beef Melt", "Roast beef, onions, Swiss cheese", 10.29, "Mains"),
            MenuItem("hawks-4", "hawks", "Macaroni Salad", "Classic deli-style side", 3.79, "Sides"),
            MenuItem("hawks-5", "hawks", "Kettle Chips", "Sea salt kettle chips", 2.29, "Sides"),
            MenuItem("hawks-6", "hawks", "Pastrami Reuben", "Pastrami, sauerkraut, rye", 10.99, "Popular"),
            MenuItem("hawks-7", "hawks", "Iced Tea", "Fresh brewed black tea", 2.49, "Drinks"),
            MenuItem("hawks-8", "hawks", "Lemonade", "House lemonade", 2.79, "Drinks")
        ),
        "grill" to listOf(
            MenuItem("grill-1", "grill", "Campus Smash Burger", "Double patty, cheddar, pickles", 11.49, "Popular"),
            MenuItem("grill-2", "grill", "Chicken Tenders Basket", "Crispy tenders with dipping sauce", 9.99, "Mains"),
            MenuItem("grill-3", "grill", "BBQ Bacon Burger", "BBQ sauce, bacon, onion rings", 12.29, "Mains"),
            MenuItem("grill-4", "grill", "Loaded Fries", "Cheese sauce, jalapenos, scallions", 5.49, "Sides"),
            MenuItem("grill-5", "grill", "Onion Rings", "Beer-battered and crispy", 4.99, "Sides"),
            MenuItem("grill-6", "grill", "Grilled Chicken Sandwich", "Herb chicken, lettuce, aioli", 9.49, "Popular"),
            MenuItem("grill-7", "grill", "Fountain Cola", "Chilled soft drink", 2.29, "Drinks"),
            MenuItem("grill-8", "grill", "Vanilla Milkshake", "Creamy hand-spun shake", 4.99, "Drinks")
        ),
        "green" to listOf(
            MenuItem("green-1", "green", "Protein Power Bowl", "Quinoa, chicken, avocado, kale", 11.99, "Popular"),
            MenuItem("green-2", "green", "Mediterranean Salad", "Feta, cucumber, olives, greens", 9.49, "Mains"),
            MenuItem("green-3", "green", "Tofu Teriyaki Bowl", "Tofu, brown rice, broccoli", 10.79, "Mains"),
            MenuItem("green-4", "green", "Hummus & Veggies", "Hummus with carrot and cucumber sticks", 4.49, "Sides"),
            MenuItem("green-5", "green", "Edamame Cup", "Steamed edamame with sea salt", 3.99, "Sides"),
            MenuItem("green-6", "green", "Southwest Chicken Salad", "Chicken, corn, beans, chipotle dressing", 10.99, "Popular"),
            MenuItem("green-7", "green", "Green Smoothie", "Spinach, banana, mango", 5.49, "Drinks"),
            MenuItem("green-8", "green", "Infused Water", "Cucumber mint water", 2.19, "Drinks")
        ),
        "brew" to listOf(
            MenuItem("brew-1", "brew", "Cold Brew Latte", "Cold brew with milk and ice", 4.99, "Popular"),
            MenuItem("brew-2", "brew", "Breakfast Croissant", "Egg, cheese, and turkey bacon", 7.49, "Mains"),
            MenuItem("brew-3", "brew", "Avocado Toast", "Sourdough, smashed avocado, chili flakes", 8.29, "Mains"),
            MenuItem("brew-4", "brew", "Blueberry Muffin", "Fresh-baked daily muffin", 3.49, "Sides"),
            MenuItem("brew-5", "brew", "Chocolate Chip Cookie", "Soft baked cookie", 2.79, "Sides"),
            MenuItem("brew-6", "brew", "Cappuccino", "Espresso with steamed foam", 4.59, "Popular"),
            MenuItem("brew-7", "brew", "Chai Tea Latte", "Spiced tea with steamed milk", 4.29, "Drinks"),
            MenuItem("brew-8", "brew", "Orange Juice", "100 percent orange juice", 3.29, "Drinks")
        )
    )

    val menuItems: List<MenuItem> = vendorMenus.values.flatten()

    fun getVendor(vendorId: String): Vendor? = vendors.find { it.id == vendorId }

    fun getMenuForVendor(vendorId: String): List<MenuItem> = vendorMenus[vendorId].orEmpty()
}
