
from rest_framework.generics import ListCreateAPIView
from crm.models import Customer
from ecomm_app.pagination import StandardResultSetPagination
from order.models import Order
from products.models import Product
from storefront.Serializers.ExposedApiSerializer import ProductListSerializer, ParentOrderListSerializer, \
    CustomerListSerializer
from authentication.BusinessLogic.ActivityStream import SystemLogs
from rest_framework import exceptions


class ProductListView(ListCreateAPIView):
    serializer_class = ProductListSerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        try:
            vendor = self.request.GET.get('vendor', None)
            collection = self.request.GET.get('collection', None)
            column = self.request.GET.get('column', None)
            search = self.request.GET.get('search', None)
            status = self.request.GET.get('status', None)
            approval_status = self.request.GET.get('approval_status', None)

            if vendor is None:
                queryset = Product.objects.filter(deleted=False)
            else:
                queryset = Product.objects.filter(deleted=False, vendor_id=vendor)

            if collection is not None:
                if collection != "":
                    queryset = queryset.filter(collection=collection)

            if column is not None:
                if column == "title":
                    queryset = queryset.filter(title__icontains=search)
                if column == "tags":
                    queryset = queryset.filter(tags__icontains=search)
                if column == "sku":
                    queryset = queryset.filter(product_variant__sku=search)
                if column == "barcode":
                    queryset = queryset.filter(product_variant__barcode=search)

            if status is not None:
                if status.lower() == 'active':
                    queryset = queryset.filter(is_active=True)
                elif status.lower() == 'inactive':
                    queryset = queryset.filter(is_active=False)
                else:
                    raise exceptions.ParseError("Invalid status filter")

            if approval_status is not None:
                if approval_status.lower() == 'approved':
                    queryset = queryset.filter(status='Approved')
                elif approval_status.lower() == 'disapproved':
                    queryset = queryset.filter(status='disapproved')
                else:
                    raise exceptions.ParseError("Invalid approval status filter")

            return queryset
        except Exception as e:
            print(e)
            raise exceptions.ParseError(str(e))


class ParenttOrderListView(ListCreateAPIView):
    serializer_class = ParentOrderListSerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        try:
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

            return queryset
        except Exception as e:
            print(e)
            raise exceptions.ParseError(str(e))


class CustomerListView(ListCreateAPIView):
    serializer_class = CustomerListSerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        queryset = Customer.objects.filter(deleted=False)
        return queryset
