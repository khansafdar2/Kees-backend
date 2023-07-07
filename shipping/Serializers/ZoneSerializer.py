from django.db.models import Q
from rest_framework import serializers
from setting.models import Country, City, Region
from setting.Serializers.LocationsSerializer import RegionListSerializer, CountryListSerializer, CityListSerializer
from shipping.models import Zone
from rest_framework.validators import UniqueTogetherValidator
from django.db import transaction


class ShippingZoneListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = ('id', 'title',)


class ZoneListSerializer(serializers.ModelSerializer):
    region = serializers.SerializerMethodField('get_region')
    country = serializers.SerializerMethodField('get_country')
    city = serializers.SerializerMethodField('get_city')

    class Meta:
        model = Zone
        fields = (
            'id',
            'title',
            'region',
            'country',
            'city',
            'is_active'
        )

    def get_region(self, obj):
        serializer_context = {'request': self.context.get('request')}
        region_data = Region.objects.filter(zone_region=obj, is_active=True, deleted=False)[:8]
        serializer = RegionListSerializer(region_data, many=True, context=serializer_context)
        return serializer.data

    def get_country(self, obj):
        serializer_context = {'request': self.context.get('request')}
        country_data = Country.objects.filter(zone_country=obj, is_active=True, deleted=False)[:8]
        serializer = CountryListSerializer(country_data, many=True, context=serializer_context)
        return serializer.data

    def get_city(self, obj):
        serializer_context = {'request': self.context.get('request')}
        city_data = City.objects.filter(zone_city=obj, is_active=True, deleted=False)[:8]
        serializer = CityListSerializer(city_data, many=True, context=serializer_context)
        return serializer.data


class AddZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = ('id', 'title')

        validators = [
            UniqueTogetherValidator(
                queryset=Zone.objects.filter(deleted=False),
                fields=['title']
            )
        ]

    @transaction.atomic
    def create(self, validated_data):
        try:
            validated_data = self.initial_data

            region = validated_data.pop('region')
            country = validated_data.pop('country', None)
            city = validated_data.pop('city', None)

            zone = Zone.objects.create(title=validated_data['title'])
            zone.region.set(region)

            city_ids = list(set(Zone.objects.filter(deleted=False, is_active=True).values_list('city', flat=True)))

            if not country or len(country) == 0:
                country_ids = Country.objects.filter(region_id=region)

                if country_ids:
                    zone.country.set(country_ids)
                    if city_ids[0] is not None:
                        cities = City.objects.filter(country__in=country_ids).exclude(id__in=city_ids)
                    else:
                        cities = City.objects.filter(country__in=country_ids)
                    zone.city.set(cities)
            else:
                zone.country.set(country)
                if city or len(city) > 0:
                    zone.city.set(city)
                else:
                    if city_ids[0] is not None:
                        cities = City.objects.filter(country__in=country).exclude(id__in=city_ids)
                    else:
                        cities = City.objects.filter(country__in=country)
                    zone.city.set(cities)

            return zone
        except Exception as e:
            print(e)
            raise Exception(str(e))

    @transaction.atomic
    def update(self, instance, validated_data):
        try:
            validated_data = self.initial_data

            region = validated_data.pop('region')
            country = validated_data.pop('country', None)
            city = validated_data.pop('city', None)

            Zone.objects.filter(id=instance.id).update(title=validated_data['title'])
            zone = Zone.objects.get(id=instance.id)
            zone.region.set(region)

            city_ids = list(set(Zone.objects.filter((~Q(id=instance.id)), deleted=False, is_active=True).values_list('city', flat=True)))

            if not country or len(country) == 0:
                country_ids = Country.objects.filter(region_id=region)

                if country_ids:
                    zone.country.set(country_ids)
                    cities = City.objects.filter(country__in=country_ids).exclude(id__in=city_ids)
                    zone.city.set(cities)
            else:
                zone.country.set(country)
                if city or len(city) > 0:
                    zone.city.set(city)
                else:
                    cities = City.objects.filter(country__in=country).exclude(id__in=city_ids)
                    zone.city.set(cities)

            return instance
        except Exception as e:
            print(e)
            raise Exception(str(e))


class ZoneDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        exclude = ('deleted', 'deleted_at',)


class VendorZoneListSerializer(serializers.ModelSerializer):
    region = serializers.SerializerMethodField('get_region')
    country = serializers.SerializerMethodField('get_country')
    city = serializers.SerializerMethodField('get_city')

    class Meta:
        model = Zone
        fields = (
            'title',
            'region',
            'country',
            'city',
        )

    def get_region(self, obj):
        region_data = Region.objects.filter(zone_region=obj, is_active=True, deleted=False).values_list('name', flat=True)
        return region_data

    def get_country(self, obj):
        country_data = Country.objects.filter(zone_country=obj, is_active=True, deleted=False).values_list('name', flat=True)
        return country_data

    def get_city(self, obj):
        city_data = City.objects.filter(zone_city=obj, is_active=True, deleted=False).values_list('name', flat=True)
        return city_data



