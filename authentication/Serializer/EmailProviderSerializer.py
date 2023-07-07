
from authentication.models import EmailProvider
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator


class EmailProviderSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmailProvider
        fields = "__all__"
        validators = [
            UniqueTogetherValidator(
                queryset=EmailProvider.objects.all(),
                fields=['provider_type', 'from_email']
            )
        ]

    def create(self, validate_data):
        instance = EmailProvider.objects.create(**validate_data)
        return instance

    def update(self, instance, validate_data):
        EmailProvider.objects.filter(id=instance.id).update(**validate_data)
        return instance

    def validate(self, data):
        return data


class EmailProviderDeleteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = EmailProvider
        fields = ('id',)
