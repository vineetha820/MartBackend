from rest_framework import serializers
from Products.models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields=('id','name','description','price','image')

    def validate_price(self,value):
        if value<0:
            raise serializers.ValidationError("Price must be a positive number.")
        return value