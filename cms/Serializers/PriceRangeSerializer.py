
from rest_framework import serializers
from cms.models import StoreFilter, PriceRangeFilter, PriceRangeHandle


class PriceFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceRangeFilter
        fields = ('id', 'min_price', 'max_price', 'handle')

    def create(self, validate_data):
        validated_data = self.initial_data

        # Save Unique Product Handle
        handle_name = f"{validated_data['min_price']}-{validated_data['max_price']}"
        handle = PriceRangeHandle.objects.filter(name=handle_name).first()
        if handle is not None:
            handle_name = handle_name + "-" + str(handle.count)
            handle.count = handle.count + 1
            handle.save()
        else:
            handle = PriceRangeHandle()
            handle.name = handle_name
            handle.count = 1
            handle.save()
        validated_data['handle'] = handle_name

        instance = PriceRangeFilter.objects.create(**validated_data)
        return instance

    def update(self, instance, validate_data):
        PriceRangeFilter.objects.filter(id=instance.id).update(**validate_data)
        return instance

