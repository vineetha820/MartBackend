from django.conf import settings
from django.db import models

# Create your models here.
class Product(models.Model):
    name=models.CharField(max_length=100)
    price=models.DecimalField(max_digits=10, decimal_places=2)
    description=models.TextField()
    image=models.ImageField(upload_to='product_images/', null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_products',
        editable=False,
    )
    created_at=models.DateTimeField(auto_now_add=True)
    seller = models.ForeignKey(
        'users.Seller', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='products', editable=False,
    )
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
