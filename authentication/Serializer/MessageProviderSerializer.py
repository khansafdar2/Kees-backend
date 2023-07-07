
from authentication.models import MessageProvider
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator


class MessageProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageProvider
        fields = "__all__"
        validators = [
            UniqueTogetherValidator(
                queryset=MessageProvider.objects.all(),
                fields=['provider_type', 'provider_mask']
            )
        ]

    def create(self, validate_data):
        instance = MessageProvider.objects.create(**validate_data)
        return instance

    def update(self, instance, validate_data):
        MessageProvider.objects.filter(id=instance.id).update(**validate_data)
        return instance

    def validate(self, data):
        return data


class MessageProviderDeleteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = MessageProvider
        fields = ('id',)
