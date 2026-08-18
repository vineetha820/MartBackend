from django.db import models

class User(models.Model):
    email=models.EmailField(unique=True)
    password=models.CharField(max_length=16)
    created_at=models.DateTimeField(auto_now_add=True)
    

class Userprofile(models.Model):
    username=models.CharField(max_length=20)
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    address=models.CharField(max_length=100)
    image=models.ImageField(upload_to='profile_images/', null=True, blank=True)
    phone=models.CharField(max_length=10)