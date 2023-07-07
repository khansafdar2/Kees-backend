
from rest_framework import serializers
from setting.models import PaymentMethod
from paymentgateway.models import GatewayCredentials


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ('id', 'title', 'description')

    def create(self, validate_data):
        instance = PaymentMethod.objects.create(**validate_data)
        return instance

    def update(self, instance, validate_data):
        data = self.initial_data
        PaymentMethod.objects.filter(id=instance.id).update(**validate_data)
        return data


class GatewaySerializer(serializers.ModelSerializer):
    class Meta:
        model = GatewayCredentials
        fields = ('id', 'gateway_name', 'description')
