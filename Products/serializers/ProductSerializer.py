from rest_framework import serializers
from Products.models import Product

class ProductSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True, default=None)

    class Meta:
        model=Product
        fields=('id','name','description','price','image','created_by','created_by_username','in_stock')
        read_only_fields = ('created_by',)

    def validate_price(self,value):
        if value<0:
            raise serializers.ValidationError("Price must be a positive number.")
        return value
