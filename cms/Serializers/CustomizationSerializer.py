
from rest_framework import serializers
from cms.models import Customization


class CustomizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customization
        fields = '__all__'
