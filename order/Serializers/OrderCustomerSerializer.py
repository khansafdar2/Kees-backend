
from rest_framework import serializers
from crm.models import Customer


class OrderCustomerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('id', 'first_name', 'last_name', 'phone', 'email')