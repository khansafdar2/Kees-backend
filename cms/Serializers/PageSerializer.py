
from rest_framework import serializers
from cms.models import Page, PageHandle
from products.BusinessLogic.RemoveSpecialCharacters import remove_specialcharacters
from datetime import datetime


class PageSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    content = serializers.CharField(required=True)
    publish_status = serializers.BooleanField(required=True)
    # handle = serializers.CharField(required=True)

    class Meta:
        model = Page
        fields = '__all__'

    def create(self, validate_data):
        validated_data = self.initial_data
        handle_name = remove_specialcharacters(validated_data['title'].replace(' ', '-').lower())
        handle = PageHandle.objects.filter(name=handle_name).first()

        if handle is not None:
            handle_name = handle_name + "-" + str(handle.count)
            handle.count = handle.count + 1
            handle.save()
        else:
            handle = PageHandle()
            handle.name = handle_name
            handle.count = 1
            handle.save()
        validated_data['handle'] = handle_name

        instance = Page.objects.create(**validated_data)
        return instance

    def update(self, instance, validate_data):
        Page.objects.filter(id=instance.id).update(**validate_data)
        return instance


class PageDeleteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = Page
        fields = ('id',)

