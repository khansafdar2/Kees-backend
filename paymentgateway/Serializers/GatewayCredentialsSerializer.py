
from paymentgateway.models import GatewayCredentials
from rest_framework import serializers


# class GatewayCredentialsListSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = GatewayCredentials
#         fields = '__all__'


class GatewayCredentialsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GatewayCredentials
        fields = '__all__'

    def create(self, validated_data):
        validated_data = self.initial_data
        gateway_credentials = GatewayCredentials.objects.create(**validated_data)
        return gateway_credentials

    def update(self, instance, validated_data):
        validated_data = self.initial_data
        GatewayCredentials.objects.filter(id=instance.id).update(**validated_data)
        return instance
