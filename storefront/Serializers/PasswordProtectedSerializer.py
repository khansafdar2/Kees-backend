
from rest_framework import serializers
from cms.models import Preferences
from rest_framework import validators, exceptions


class PasswordCheckerSerializer(serializers.Serializer):
    password = serializers.CharField()

    def validate(self, data):
        data = data.get("password", "")
        try:
            preference = Preferences.objects.all().first()
            if data == preference.password:
                return preference
            raise exceptions.ParseError("Password did not match")
        except Exception as e:
            print(e)
            raise exceptions.ValidationError({"detail": "Data not found"})




