
from rest_framework import serializers
from authentication.models import User


class TransferOwnershipSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = User
        fields = ('id',)
