
from rest_framework import serializers, exceptions
from authentication.models import User


class ForgotPasswordSerialzier(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        try:
            email = data.get("email", "")
            data["user"] = User.objects.get(email=email)
        except User.DoesNotExist:
            msg = "Email not found"
            raise exceptions.NotFound(msg)
        except User.MultipleObjectsReturned:
            raise exceptions.APIException()
        return data


class ChangeForgotPasswordSerializer(serializers.Serializer):
    code = serializers.IntegerField(required=True)
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)


class VerifyCodeSerializer(serializers.Serializer):
    code = serializers.CharField()
