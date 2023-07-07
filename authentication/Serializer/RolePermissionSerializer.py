
from rest_framework import serializers
from authentication.models import RolePermission


class RolePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolePermission
        fields = '__all__'

    def create(self, validate_data):
        instance = RolePermission.objects.create(**validate_data)
        return instance

    def update(self, instance, validate_data):
        RolePermission.objects.filter(id=instance.id).update(**validate_data)
        return instance


class RolePermissionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolePermission
        fields = ("id",)
