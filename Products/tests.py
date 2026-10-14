from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from users.models import Seller
from .models import Product


class ProductAdminTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_superuser(email='owner@example.com', password='Test-password-123!')
        self.other_admin = User.objects.create_superuser(email='other@example.com', password='Test-password-123!')
        self.customer = User.objects.create_user(email='customer@example.com')
        self.seller = User.objects.create_user(email='seller@example.com')
        Seller.objects.create(user=self.seller, shop_name='Old shop')
        self.staff = User.objects.create_user(email='staff@example.com', is_staff=True)
        self.setting = self.settings(PRODUCT_ADMIN_USER_ID=self.admin.pk)
        self.setting.enable()
        self.addCleanup(self.setting.disable)
        self.client = APIClient()
        self.payload = {'name': 'Apple', 'price': '10.00', 'description': 'Fresh'}

    def test_designated_admin_can_create_edit_and_delete(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/products/products/', {**self.payload, 'created_by': self.other_admin.pk})
        self.assertEqual(response.status_code, 201)
        product_id = response.data['id']
        self.assertEqual(response.data['created_by'], self.admin.pk)
        response = self.client.patch(f'/products/products/{product_id}/', {'name': 'Green apple', 'created_by': self.other_admin.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['created_by'], self.admin.pk)
        self.assertEqual(self.client.delete(f'/products/products/{product_id}/').status_code, 204)

    def test_every_other_account_is_denied_product_writes(self):
        product = Product.objects.create(**self.payload)
        for user in (None, self.customer, self.seller, self.staff, self.other_admin):
            self.client.force_authenticate(user=user)
            for method, url in (
                ('post', '/products/products/'),
                ('put', f'/products/products/{product.pk}/'),
                ('patch', f'/products/products/{product.pk}/'),
                ('delete', f'/products/products/{product.pk}/'),
            ):
                with self.subTest(user=user, method=method):
                    response = getattr(self.client, method)(url, self.payload)
                    self.assertIn(response.status_code, (401, 403))
            self.assertEqual(self.client.get('/products/products/').status_code, 200)
        self.assertEqual(Product.objects.count(), 1)

    def test_django_admin_enforces_same_single_admin_rule(self):
        product = Product.objects.create(**self.payload)
        self.client.force_login(self.other_admin)
        self.assertEqual(self.client.get('/admin/Products/product/add/').status_code, 403)
        self.assertEqual(self.client.post(f'/admin/Products/product/{product.pk}/change/', self.payload).status_code, 403)
        self.assertEqual(self.client.post(f'/admin/Products/product/{product.pk}/delete/', {'post': 'yes'}).status_code, 403)
        self.client.force_login(self.admin)
        response = self.client.post('/admin/Products/product/add/', self.payload)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Product.objects.latest('id').created_by, self.admin)

    def test_inactive_designated_admin_cannot_write(self):
        self.admin.is_active = False
        self.admin.save()
        self.client.force_authenticate(user=self.admin)
        self.assertEqual(self.client.post('/products/products/', self.payload).status_code, 403)

    def test_deleted_author_does_not_delete_product(self):
        product = Product.objects.create(**self.payload, created_by=self.admin)
        self.admin.delete()
        product.refresh_from_db()
        self.assertIsNone(product.created_by)
