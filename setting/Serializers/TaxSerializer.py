
from rest_framework import serializers
from setting.models import Tax


class TaxSerializer(serializers.ModelSerializer):
    tax_percentage = serializers.DecimalField(decimal_places=2, max_digits=4)

    class Meta:
        model = Tax
        fields = ('id', 'tax_name', 'tax_percentage')

    def create(self, validate_data):
        instance = Tax.objects.create(**validate_data)
        return instance

    def update(self, instance, validate_data):
        Tax.objects.filter(id=instance.id).update(**validate_data)
        return instance
