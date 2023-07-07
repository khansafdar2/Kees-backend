

from rest_framework import serializers
from cms.models import MenuItem, Page


class MenuSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    page_type = serializers.CharField(required=True)
    content_type = serializers.CharField(required=True)

    class Meta:
        model = MenuItem
        # fields = ['title', 'content', 'publish_status', 'publish_date', 'handle', 'created_at', 'updated_at']
        fields = '__all__'

    def create(self, validate_data):
        if validate_data['page_type'] == "Page":
            link = Page.objects.get(id=validate_data['content_type'])
            validate_data.pop('content_type')
        instance = MenuItem.objects.create(content_object=link, **validate_data)
        return instance

    def update(self, instance, validate_data):
        MenuItem.objects.filter(id=instance.id).update(**validate_data)
        return instance

