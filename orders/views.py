from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Order
from .serializers.OrderSerializer import OrderCreateSerializer, OrderSerializer

# class OrdercreateView(APIView):
#     def post(self,request):
#         user=request.user
#         serializer=OrderCreateSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(user=user)
#             return Response({'message':'Order created successfully.'},status=201)   
#         return Response({'message':'Invalid data provided.'},status=400)

# class OrderListView(APIView):
#     def get(self,request):
#         user=request.user
#         orders=Order.objects.filter(user=user)
#         serializer=OrderSerializer(orders,many=True)
#         return Response(serializer.data,status=200)

class OrdercreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OrderSerializer
        return OrderCreateSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
