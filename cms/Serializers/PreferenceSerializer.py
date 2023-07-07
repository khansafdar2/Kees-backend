
from rest_framework import serializers
from cms.models import Preferences


class PreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preferences
        fields = ('title', 'description', 'image', 'enable_password', 'seo_title', 'seo_description','seo_keywords')
