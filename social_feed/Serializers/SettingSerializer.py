
from social_feed.models import Setting
from rest_framework import serializers


class SettingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Setting
        fields = "__all__"

    def create(self, validate_data):
        instance = Setting.objects.create(**validate_data)
        return instance

    def update(self, instance, validate_data):
        Setting.objects.filter(id=instance.id).update(**validate_data)
        return instance
