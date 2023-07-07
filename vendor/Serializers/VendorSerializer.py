
import datetime
import random
import secrets
from django.conf import settings
from rest_framework.response import Response
from rest_framework.validators import UniqueTogetherValidator
from rest_framework import serializers, exceptions
from django.db import transaction
from authentication.models import User, UserInvitation
from authentication.BusinessLogic.EmailSender import send_email, email_templates
from setting.models import StoreInformation
from vendor.models import Vendor, Commission


class GetCommissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commission
        exclude = ['created_at', 'updated_at', 'deleted', 'deleted_at']


class VendorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = (
            'id',
            'name',
            'email',
            'created_at',
            'is_active',
            'status'
        )


class CommissionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commission
        fields = (
            'id',
            'title',
            'vendor',
            'type',
            'value'
        )


class VendorDetailSerializer(serializers.ModelSerializer):
    commissions = serializers.SerializerMethodField('get_commissions')

    class Meta:
        model = Vendor
        exclude = ('deleted', 'deleted_at',)

    def get_commissions(self, obj):
        serializer_context = {'request': self.context.get('request')}
        commissions_data = Commission.objects.filter(vendor=obj, deleted=False)
        serializer = GetCommissionSerializer(commissions_data, many=True, context=serializer_context)
        return serializer.data


class AddVendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        exclude = ('id', 'deleted', 'deleted_at', 'created_at', 'updated_at',)
        validators = [
            UniqueTogetherValidator(
                queryset=Vendor.objects.filter(deleted=False),
                fields=['email']
            )
        ]

    @transaction.atomic
    def create(self, validate_data):
        try:
            validated_data = self.initial_data
            validated_data['is_active'] = True
            validated_data['status'] = 'Approved'
            name = validated_data['name']
            email = validated_data['email']
            commissions = validated_data.pop('commissions')

            if '@' in email:
                username_list = email.split('@')
                username = username_list[0]
            else:
                raise Exception('email is invalid')

            unique_id = str(random.randint(1000, 1000000)) + datetime.datetime.now().strftime('%d%m%y%H%M%S')
            validated_data['unique_id'] = unique_id

            vendor = Vendor.objects.create(**validated_data)

            for commission in commissions:
                commission['vendor_id'] = vendor.id
                Commission.objects.create(**commission)

            user = {
                'first_name': name,
                'email': email,
                'username': username,
                'is_vendor': True,
                'vendor': vendor
            }

            user = User.objects.create(**user)

            # User Invitation
            key = str(secrets.token_urlsafe())
            user_invitation = UserInvitation.objects.create(user=user, key=key)

            try:
                store = StoreInformation.objects.get(deleted=False)
            except Exception as e:
                print(e)
                return Response({'detail': 'Store not exist'}, status=404)

            email_content = {'url': settings.VENDOR_URL, 'key': key}
            email_template = email_templates(template_name='user_invite', email_content=email_content)

            invitation_sent = send_email(
                to_email=user.email,
                email_subject=f"{store.store_name} Vendor Invitation",
                email_template=email_template
            )

            if invitation_sent:
                user_invitation.sent = invitation_sent
                user_invitation.save()

            return vendor
        except Exception as e:
            print(e)
            raise Exception(str(e))


class UpdateVendorSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = Vendor
        exclude = ('deleted', 'deleted_at', 'created_at', 'updated_at')
        validators = [
            UniqueTogetherValidator(
                queryset=Vendor.objects.all(),
                fields=['email']
            )
        ]

    def update(self, instance, validate_data):
        try:
            validated_data = self.initial_data
            commissions = validated_data.pop('commissions', None)
            Vendor.objects.filter(id=instance.id).update(**validated_data)

            if commissions:

                for commission in commissions:
                    commission['vendor_id'] = instance.id
                    if 'id' in commission:
                        Commission.objects.filter(id=commission['id']).update(**commission)
                    else:
                        Commission.objects.create(**commission)
            return instance

        except Exception as e:
            print(e)
            raise Exception(str(e))


class DeleteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = Vendor
        fields = ('id',)


class VendorStatusChangeSerializer(serializers.ModelSerializer):
    ids = serializers.ListField(required=True)
    status = serializers.CharField(max_length=50, allow_blank=False, allow_null=False)
    value = serializers.BooleanField(default=False)

    class Meta:
        model = Vendor
        fields = ('ids', 'status', 'value',)

    def create(self, validated_data):
        validated_data = self.initial_data
        if validated_data["status"] == "active":
            try:
                Vendor.objects.filter(id__in=validated_data['ids']).update(is_approved=validated_data["value"])
            except Exception as e:
                raise exceptions.ParseError(str(e))
            return validated_data
        raise exceptions.ParseError("Status can be approved or active")


class DummyDataInsertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Vendor.objects.all(),
                fields=['email']
            )
        ]


class AddExternalVendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        exclude = ('id', 'deleted', 'deleted_at', 'created_at', 'updated_at',)

        validators = [
            UniqueTogetherValidator(
                queryset=Vendor.objects.all(),
                fields=['email']
            )
        ]

    def create(self, validate_data):
        try:
            validated_data = self.initial_data
            validated_data['is_active'] = False
            validated_data['status'] = 'Pending'

            vendor = Vendor.objects.create(**validated_data)

            store = StoreInformation.objects.filter(deleted=False).first()

            # email send to vendor
            try:
                email_content = {'Name': f"{vendor.name}"}
                email_template = email_templates(template_name='vendor_registration_vendor', email_content=email_content)

                send_email(
                    email_subject=f"Welcome to join {store.store_name}",
                    to_email=vendor.email,
                    email_template=email_template
                )
            except Exception as e:
                print(e)

            # email send to admin
            try:
                email_content = {'Name': f"{vendor.name}", 'email': {vendor.email}}
                email_template = email_templates(template_name='vendor_registration_admin', email_content=email_content)

                send_email(
                    email_subject=f"Vendor request at {store.store_name}",
                    to_email=vendor.email,
                    email_template=email_template
                )
            except Exception as e:
                print(e)
            return vendor
        except Exception as e:
            print(e)
            raise Exception(str(e))


class VendorApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        exclude = ('id', 'deleted', 'deleted_at', 'created_at', 'updated_at',)

    def update(self, instance, validated_data):
        status = validated_data['status']
        user = User.objects.filter(vendor_id=instance.id).first()

        try:
            store = StoreInformation.objects.get(deleted=False)
        except Exception as e:
            print(e)
            return Response({'detail': 'Store not exist'}, status=404)

        if instance:
            if instance.status == 'Pending':
                if status == 'Approved':
                    if not user:
                        instance.status = status
                        instance.is_active = True
                        instance.save()
                        username_list = instance.email.split('@')
                        username = username_list[0]
                        user = {
                            'first_name': instance.name,
                            'email': instance.email,
                            'username': username,
                            'is_vendor': True,
                            'vendor': instance
                        }

                        user = User.objects.create(**user)

                        # User Invitation
                        key = str(secrets.token_urlsafe())
                        user_invitation = UserInvitation.objects.create(user=user, key=key)

                        email_content = {'url': settings.VENDOR_URL, 'key': key}
                        email_template = email_templates(template_name='user_invite', email_content=email_content)

                        invitation_sent = send_email(
                            to_email=user.email,
                            email_subject=f"{store.store_name} Vendor Invitation",
                            email_template=email_template
                        )

                        if invitation_sent:
                            user_invitation.sent = invitation_sent
                            user_invitation.save()

                elif status == 'Disapproved':
                    instance.status = status
                    instance.is_active = False
                    instance.save()

            elif instance.status == 'Approved':
                if status == 'Disapproved':
                    instance.status = status
                    instance.is_active = False
                    instance.save()
                    User.objects.filter(id=user.id).update(is_active=False)

            elif instance.status == 'Disapproved':
                if status == 'Approved':
                    if not user:
                        instance.status = status
                        instance.is_active = True
                        instance.save()
                        username_list = instance.email.split('@')
                        username = username_list[0]
                        user = {
                            'first_name': instance.name,
                            'email': instance.email,
                            'username': username,
                            'is_vendor': True,
                            'vendor': instance
                        }

                        user = User.objects.create(**user)

                        # User Invitation
                        key = str(secrets.token_urlsafe())
                        user_invitation = UserInvitation.objects.create(user=user, key=key)

                        email_content = {'url': settings.VENDOR_URL, 'key': key}
                        email_template = email_templates(template_name='user_invite', email_content=email_content)

                        invitation_sent = send_email(
                            to_email=user.email,
                            email_subject=f"{store.store_name} Vendor Invitation",
                            email_template=email_template
                        )

                        if invitation_sent:
                            user_invitation.sent = invitation_sent
                            user_invitation.save()
                    else:
                        instance.status = status
                        instance.is_active = True
                        instance.save()
                        User.objects.filter(id=user.id).update(is_active=True)
        return instance
