
from rest_framework import serializers
from setting.models import Region, Country, City


class RegionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        exclude = ['deleted', 'deleted_at']

    def create(self, validate_data):
        instance = Region.objects.create(**validate_data)
        return instance

    def update(self, instance, validate_data):
        Region.objects.filter(id=instance.id).update(**validate_data)
        return instance


class CountryListSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source='region.name', allow_null=False, allow_blank=False, required=False)

    class Meta:
        model = Country
        exclude = ['deleted', 'deleted_at']

    def create(self, validate_data):
        validated_data = self.initial_data
        region_id = validated_data.pop('region_id')
        instance = Country.objects.create(region_id=region_id, **validated_data)
        return instance

    def update(self, instance, validate_data):
        validated_data = self.initial_data
        region_id = validated_data.pop('region_id')
        Country.objects.filter(id=instance.id).update(region_id=region_id, **validated_data)
        return instance


class CityListSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', allow_null=False, allow_blank=False, required=False)

    class Meta:
        model = City
        exclude = ['deleted', 'deleted_at']

    def create(self, validate_data):
        validated_data = self.initial_data
        country_id = validated_data.pop('country_id')
        instance = City.objects.create(country_id=country_id, **validated_data)
        return instance

    def update(self, instance, validate_data):
        validated_data = self.initial_data
        country_id = validated_data.pop('country_id')
        City.objects.filter(id=instance.id).update(country_id=country_id, **validated_data)
        return instance
