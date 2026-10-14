from django.contrib.auth import authenticate, get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.test import APIRequestFactory
from .admin import CustomUserCreationForm
from .models import Seller


class UnifiedUserTests(TestCase):
    password = 'Test-Password-7mX!2026'

    def test_public_registration_rejects_seller_and_admin_roles(self):
        client = APIClient()
        for role in ('seller', 'admin'):
            response = client.post('/users/register/', {
                'email': 'new@example.com', 'password': self.password,
                'account_type': role, 'shop_name': 'Shop',
            })
            self.assertEqual(response.status_code, 400)
        self.assertFalse(get_user_model().objects.filter(email='new@example.com').exists())
        self.assertFalse(Seller.objects.exists())

    def test_login_exposes_product_permission_for_frontend(self):
        User = get_user_model()
        admin = User.objects.create_superuser(email='owner@example.com', password=self.password)
        other = User.objects.create_superuser(email='other@example.com', password=self.password)
        with self.settings(PRODUCT_ADMIN_USER_ID=admin.pk):
            client = APIClient()
            for user, expected in ((admin, True), (other, False)):
                response = client.post('/users/login/', {'email': user.email, 'password': self.password})
                self.assertEqual(response.data['user']['can_manage_products'], expected)
                client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
                response = client.post('/products/products/', {'name': 'Apple', 'price': '10.00', 'description': 'Fresh'})
                self.assertEqual(response.status_code, 201 if expected else 403)

    def test_registration_login_and_jwt_use_custom_user(self):
        client = APIClient()
        response = client.post('/users/register/', {'email': 'customer@example.com', 'password': self.password, 'is_staff': True, 'is_superuser': True})
        self.assertEqual(response.status_code, 201)
        user = get_user_model().objects.get(email='customer@example.com')
        self.assertTrue(user.check_password(self.password))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        response = client.post('/users/login/', {'email': user.email, 'password': self.password})
        self.assertEqual(response.status_code, 200)
        request = APIRequestFactory().get('/', HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
        authenticated, token = JWTAuthentication().authenticate(request)
        self.assertEqual(authenticated, user)
        self.assertEqual(client.post('/users/refresh-token/', {'refresh': response.data['refresh']}).status_code, 200)
        self.assertTrue(self.client.login(email=user.email, password=self.password))
        self.assertEqual(self.client.get('/admin/').status_code, 302)

    def test_superuser_uses_email_and_can_manage_products(self):
        user = get_user_model().objects.create_superuser(email='admin@example.com', password=self.password)
        self.assertEqual(authenticate(email=user.email, password=self.password), user)
        self.assertTrue(self.client.login(email=user.email, password=self.password))
        self.assertEqual(self.client.get('/admin/Products/product/').status_code, 200)
        self.assertEqual(self.client.get('/admin/users/user/add/').status_code, 200)
        self.assertEqual(self.client.get(f'/admin/users/user/{user.pk}/change/').status_code, 200)

    def test_inactive_user_cannot_login(self):
        user = get_user_model().objects.create_user(email='inactive@example.com', password=self.password, is_active=False)
        self.assertIsNone(authenticate(email=user.email, password=self.password))
        response = APIClient().post('/users/login/', {'email': user.email, 'password': self.password})
        self.assertEqual(response.status_code, 400)

    def test_registration_rejects_invalid_and_duplicate_email(self):
        client = APIClient()
        self.assertEqual(client.post('/users/register/', {'email': 'bad', 'password': self.password}).status_code, 400)
        get_user_model().objects.create_user(email='exists@example.com', password=self.password)
        self.assertEqual(client.post('/users/register/', {'email': 'exists@example.com', 'password': self.password}).status_code, 400)

    def test_admin_creation_form_hashes_password(self):
        form = CustomUserCreationForm(data={'email': 'new@example.com', 'password1': self.password, 'password2': self.password})
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertTrue(user.check_password(self.password))
