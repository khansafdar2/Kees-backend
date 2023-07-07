
import os, csv
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from order.models import Order, Customer, ChildOrder, Vendor


class OrdersExport(APIView):
    def get(self, request):
        ids = self.request.GET.get('ids', None)

        if ids != 'all':
            string_data = str(ids)
            ids = string_data.split(',')
            orders = Order.objects.filter(id__in=ids)
        else:
            orders = Order.objects.all()
        if orders is not None:
            response = HttpResponse(content_type='text/csv')
            writer = csv.writer(response)

            writer.writerow(
                ['name', 'email', 'phone', 'order_name', 'order_id', 'payment_method', 'subtotal_price', 'total_shipping',
                 'total_price', 'fulfillment_status', 'payment_status', 'order_status', 'child_order_name',
                 'child_payment_method', 'child_subtotal_price', 'child_total_shipping', 'child_total_price',
                 'child_fulfillment_status', 'child_payment_status', 'child_order_status', 'vendor_name'])

            for order in orders:
                try:
                    customer = Customer.objects.filter(id=order.customer_id, deleted=False).first()
                    child_orders = ChildOrder.objects.filter(order_id=order.id)
                    counter = 1
                    for child_order in child_orders:
                        vendor = Vendor.objects.filter(id=child_order.vendor_id).first()
                        if counter == 1:
                            writer.writerow(
                                [customer.first_name + " " + customer.last_name, customer.email, customer.phone, order.name, order.order_id,
                                 order.payment_method, order.subtotal_price, order.total_shipping, order.total_price,
                                 order.fulfillment_status, order.payment_status, order.order_status, child_order.name,
                                 child_order.order_id, child_order.payment_method, child_order.subtotal_price,
                                 child_order.total_shipping, child_order.total_price, child_order.fulfillment_status,
                                 child_order.payment_status, child_order.order_status, vendor.name])
                            counter += 1
                        else:
                            writer.writerow(
                                [None, None, None, None, None, None, None, None, None, None, None, child_order.name,
                                 child_order.order_id, child_order.payment_method, child_order.subtotal_price,
                                 child_order.total_shipping, child_order.total_price, child_order.fulfillment_status,
                                 child_order.payment_status, child_order.order_status, vendor.name])
                except Exception as e:
                    print(e)
            response['Content-Disposition'] = 'attachment; filename="orders_export.csv"'
            return response
