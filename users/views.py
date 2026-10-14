from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from Products.permissions import can_manage_products


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)
    account_type = serializers.ChoiceField(choices=('customer',), default='customer')
    shop_name = serializers.CharField(max_length=150, required=False)

    def validate(self, attrs):
        if attrs.get('shop_name'):
            raise serializers.ValidationError({'shop_name': 'Seller registration is not available.'})
        User = get_user_model()
        attrs['email'] = User.objects.normalize_email(attrs['email'])
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({'email': 'Email already exists.'})
        try:
            validate_password(attrs['password'], User(email=attrs['email']))
        except ValidationError as exc:
            raise serializers.ValidationError({'password': exc.messages})
        return attrs


class RegistrationView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)
        account_type = data.pop('account_type')
        data.pop('shop_name', None)
        try:
            with transaction.atomic():
                get_user_model().objects.create_user(**data)
        except IntegrityError:
            return Response({'error': 'Email already exists.'}, status=400)
        return Response({'message': 'User registered successfully.', 'account_type': account_type}, status=201)


class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        if not isinstance(email, str) or not isinstance(password, str) or not email or not password:
            return Response({'error': 'Email and password are required.'}, status=400)
        user = authenticate(request=request, email=get_user_model().objects.normalize_email(email), password=password)
        if user is None:
            return Response({'error': 'Invalid email or password.'}, status=400)
        refresh = RefreshToken.for_user(user)
        product_admin = can_manage_products(user)
        return Response({
            'message': 'Login successful.', 'refresh': str(refresh), 'access': str(refresh.access_token),
            'user': {'id': user.pk, 'email': user.email, 'is_staff': user.is_staff,
                     'account_type': 'admin' if product_admin else 'customer',
                     'can_manage_products': product_admin},
        })
