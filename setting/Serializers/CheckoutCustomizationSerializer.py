
from rest_framework import serializers
from setting.models import CheckoutSetting


class CheckoutCustomizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckoutSetting
        exclude = ['id', 'created_at', 'updated_at', 'deleted', 'deleted_at', ]

    def create(self, validate_data):
        instance = CheckoutSetting.objects.create(**validate_data)
        return instance

    def update(self, instance, validate_data):
        data = self.initial_data
        CheckoutSetting.objects.filter(id=instance.id).update(**validate_data)
        return data
