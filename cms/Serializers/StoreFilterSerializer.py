
from rest_framework import serializers
from cms.models import StoreFilter, PriceRangeFilter


class StoreFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreFilter
        fields = '__all__'
