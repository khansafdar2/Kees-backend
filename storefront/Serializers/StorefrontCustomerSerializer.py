from datetime import datetime
import random

from rest_framework import serializers, exceptions
from crm.models import Customer, Address, CustomerForgetPassword, Wallet
from drf_yasg.utils import swagger_serializer_method
from rest_framework.validators import UniqueValidator
from crm.Serializers.CustomerSerializer import AddressSerializer
from order.models import Order
from order.Serializers.CheckoutOrderSerializer import OrdersListSerializer
from authentication.BusinessLogic.EmailSender import send_email, email_templates
import base64, secrets
from django.utils import timezone
from django.conf import settings
from setting.models import StoreInformation


class CustomerSignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[UniqueValidator(queryset=Customer.objects.filter(has_account=True))])

    class Meta:
        model = Customer
        fields = ('id', 'token', 'email')

    def create(self, validated_data):
        validated_data = self.initial_data

        if len(validated_data['password']) < 8:
            raise exceptions.ParseError("Password be at least 8 characters")

        validated_data['password'] = base64.b64encode(validated_data['password'].encode("ascii")).decode("ascii")

        customer = Customer.objects.filter(email=validated_data['email']).first()
        if customer:
            if customer.has_account:
                raise exceptions.ParseError("Your account already exist, please login your account")
            else:
                customer.has_account = True
                #password should be encrypted
                customer.password = validated_data['password']
                customer.token = "Token " + secrets.token_hex(20)
                customer.last_login = timezone.now()
                customer.save()
                current_date = datetime.now()
                unique_id = (str(random.randint(1000, 1000000)) + '-' + current_date.strftime("%Y-%m-%dT%H-%M-%S")). \
                    replace('-', '')
                Wallet.objects.create(customer=customer, unique_id=unique_id)

        else:
            validated_data['token'] = "Token " + secrets.token_hex(20)
            validated_data['last_login'] = timezone.now()
            customer = Customer.objects.create(**validated_data)
            current_date = datetime.now()
            unique_id = (str(random.randint(1000, 1000000)) + '-' + current_date.strftime("%Y-%m-%dT%H-%M-%S")). \
                replace('-', '')
            Wallet.objects.create(customer=customer, unique_id=unique_id)

        if customer.email:
            try:
                email_content = {'Name': f"{customer.first_name} {customer.last_name}"}
                email_template = email_templates(template_name='customer_welcome', email_content=email_content)

                send_email(
                    email_subject="Welcome for signup here",
                    to_email=customer.email,
                    email_template=email_template
                )
            except Exception as e:
                print(e)

        return customer


class SignInSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get("email", "")
        password = data.get("password", "")

        if email and password:
            if "@" in email:
                try:
                    customer = Customer.objects.get(email=email, deleted=False)
                except Customer.DoesNotExist:
                    raise exceptions.ValidationError({"detail": "Invalid email"})

                if customer:
                    if customer.has_account:
                        password = base64.b64encode(password.encode("ascii")).decode("ascii")
                        if password == customer.password:
                            customer.token = "Token " + secrets.token_hex(20)
                            customer.last_login = timezone.now()
                            customer.save()
                            return customer
                        raise exceptions.ValidationError({"detail": "Invalid Password"})
                    else:
                        raise exceptions.ParseError("Invalid Email")
            else:
                raise exceptions.ParseError("Inavlid Email Format")
        else:
            msg = "Must provide username and password both"
            raise exceptions.ParseError(msg)


class CustomerAccountDetailSerializer(serializers.ModelSerializer):
    address = serializers.SerializerMethodField('get_address_serializer')
    orders = serializers.SerializerMethodField('get_orders_list')

    class Meta:
        model = Customer
        fields = ('id', 'first_name', 'last_name', 'email', 'address', 'orders')

    @swagger_serializer_method(serializer_or_field=AddressSerializer)
    def get_address_serializer(self, obj):
        serializer_context = {'request': self.context.get('request')}
        address = Address.objects.filter(customer=obj, deleted=False)
        serializer = AddressSerializer(address, many=True, context=serializer_context)
        return serializer.data

    @swagger_serializer_method(serializer_or_field=OrdersListSerializer)
    def get_orders_list(self, obj):
        serializer_context = {'request': self.context.get('request')}
        orders = Order.objects.filter(customer=obj)
        serializer = OrdersListSerializer(orders, many=True, context=serializer_context)
        return serializer.data


