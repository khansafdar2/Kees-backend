
from rest_framework.response import Response
from rest_framework import exceptions
from rest_framework.views import APIView
from order.models import Checkout, LineItems, Order
from storefront.BussinessLogic.CheckDomain import check_domain
from order.Serializers.CheckoutOrderSerializer import CheckoutOrderAddSerializer, CustomerAccountOrderDetailSerializer
from drf_yasg.utils import swagger_auto_schema


class OrderView(APIView):
    @swagger_auto_schema(responses={200: CheckoutOrderAddSerializer}, request_body=CheckoutOrderAddSerializer)
    def post(self, request):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            request_data = request.data
            serializer = CheckoutOrderAddSerializer(data=request_data)
            if serializer.is_valid():
                serializer.save()

                return Response(serializer.data, status=200)
            else:
                return Response(serializer.errors, status=422)

        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)


class OrderDetailView(APIView):
    @swagger_auto_schema(responses={200: CustomerAccountOrderDetailSerializer}, request_body=CustomerAccountOrderDetailSerializer)
    def get(self, request):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        order_id = request.GET.get('order_id', None)
        try:
            try:
                order = Order.objects.get(order_id=order_id)
            except Exception as e:
                print(e)
                return Response({"detail": "Invalid Order ID"}, status=404)

            serializer = CustomerAccountOrderDetailSerializer(order)
            return Response(serializer.data, status=200)

        except Exception as e:
            return Response({"detail": str(e)}, status=400)
