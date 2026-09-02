from .models import Product
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers.ProductSerializer import ProductSerializer


class ProductListView(APIView):
    def get(self,request):
        products=Product.objects.all()
        products_data=[]
        for product in products:
            products_data.append({
                'id':product.id,
                'name':product.name,
                'description':product.description,
                'price':product.price,
                'image_url':request.build_absolute_uri(product.image.url) if product.image else None
            })
        return Response(products_data)
class ProductCreateView(APIView):
    def post(self,request):
        serializer=ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'Product created successfully.'},status=201)
        return Response(serializer.errors,status=400)

class ProductDetailView(APIView):
    def get(self,request,pk):
        try:
            product=Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({'error':'Product not found.'},status=404)
        serializer=ProductSerializer(product)
        return Response(serializer.data)
class ProductUpdateView(APIView):
    def put(self,request,pk):
        try:
            product=Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({'error':'Product not found.'},status=404)
        serializer=ProductSerializer(product,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'Product updated successfully.'})
        return Response(serializer.errors,status=400)
class ProductDeleteView(APIView):
    def delete(self,request,pk):
        try:
            product=Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({'error':'Product not found.'},status=404)
        product.delete()
        return Response({'message':'Product deleted successfully.'})





