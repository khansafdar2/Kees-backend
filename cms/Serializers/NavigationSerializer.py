
from cms.models import Navigation
from rest_framework import serializers


class NavigationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Navigation
        fields = ('id', 'title')


class NavigationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Navigation
        fields = ('id', 'title', 'navigation_json')

    def create(self, validated_data):
        validated_data = self.initial_data
        navigation = Navigation.objects.create(**validated_data)
        return navigation

    def update(self, instance, validated_data):
        validated_data = self.initial_data
        Navigation.objects.filter(id=instance.id).update(**validated_data)
        return instance
