import os
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "martBackend.settings")

import django

django.setup()

from django.db import transaction

from Products.models import Product
from orders.models import Order, OrderItem
from users.models import User


PRODUCTS = [
    {
        "name": "Modern Double Sofa",
        "price": Decimal("499.00"),
        "description": "Comfortable three-seater fabric sofa for living rooms.",
        "image": "product_images/default.jpg",
    },
    {
        "name": "Classic Arm Chair",
        "price": Decimal("179.00"),
        "description": "Soft cushioned arm chair with a sturdy wooden frame.",
        "image": "product_images/default.jpg",
    },
    {
        "name": "Wooden Coffee Table",
        "price": Decimal("129.00"),
        "description": "Compact coffee table with a smooth walnut finish.",
        "image": "product_images/default.jpg",
    },
    {
        "name": "Smart Fitness Watch",
        "price": Decimal("89.99"),
        "description": "Water-resistant watch with heart-rate and activity tracking.",
        "image": "product_images/default.jpg",
    },
    {
        "name": "Wireless Bluetooth Earbuds",
        "price": Decimal("59.99"),
        "description": "Noise-isolating earbuds with charging case and long battery life.",
        "image": "product_images/default.jpg",
    },
    {
        "name": "Android Smartphone 128GB",
        "price": Decimal("699.00"),
        "description": "Sleek smartphone with 128GB storage and a high-resolution display.",
        "image": "product_images/default.jpg",
    },
    {
        "name": "Dining Chair Set",
        "price": Decimal("249.00"),
        "description": "Set of four padded dining chairs for everyday use.",
        "image": "product_images/default.jpg",
    },
    {
        "name": "Office Desk Lamp",
        "price": Decimal("39.99"),
        "description": "Adjustable LED desk lamp with three brightness levels.",
        "image": "product_images/default.jpg",
    },
    {
        "name": "Portable Speaker",
        "price": Decimal("74.99"),
        "description": "Compact wireless speaker with rich bass and USB-C charging.",
        "image": "product_images/default.jpg",
    },
    {
        "name": "Single Sofa Chair",
        "price": Decimal("219.00"),
        "description": "Cozy single-seat sofa chair for reading corners and lounges.",
        "image": "product_images/default.jpg",
    },
]

ORDER_SPECS = [
    {
        "recipient_name": "Vineetha",
        "phone": "9876543210",
        "shipping_address": "12 Market Street, Hyderabad",
        "status": "pending",
        "items": [("Modern Double Sofa", 1), ("Wooden Coffee Table", 1)],
    },
    {
        "recipient_name": "Vineetha",
        "phone": "9876543210",
        "shipping_address": "12 Market Street, Hyderabad",
        "status": "confirmed",
        "items": [
            ("Smart Fitness Watch", 2),
            ("Wireless Bluetooth Earbuds", 1),
            ("Portable Speaker", 1),
        ],
    },
    {
        "recipient_name": "Vineetha",
        "phone": "9876543210",
        "shipping_address": "12 Market Street, Hyderabad",
        "status": "shipped",
        "items": [("Android Smartphone 128GB", 1), ("Office Desk Lamp", 2)],
    },
]


def seed_products():
    products_added = 0

    for data in PRODUCTS:
        _, created = Product.objects.get_or_create(name=data["name"], defaults=data)
        if created:
            products_added += 1

    return products_added


def seed_orders():
    user = User.objects.first()
    if user is None:
        user = User.objects.create_user(email="customer@example.com", password=None)

    product_by_name = {
        product.name: product
        for product in Product.objects.filter(
            name__in=[product_data["name"] for product_data in PRODUCTS]
        )
    }

    orders_created = 0
    order_items_created = 0

    for spec in ORDER_SPECS:
        Order.objects.filter(
            user=user,
            recipient_name=spec["recipient_name"],
            shipping_address=spec["shipping_address"],
            status=spec["status"],
            items__isnull=True,
        ).delete()

    for spec in ORDER_SPECS:
        first_product_name = spec["items"][0][0]
        already_exists = Order.objects.filter(
            user=user,
            recipient_name=spec["recipient_name"],
            shipping_address=spec["shipping_address"],
            status=spec["status"],
            items__product_name=first_product_name,
        ).exists()

        if already_exists:
            continue

        order_items = [
            (product_by_name[product_name], quantity)
            for product_name, quantity in spec["items"]
        ]
        total_amount = sum(
            (product.price * quantity for product, quantity in order_items),
            Decimal("0.00"),
        )

        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                recipient_name=spec["recipient_name"],
                phone=spec["phone"],
                shipping_address=spec["shipping_address"],
                status=spec["status"],
                total_amount=total_amount,
            )
            orders_created += 1

            for product, quantity in order_items:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    quantity=quantity,
                    unit_price=product.price,
                    subtotal=product.price * quantity,
                )
                order_items_created += 1

    return orders_created, order_items_created


if __name__ == "__main__":
    products_added = seed_products()
    orders_created, order_items_created = seed_orders()

    print(f"products_added={products_added}")
    print(f"products_total={Product.objects.count()}")
    print(f"orders_created={orders_created}")
    print(f"order_items_created={order_items_created}")
    print(f"orders_total={Order.objects.count()}")
