
from rest_framework import serializers
from notification.models import FirebaseSettings


class FirebaseSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FirebaseSettings
        fields = '__all__'
