
from rest_framework import serializers
from cms.models import Page


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ('handle', 'title', 'content', 'slug', 'seo_title', 'seo_description','seo_keywords')
