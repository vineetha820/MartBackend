from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
# Create your views here.


class RegistrationView(APIView):
    def post(self,request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email and password are required.'}, status=400)
        if len(password) < 8:
            return Response({'error': 'Password must be at least 8 characters long.'}, status=400)
        existing_user=User.objects.filter(email=email).first()
        if existing_user:
            return Response({'error': 'Email already exists.'}, status=400)
        user=User.objects.create(email=email,password=make_password(password))
        refresh = RefreshToken.for_user(user)
       
        return Response({'message': 'User created successfully.', 'refresh': str(refresh), 'access': str(refresh.access_token)}, status=201)

class LoginView(APIView):
    def post(self,request):
        email=request.data.get('email')
        password=request.data.get('password')
        if not email or not password:
            return Response({'error': 'Email and password are required.'}, status=400)  

        try:
            user=User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Invalid email or password.'}, status=400)

        if not user.check_password(password):
            return Response({'error': 'Invalid email or password.'}, status=400)

        return Response({'message': 'Login successful.'}, status=200)