class CustomerAccountUpdateSerializer(serializers.ModelSerializer):
    address = serializers.SerializerMethodField('get_address_serializer')
    orders = serializers.SerializerMethodField('get_orders_list')

    class Meta:
        model = Customer
        fields = ('first_name', 'last_name', 'email', 'address', 'orders')

    @swagger_serializer_method(serializer_or_field=AddressSerializer)
    def get_address_serializer(self, obj):
        serializer_context = {'request': self.context.get('request')}
        address = Address.objects.filter(customer=obj, deleted=False)
        serializer = AddressSerializer(address, many=True, context=serializer_context)
        return serializer.data

    @swagger_serializer_method(serializer_or_field=OrdersListSerializer)
    def get_orders_list(self, obj):
        serializer_context = {'request': self.context.get('request')}
        orders = Order.objects.filter(customer=obj)
        serializer = OrdersListSerializer(orders, many=True, context=serializer_context)
        return serializer.data

    def update(self, instance, validated_data):
        validated_data = self.initial_data
        address = validated_data.pop('address', None)
        customer = instance

        if 'first_name' in validated_data:
            customer.first_name = validated_data['first_name']

        if 'last_name' in validated_data:
            customer.last_name = validated_data['last_name']

        if 'new_password' in validated_data and 'old_password' in validated_data:
            old_password = validated_data.pop('old_password')
            new_password = validated_data.pop('new_password')

            old_password = base64.b64encode(old_password.encode("ascii")).decode("ascii")
            if old_password == customer.password:
                if len(new_password) < 8:
                    raise exceptions.ParseError("Password should be at least 8 characters")
                new_password = base64.b64encode(new_password.encode("ascii")).decode("ascii")
                customer.password = new_password
            else:
                raise exceptions.ParseError("incorrect old password")

        if address is not None:
            address_id = address.get('id', None)
            if address_id:
                Address.objects.filter(id=address_id).update(**address)
            else:
                if address['primary_address']:
                    Address.objects.filter(customer=customer, primary_address=True).update(primary_address=False)

                Address.objects.create(customer=customer, **address)

        if customer:
            customer.save()

        return customer


class CustomerForgetPasswordSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = CustomerForgetPassword
        fields = ('id', 'email')

    def create(self, validated_data):
        validated_data = self.initial_data
        if 'email' in validated_data:
            email = validated_data['email']

            key = str(secrets.token_urlsafe())
            customer = Customer.objects.filter(email=email).first()
            if customer:
                customer_invitation = CustomerForgetPassword.objects.create(customer=customer, key=key)
                store = StoreInformation.objects.get(deleted=False)

                if customer.email:
                    try:
                        email_content = {'user_name': f"{customer.first_name} {customer.last_name}", 'url': settings.STOREFRONT_URL, 'key': str(key)}
                        email_template = email_templates(template_name='customer_forgot_password', email_content=email_content)

                        send_email(
                            email_subject=f"{store.store_name} Customer Forgot Password",
                            to_email=customer.email,
                            email_template=email_template
                        )

                        customer_invitation.sent = True
                    except Exception as e:
                        print(e)
                        customer_invitation.sent = False

                customer_invitation.save()
                return customer_invitation


class SetPasswordSerializer(serializers.ModelSerializer):
    key = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    class Meta:
        model = Customer
        fields = ('key', 'password', 'confirm_password')

    def create(self, validated_data):
        validated_data = self.initial_data
        if 'key' in validated_data:
            key = validated_data['key']
            password = validated_data['password']
            confirm_password = validated_data['confirm_password']

            customer_forget_password = CustomerForgetPassword.objects.filter(key=key).first()
            if customer_forget_password.expired:
                raise exceptions.ParseError("Forgot link is expired!", code=403)

            if password != confirm_password:
                raise exceptions.ValidationError("password didn't match")

            if len(password) < 8:
                raise exceptions.ValidationError('Password length should be at least 8')

            password = base64.b64encode(password.encode("ascii")).decode("ascii")
            customer = Customer.objects.filter(id=customer_forget_password.customer.id).first()
            customer.password = password
            customer.save()
            customer_forget_password.expired = True
            customer_forget_password.save()

            return validated_data
