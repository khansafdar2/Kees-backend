
import secrets, os
from rest_framework import serializers
from rest_framework.response import Response
from django.conf import settings
from authentication.models import User, RolePermission, UserInvitation, UserLastLogin
from drf_yasg.utils import swagger_serializer_method
from rest_framework.validators import UniqueValidator
from authentication.BusinessLogic.EmailSender import send_email, email_templates
from setting.models import StoreInformation


class RolePermissionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = RolePermission
        exclude = ['deleted', 'deleted_at', 'created_at', 'updated_at']


class UserLastLoginSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserLastLogin
        fields = ("ip_address", "location", "date")


class UserListSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField('get_permission_serializer')
    last_login_list = serializers.SerializerMethodField('get_last_login_serializer')

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "date_joined",
            "is_active",
            "email_2fa",
            "phone_2fa",
            "last_login",
            "newsletter",
            "is_superuser",
            "is_admin",
            "is_owner",
            "permissions",
            "last_login_list"
        )

    @swagger_serializer_method(serializer_or_field=RolePermissionSerializer)
    def get_permission_serializer(self, obj):
        serializer_context = {'request': self.context.get('request')}
        if obj.is_superuser:
            return {
                "dashboard": True,
                "theme": True,
                "products": True,
                "orders": True,
                "customer": True,
                "discounts": True,
                "configuration": True,
                "customization": True,
                "vendor": True
            }
        permissions = RolePermission.objects.filter(user=obj).first()
        serializer = RolePermissionSerializer(permissions, context=serializer_context)
        return serializer.data

    @swagger_serializer_method(serializer_or_field=UserLastLoginSerializer(many=True))
    def get_last_login_serializer(self, obj):
        serializer_context = {'request': self.context.get('request')}
        last_logins = UserLastLogin.objects.filter(user=obj)[0:10]
        serializer = UserLastLoginSerializer(last_logins, many=True, context=serializer_context)
        return serializer.data


class AddUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    username = serializers.CharField()
    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])
    permissions = serializers.SerializerMethodField('get_permission_serializer')

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "newsletter",
            "permissions"
        )

    @swagger_serializer_method(serializer_or_field=RolePermissionSerializer)
    def get_permission_serializer(self, obj):
        serializer_context = {'request': self.context.get('request')}
        permissions = RolePermission.objects.filter(user=obj)
        serializer = RolePermissionSerializer(permissions, many=True, context=serializer_context)
        return serializer.data

    def validate_username(self, value):
        if ' ' in value:
            raise serializers.ValidationError("Spaces cannot be in username")
        return value

    def create(self, validated_data):
        user = User.objects.filter(email=validated_data.get('email')).first()
        if user:
            user.deleted = False
            user.deleted_at = None
            user.save()

            RolePermission.objects.filter(user=user).update(**validated_data.get('permissions'))
        else:
            check_user = User.objects.filter(username=validated_data.get("username")).first()
            if check_user is not None:
                raise serializers.ValidationError({"detail": "Username already exist"})
            else:
                validated_data = self.initial_data
                permissions_data = validated_data.pop('permissions')
                is_admin = True
                for permission in permissions_data:
                    if not permissions_data[permission]:
                        is_admin = False
                validated_data['is_admin'] = is_admin
                validated_data['is_active'] = False

                user = User.objects.create(**validated_data)
                RolePermission.objects.create(user=user, **permissions_data)

            # User Invitation
            key = str(secrets.token_urlsafe())
            user_invitation = UserInvitation.objects.create(user=user, key=key)

            try:
                store = StoreInformation.objects.get(deleted=False)
            except Exception as e:
                print(e)
                return Response({'detail': 'Store not exist'}, status=404)

            email_content = {'url': settings.CLIENT_URL, 'key': key}
            email_template = email_templates(template_name='user_invite', email_content=email_content)

            invitation_sent = send_email(
                to_email=user.email,
                email_subject=f"{store.store_name} User Invitation",
                email_template=email_template
                )

            if invitation_sent:
                user_invitation.sent = invitation_sent
                user_invitation.save()

            return user


class UpdateUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    username = serializers.CharField()
    # email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])
    permissions = serializers.SerializerMethodField('get_permission_serializer')

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "newsletter",
            "permissions"
        )

    @swagger_serializer_method(serializer_or_field=RolePermissionSerializer)
    def get_permission_serializer(self, obj):
        serializer_context = {'request': self.context.get('request')}
        permissions = RolePermission.objects.filter(user=obj)
        serializer = RolePermissionSerializer(permissions, many=True, context=serializer_context)
        return serializer.data

    def validate_username(self, value):
        if ' ' in value:
            raise serializers.ValidationError("Spaces cannot be in username")
        return value

    def update(self, instance, validated_data):
        validated_data = self.initial_data
        try:
            permissions_data = validated_data.pop('permissions')
            email = validated_data.pop('email', None)
            username = validated_data.pop('username', None)

            is_admin = True
            for permission in permissions_data:
                if not permissions_data[permission]:
                    is_admin = False

            validated_data['is_admin'] = is_admin
            User.objects.filter(id=instance.id).update(**validated_data)
            RolePermission.objects.filter(user_id=instance.id).update(**permissions_data)
        except Exception as e:
            print(e)
            User.objects.filter(id=instance.id).update(**validated_data)
        return instance


class UserDeleteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = User
        fields = ('id',)


class ChangePasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "password")

    def update(self, instance, validated_data):
        instance.set_password(validated_data.get("password"))
        instance.save()
        return instance
