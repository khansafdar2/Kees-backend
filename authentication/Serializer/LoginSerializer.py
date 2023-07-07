
from django.contrib.auth import authenticate
from rest_framework import serializers, exceptions
from authentication.models import User
from datetime import datetime


class ServiceUnavailable(exceptions.ValidationError):
    status_code = 401


class LoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get("username_or_email", "")
        password = data.get("password", "")
        if username and password:
            if "@" in username:
                try:
                    fetch_user = User.objects.get(email=username)
                    username = fetch_user.username
                except User.DoesNotExist:
                    raise exceptions.ValidationError({"detail": "Invalid email"})
            user = authenticate(username=username, password=password)
            if user is not None and not user.deleted:
                data["user"] = user
                user.last_login = datetime.now()
                if user.first_name == "":
                    user.first_name = username
                if user.is_superuser:
                    user.is_owner = True
                user.save()
            else:
                msg = {"detail": "Invalid credentials"}
                raise exceptions.ValidationError(msg)
        else:
            msg = "Must provide username and password both"
            raise exceptions.ParseError(msg)
        return data
