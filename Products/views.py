from .models import Product
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers.ProductSerializer import ProductSerializer
from rest_framework import viewsets

# class ProductListView(APIView):
#     def get(self,request):
#         products=Product.objects.all()
#         serializer=ProductSerializer(products, many=True)
#         return Response(serializer.data)
# class ProductCreateView(APIView):
#     def post(self,request):
#         serializer=ProductSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({'message':'Product created successfully.'},status=201)
#         return Response(serializer.errors,status=400)

# class ProductDetailView(APIView):
#     def get(self,request,pk):
#         try:
#             product=Product.objects.get(pk=pk)
#         except Product.DoesNotExist:
#             return Response({'error':'Product not found.'},status=404)
#         serializer=ProductSerializer(product)
#         return Response(serializer.data)
# class ProductUpdateView(APIView):
#     def put(self,request,pk):
#         try:
#             product=Product.objects.get(pk=pk)
#         except Product.DoesNotExist:
#             return Response({'error':'Product not found.'},status=404)
#         serializer=ProductSerializer(product,data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({'message':'Product updated successfully.'})
#         return Response(serializer.errors,status=400)
# class ProductDeleteView(APIView):
    # def delete(self,request,pk):
    #     try:
    #         product=Product.objects.get(pk=pk)
    #     except Product.DoesNotExist:
    #         return Response({'error':'Product not found.'},status=404)
    #     product.delete()
    #     return Response({'message':'Product deleted successfully.'})
class productViewSet(viewsets.ModelViewSet):
    queryset=Product.objects.all()
    serializer_class=ProductSerializer
