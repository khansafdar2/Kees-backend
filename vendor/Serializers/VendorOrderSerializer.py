
from rest_framework import serializers

from crm.models import Customer
from order.models import ChildOrder


class VendorOrderListSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField('get_customer')

    class Meta:
        model = ChildOrder
        fields = ('id', 'name', 'order_id', 'customer_name', 'vendor_id', 'created_at', 'total_price', 'payment_status',
                  'fulfillment_status', 'order_status')

    def get_customer(self, obj):
        customer = Customer.objects.filter(order_customer__childOrders_order=obj, deleted=False).first()
        if not customer:
            return None
        name = f"{customer.first_name} {customer.last_name}"
        return name

