
from vendor.models import Vendor
from rest_framework import serializers


class VendorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['name']



