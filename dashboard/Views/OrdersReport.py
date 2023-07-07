
import csv
from datetime import datetime
from rest_framework import exceptions
from rest_framework.views import APIView
from django.http import HttpResponse
from authentication.BusinessLogic.ApiPermissions import AccessApi
from order.models import Order, Customer, ChildOrder, ChildOrderLineItems
from storefront.BussinessLogic.CheckDomain import check_domain


class OrdersReport(APIView):
    def get(self, request):
        access = AccessApi(self.request.user, "dashboard")
        access_domain = check_domain(self.request)
        if not access or access_domain:
            raise exceptions.ParseError("This user does not have permission to this Api")

        start_date = self.request.GET.get('start_date', None)
        end_date = self.request.GET.get('end_date', None)
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_date = datetime.strptime(f"{end_date} 23:59:59", '%Y-%m-%d %H:%M:%S')

        if start_date and end_date:
            orders = Order.objects.filter(created_at__gte=start_date, created_at__lte=end_date)
        elif start_date:
            orders = Order.objects.filter(created_at__gte=start_date)
        elif end_date:
            orders = Order.objects.filter(created_at__lte=end_date)
        else:
            orders = Order.objects.all()

        if orders is not None:
            response = HttpResponse(content_type='text/csv')
            writer = csv.writer(response)

            writer.writerow(
                ['serial no', 'customer name', 'email', 'phone', 'order name', 'order id', 'sku no', 'product title',
                 'sales value', 'sales discount', 'shipping', 'net sales',
                 'cost', 'payment method', 'order status', 'payment status',
                 'child order name', 'child payment method', 'vendor name', 'vendor commission']
            )

            sr = 0
            for order in orders:
                customer = Customer.objects.filter(id=order.customer_id).first()
                child_orders = ChildOrder.objects.filter(order_id=order.id)

                for child_order in child_orders:
                    child_order_line_items = ChildOrderLineItems.objects.filter(child_order=child_order, deleted=False)

                    for child_order_line_item in child_order_line_items:
                        net_sale = (child_order_line_item.price * child_order_line_item.quantity) + child_order_line_item.shipping_amount
                        sr += 1

                        writer.writerow(
                            [sr, customer.first_name, customer.email, customer.phone, order.name, order.order_id,
                             child_order_line_item.variant.sku, child_order_line_item.variant.product.title,
                             child_order_line_item.compare_at_price, child_order_line_item.price,
                             child_order_line_item.shipping_amount, net_sale,
                             child_order_line_item.variant.cost_per_item, order.payment_method, order.order_status,
                             order.payment_status, child_order.name, child_order.payment_method,
                             child_order.vendor.name, child_order_line_item.vendor_commission]
                        )

            response['Content-Disposition'] = 'attachment; filename="orders_report.csv"'
            return response
