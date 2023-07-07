from datetime import datetime
import random

from rest_framework import serializers

from crm.Serializers.CustomerSerializer import CustomerDetailSerializer
from crm.models import Coupon, Customer


class CouponListSerializer(serializers.ModelSerializer):
    customer_email = serializers.SerializerMethodField('get_customer')

    class Meta:
        model = Coupon
        fields = '__all__'

    def get_customer(self, obj):
        customer = Customer.objects.filter(id=obj.customer_id).first().email
        return customer


class CouponAddSerializer(serializers.ModelSerializer):
    expiry_date = serializers.DateTimeField()

    class Meta:
        model = Coupon
        exclude = ('unique_id',)

    def create(self, validated_data):
        validated_data = self.initial_data
        customer_id = validated_data.pop('customer', None)
        current_date = datetime.now()
        unique_id = (str(random.randint(1000, 1000000)) + '-' + current_date.strftime("%Y-%m-%dT%H-%M-%S")). \
            replace('-', '')
        coupon = Coupon.objects.create(customer_id=customer_id, unique_id=unique_id, **validated_data)
        return coupon

    def update(self, instance, validated_data):
        validated_data = self.initial_data
        customer_id = validated_data.pop('customer', None)
        Coupon.objects.filter(id=instance.id).update(customer_id=customer_id, **validated_data)
        return instance


class CouponDetailSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField('get_customer')

    class Meta:
        model = Coupon
        exclude = ('is_deleted', 'deleted_at',)

    def get_customer(self, obj):
        serializer_context = {'request': self.context.get('request')}
        customer = Customer.objects.filter(id=obj.customer_id).first()
        serializer = CustomerDetailSerializer(customer, context=serializer_context)
        return serializer.data
