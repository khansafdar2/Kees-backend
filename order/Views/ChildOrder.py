
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime

from crm.models import Wallet, WalletHistory
from order.models import LineItems, Order, ChildOrder, ChildOrderLineItems
from order.Serializers.ChildOrderSerializer import ChildOrderDetailSerializer, ChildOrderUpdateSerializer, \
    ChildOrderAddSerializer, ChildOrderStatusChangeSerializer
from drf_yasg.utils import swagger_auto_schema
from authentication.BusinessLogic.ActivityStream import SystemLogs
from authentication.BusinessLogic.ApiPermissions import AccessApi
from rest_framework import exceptions


class ChildOrderView(APIView):
    def post(self, request):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "orders")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to access this Api")

            serializer = ChildOrderAddSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

            # Post Entry in Logs
            action_performed = self.request.user.username + " Create child order"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            return Response(serializer.data, status=200)

        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=422)

    @swagger_auto_schema(responses={200: ChildOrderUpdateSerializer}, request_body=ChildOrderUpdateSerializer)
    def put(self, request):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "orders")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to access this Api")

            child_order = ChildOrder.objects.filter(id=request.data['id']).first()
            serializer = ChildOrderUpdateSerializer(child_order, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

            # Post Entry in Logs
            action_performed = self.request.user.username + " get single child order update"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            return Response(serializer.data, status=200)

        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=422)


class ChildOrderDetailView(APIView):
    @swagger_auto_schema(responses={200: ChildOrderDetailSerializer}, request_body=ChildOrderDetailSerializer)
    def get(self, request, pk):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "orders")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to this Api")

            order = ChildOrder.objects.filter(id=pk).first()
            if not order:
                data = {}
                return Response(data, status=200)

            serializer = ChildOrderDetailSerializer(order)

            # Post Entry in Logs
            action_performed = self.request.user.username + " get single child order detail"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            return Response(serializer.data, status=200)

        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=422)


class ChildOrderListItemView(APIView):
    def delete(self, request, pk):
        try:
            access = AccessApi(self.request.user, "orders")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

            if pk is None:
                return Response('id is missing', status=404)

            child_line_item = ChildOrderLineItems.objects.filter(id=pk, deleted=False).first()
            if child_line_item:
                child_line_item.deleted = True
                child_line_item.deleted_at = datetime.now()
                child_line_item.save()

                child_order = ChildOrder.objects.filter(child_order_lineitem_order=child_line_item).first()
                if child_order:
                    child_order.subtotal_price -= child_line_item.total_price
                    child_order.total_shipping -= child_line_item.shipping_amount
                    child_order.total_price = child_order.total_price - (child_line_item.total_price + child_line_item.shipping_amount)
                    child_order.save()

                    order = Order.objects.filter(childOrders_order=child_order).first()
                    if order:
                        order.subtotal_price -= child_line_item.total_price
                        order.total_shipping -= child_line_item.shipping_amount
                        order.total_price -= (child_line_item.total_price + child_line_item.shipping_amount)
                        order.save()

                        LineItems.objects.filter(order=order, variant=child_line_item.variant, deleted=False).update(deleted=True, deleted_at=datetime.now())

            # Post Entry in Logs
            action_performed = self.request.user.username + " delete line item" + str(pk)
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            return Response({'Lineitem deleted successfully'}, status=200)

        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=422)


class ChildOrderStatusChange(APIView):
    def put(self, request):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "orders")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to this Api")

            request_data = request.data
            order = ChildOrder.objects.filter(id=request_data['id']).first()
            serializer = ChildOrderStatusChangeSerializer(order, data=request_data)
            if serializer.is_valid():
                serializer.save()

                return Response(serializer.data, status=200)
            else:
                return Response(serializer.errors, status=422)

        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)


class RefundChildOrderView(APIView):
    def get(self, request, pk):
        try:
            child_order_id = pk
            if child_order_id is not None:
                child_order = ChildOrder.objects.filter(id=child_order_id).first()
                if child_order.total_price < child_order.paid_amount:
                    return_amount = float(child_order.paid_amount) - float(child_order.total_price)
                    child_order.paid_amount = float(child_order.paid_amount) - return_amount
                    child_order.save()

                    wallet = Wallet.objects.filter(customer=child_order.order.customer, is_active=True).first()
                    wallet.value = float(wallet.value) + return_amount
                    wallet.save()

                    # entry in wallet history
                    WalletHistory.objects.create(wallet=wallet,
                                                 type=f'Refund on order {child_order.name}', action='Credited',
                                                 value=return_amount)

                    return Response({'detail': f'{return_amount} amount is refunded in customer wallet'}, status=200)

            return Response({'detail': 'no refunded amount calculated'}, status=200)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)