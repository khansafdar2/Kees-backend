
from rest_framework.validators import UniqueTogetherValidator
from rest_framework import serializers, exceptions
from vendor.models import Vendor


class VendorMigrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Vendor.objects.all(),
                fields=['email']
            )
        ]

    def create(self, validate_data):
        validated_data = self.initial_data
        vendor_data = {
            "name": validated_data['name'],
            "email": validated_data['email'],
            "phone": validated_data['phone'],
            "city": validated_data['city'],
            "address": validated_data['address'],
            "commission_type": validated_data['commission type'],
            "commission_value": validated_data['commission value'],
            "notes": validated_data['notes']
        }

        vendor = Vendor.objects.create(**vendor_data)
        return vendor
