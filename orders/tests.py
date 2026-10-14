from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from Products.models import Product
from users.models import Seller
from .models import Order
from decimal import Decimal


class CustomerOrderTests(TestCase):
    def test_customer_orders_seller_product_and_sees_only_own_orders(self):
        User = get_user_model()
        customer = User.objects.create_user(email='buyer@example.com')
        other = User.objects.create_user(email='other@example.com')
        seller = Seller.objects.create(user=User.objects.create_user(email='seller@example.com'), shop_name='Shop')
        product = Product.objects.create(name='Apple', price='12.50', seller=seller, created_by=seller.user)
        payload = {
            'recipient_name': 'Buyer', 'phone': '1234567890', 'shipping_address': 'Test address',
            'items': [{'product': product.pk, 'quantity': 2}],
            'user': other.pk, 'total_amount': '0.01',
        }
        client = APIClient()
        self.assertEqual(client.post('/orders/', payload, format='json').status_code, 401)
        client.force_authenticate(user=customer)
        response = client.post('/orders/', payload, format='json')
        self.assertEqual(response.status_code, 201)
        order = Order.objects.get(pk=response.data['id'])
        self.assertEqual(order.user, customer)
        self.assertEqual(order.total_amount, Decimal('25.00'))
        self.assertEqual(order.items.get().subtotal, Decimal('25.00'))
        self.assertEqual(len(client.get('/orders/').data), 1)
        client.force_authenticate(user=other)
        self.assertEqual(client.get('/orders/').data, [])

    def test_invalid_order_creates_no_order(self):
        client = APIClient()
        client.force_authenticate(user=get_user_model().objects.create_user(email='buyer@example.com'))
        response = client.post('/orders/', {
            'recipient_name': 'Buyer', 'phone': '1234567890', 'shipping_address': 'Test address',
            'items': [],
        }, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Order.objects.exists())
