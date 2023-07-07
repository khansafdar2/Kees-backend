
from rest_framework import serializers, exceptions


class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, data):
        special_sym = ['$', '#', '%','@','&','!']

        if data['password'] != data['confirm_password']:
            raise exceptions.ValidationError("password didn't match")

        if len(data['password']) < 8:
            raise exceptions.ValidationError('length should be at least 8')

        if not any(char.isdigit() for char in data['password']):
            raise exceptions.ValidationError('Password should have at least one numeral')

        if not any(char.isupper() for char in data['password']):
            raise exceptions.ValidationError('Password should have at least one uppercase letter')

        if not any(char.islower() for char in data['password']):
            raise exceptions.ValidationError('Password should have at least one lowercase letter')

        if not any(char in special_sym for char in data['password']):
            raise exceptions.ValidationError('Password should have at least one of the symbols $#%@&!')

        return data
