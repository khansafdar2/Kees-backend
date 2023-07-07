
from rest_framework import serializers
from order.models import Order, LineItems


class DashboardCountSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField('get_count')

    class Meta:
        model = Order
        fields = ('count',)

    def get_count(self, obj):
        data = self.data
        sub_total_price = 0
        for i in data:
            sub_total_price = sub_total_price + float(i.subtotal_price)
        print(sub_total_price)
        return data
