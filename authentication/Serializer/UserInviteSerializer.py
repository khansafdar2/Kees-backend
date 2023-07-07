
from rest_framework import serializers, exceptions
from authentication.models import UserInvitation


class InviteSerializer(serializers.ModelSerializer):
    key = serializers.CharField(required=True)

    class Meta:
        model = UserInvitation
        fields = ('key',)


class PasswordSerializer(serializers.ModelSerializer):
    key = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    class Meta:
        model = UserInvitation
        fields = ('key', 'password', 'confirm_password')

    def validate(self, data):
        special_sym = ['$', '#', '%','@','&','!']

        if data['password'] != data['confirm_password']:
            raise exceptions.ParseError("password didn't match")

        if len(data['password']) < 8:
            raise exceptions.ParseError('Password length should be at least 8')

        if not any(char.isdigit() for char in data['password']):
            raise exceptions.ParseError('Password should have at least one numeral')

        if not any(char.isupper() for char in data['password']):
            raise exceptions.ParseError('Password should have at least one uppercase letter')

        if not any(char.islower() for char in data['password']):
            raise exceptions.ParseError('Password should have at least one lowercase letter')

        if not any(char in special_sym for char in data['password']):
            raise exceptions.ParseError('Password should have at least one of the symbols $#%@&!')

        return data
