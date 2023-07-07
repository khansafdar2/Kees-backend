
from rest_framework import serializers
from products.models import Collection, Brand


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ('title', 'handle', 'slug', 'seo_title', 'seo_description','seo_keywords')


class BrandSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='name')

    class Meta:
        model = Brand
        fields = ('title', 'handle')
