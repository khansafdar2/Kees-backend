
from rest_framework import exceptions
from rest_framework.generics import ListCreateAPIView
from authentication.BusinessLogic.ActivityStream import SystemLogs
from ecomm_app.pagination import StandardResultSetPagination
from order.models import ChildOrder
from vendor.Serializers.VendorOrderSerializer import VendorOrderListSerializer


class VendorOrderListView(ListCreateAPIView):
    serializer_class = VendorOrderListSerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        try:
            search = self.request.GET.get('search', None)
            column = self.request.GET.get('column', None)
            fulfilment_status = self.request.GET.get('fulfillment_status', None)
            payment_status = self.request.GET.get('payment_status', None)
            refund_status = self.request.GET.get('refund_status', None)

            vendor_id = self.request.user.vendor.id

            queryset = ChildOrder.objects.filter(vendor_id=vendor_id)

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
            action_performed = self.request.user.username + " get list of Vendor orders"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            return queryset
        except Exception as e:
            print(e)
            raise exceptions.ParseError(str(e))
