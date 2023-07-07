
import json
import datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from rest_framework import exceptions

from crm.models import Wallet, WalletHistory
from order.models import Checkout, LineItems, Order, DraftOrder, OrderHistory
from order.Serializers.ParentOrderSerializer import ParentOrderListSerializer, ParentOrderDetailSerializer, \
    ParentOrderUpdateSerializer, OrderStatusChangeSerializer, OrderHistorySerializer
from drf_yasg.utils import swagger_auto_schema
from ecomm_app.pagination import StandardResultSetPagination
from authentication.BusinessLogic.ActivityStream import SystemLogs
from authentication.BusinessLogic.ApiPermissions import AccessApi


class ParenttOrderListView(ListCreateAPIView):
    serializer_class = ParentOrderListSerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        try:
            access = AccessApi(self.request.user, "orders")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

            search = self.request.GET.get('search', None)
            column = self.request.GET.get('column', None)
            fulfilment_status = self.request.GET.get('fulfillment_status', None)
            payment_status = self.request.GET.get('payment_status', None)
            refund_status = self.request.GET.get('refund_status', None)

            queryset = Order.objects.all()
            if column is not None:
                if column == "name":
                    queryset = queryset.filter(name__icontains=search)
                if column == "order_id":
                    queryset = queryset.filter(order_id__icontains=search)

            if fulfilment_status is not None:
                if fulfilment_status.lower() == 'fulfilled':
                    queryset = queryset.filter(fulfillment_status='Fulfilled')
                elif fulfilment_status.lower() == 'partially_fulfilled':
                    queryset = queryset.filter(fulfillment_status='Partially Fulfilled')
                elif fulfilment_status.lower() == 'unfulfilled':
                    queryset = queryset.filter(fulfillment_status='Unfulfilled')
                else:
                    raise exceptions.ParseError("Invalid fulfilment status filter")

            if payment_status is not None:
                if payment_status.lower() == 'paid':
                    queryset = queryset.filter(payment_status='Paid')
                elif payment_status.lower() == 'partially_paid':
                    queryset = queryset.filter(payment_status='Partially Paid')
                elif payment_status.lower() == 'pending':
                    queryset = queryset.filter(payment_status='Pending')
                else:
                    raise exceptions.ParseError("Invalid payment status filter")

            if refund_status is not None:
                if refund_status.lower() == 'wallet':
                    queryset = queryset.filter(refund_type='Wallet')
                elif refund_status.lower() == 'bank':
                    queryset = queryset.filter(refund_type='Bank')
                else:
                    raise exceptions.ParseError("Invalid refund status filter")

            # Post Entry in Logs
            action_performed = self.request.user.username + " get list of Parent orders"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            return queryset
        except Exception as e:
            print(e)
            raise exceptions.ParseError(str(e))


class ParentOrderView(APIView):
    @swagger_auto_schema(responses={200: ParentOrderUpdateSerializer}, request_body=ParentOrderUpdateSerializer)
    def put(self, request):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "orders")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to access this Api")

            request_data = request.data
            order = Order.objects.filter(id=request_data['id']).first()
            serializer = ParentOrderUpdateSerializer(order, data=request_data)
            if serializer.is_valid():
                serializer.save()

                return Response(serializer.data, status=200)
            else:
                return Response(serializer.errors, status=422)

        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)


class ParentOrderDetailView(APIView):
    @swagger_auto_schema(responses={200: ParentOrderDetailSerializer}, request_body=ParentOrderDetailSerializer)
    def get(self, request, pk):
        try:
            access = AccessApi(self.request.user, "orders")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

            order = Order.objects.filter(id=pk).first()
            if not order:
                data = {}
                return Response(data, status=200)
            
            serializer = ParentOrderDetailSerializer(order)

            # Post Entry in Logs
            action_performed = self.request.user.username + " get single order detail"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            return Response(serializer.data, status=200)

        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=422)


class ParentOrderStatusChange(APIView):
    @swagger_auto_schema(responses={200: OrderStatusChangeSerializer}, request_body=OrderStatusChangeSerializer)
    def put(self, request):
        try:
            access = AccessApi(self.request.user, "orders")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

            request_data = request.data
            order = Order.objects.filter(id=request_data['id']).first()
            serializer = OrderStatusChangeSerializer(order, data=request_data)
            if serializer.is_valid():
                serializer.save()

                return Response(serializer.data, status=200)
            else:
                return Response(serializer.errors, status=422)

        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)


class OrderHistoryView(APIView):
    def get(self, request):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "orders")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to access this Api")

            order_id = request.GET.get('order_id', None)
            childorder_id = request.GET.get('childorder_id', None)

            if order_id is not None:
                queryset = OrderHistory.objects.filter(order_id=order_id)
            elif childorder_id is not None:
                queryset = OrderHistory.objects.filter(child_order_id=childorder_id)
            else:
                queryset = None

            serializer = OrderHistorySerializer(queryset, many=True)
            return Response(serializer.data, status=200)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)

    def post(self, request):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "orders")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to access this Api")

            request_data = request.data
            serializer = OrderHistorySerializer(data=request_data)
            if serializer.is_valid():
                serializer.save()

                return Response(serializer.data, status=200)
            else:
                return Response(serializer.errors, status=422)

        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)


class LoyaltyPointCalculation(APIView):
    def post(self, request):
        requested_data = request.data.dict()
        start_date = requested_data["start_date"][:16]
        end_date = requested_data["end_date"][:16]
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M')
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M')

        orders = Order.objects.filter(created_at__range=[start_date, end_date],
                                      customer_id=requested_data["customer_id"])
        total_orders = orders.count()
        total_price = 0.00
        for order in orders:
            total_price += float(order.total_price)

        response = {
            "total_orders": total_orders,
            "total_price": total_price
        }
        return Response(response, status=200)


class RefundOrderView(APIView):
    def get(self, request, pk):
        try:
            access = AccessApi(self.request.user, "orders")
            if not access:
                raise exceptions.ParseError("This user does not have permission to access this Api")

            order_id = pk

            if order_id is not None:
                order = Order.objects.filter(id=order_id).first()
                if order.total_price < order.paid_amount:
                    return_amount = float(order.paid_amount) - float(order.total_price)
                    order.paid_amount = float(order.paid_amount) - return_amount
                    order.save()

                    wallet = Wallet.objects.filter(customer=order.customer, is_active=True).first()
                    wallet.value = float(wallet.value) + return_amount
                    wallet.save()

                    # entry in wallet history
                    WalletHistory.objects.create(wallet=wallet,
                                                 type=f'Refund on order {order.name}', action='Credited',
                                                 value=return_amount)

                    return Response({'detail': f'{return_amount} amount is refunded in customer wallet'}, status=200)

            return Response({'detail': 'no refunded amount calculated'}, status=200)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)