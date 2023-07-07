
from rest_framework import serializers
from setting.models import StoreInformation


class StoreInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = StoreInformation
        fields = '__all__'

    def create(self, validate_data):
        instance = StoreInformation.objects.create(**validate_data)
        return instance

    def update (self, instance, validate_data):
        StoreInformation.objects.filter(id=instance.id).update(**validate_data)
        return instance


class StoreInfoDeleteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = StoreInformation
        fields = ('id',)

