from datetime import datetime
import random

from rest_framework import serializers, exceptions
from crm.models import Customer, Address, Wallet
from drf_yasg.utils import swagger_serializer_method
from rest_framework.validators import UniqueValidator


class CustomerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('id', 'first_name', 'last_name', 'phone', 'email', 'notes',)


class AddressSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Address
        exclude = ['customer', 'deleted', 'deleted_at', 'created_at', 'updated_at']


class CustomerDetailSerializer(serializers.ModelSerializer):
    address = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        exclude = ('deleted', 'deleted_at',)

    @swagger_serializer_method(serializer_or_field=AddressSerializer)
    def get_address(self, obj):
        serializer_context = {'request': self.context.get('request')}
        address = Address.objects.filter(customer=obj, deleted=False)
        serializer = AddressSerializer(address, many=True, context=serializer_context)
        return serializer.data


class CustomerAddSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[UniqueValidator(queryset=Customer.objects.all())])
    address = serializers.SerializerMethodField('get_address_serializer')

    class Meta:
        model = Customer
        fields = ('id', 'first_name', 'last_name', 'phone', 'email', 'notes', 'address')

    @swagger_serializer_method(serializer_or_field=AddressSerializer)
    def get_address_serializer(self, obj):
        serializer_context = {'request': self.context.get('request')}
        address = Address.objects.all().filter(customer=obj, deleted=False)
        serializer = AddressSerializer(address, many=True, context=serializer_context)
        return serializer.data

    def create(self, validated_data):
        validated_data = self.initial_data
        address_data = validated_data.pop('address')
        customer = Customer.objects.create(**validated_data)
        for address in address_data:
            Address.objects.create(customer=customer, **address)
        current_date = datetime.now()
        unique_id = (str(random.randint(1000, 1000000)) + '-' + current_date.strftime("%Y-%m-%dT%H-%M-%S")).\
            replace('-', '')
        Wallet.objects.create(customer=customer, unique_id=unique_id)

        return customer

    def update(self, instance, validated_data):
        validated_data = self.initial_data
        address_data = validated_data.pop('address')
        Customer.objects.filter(id=instance.id).update(**validated_data)
        for address in address_data:
            address_id = address.get('id', None)
            if address_id is not None:
                Address.objects.filter(id=address_id).update(**address)
            else:
                Address.objects.create(customer_id=instance.id, **address)
        return instance


class CustomerDeleteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = Customer
        fields = ('id',)


class CustomerStatusChangeSerializer(serializers.ModelSerializer):
    ids = serializers.ListField(required=True)
    status = serializers.CharField(max_length=50, allow_blank=False, allow_null=False)
    value = serializers.BooleanField(default=False)

    class Meta:
        model = Customer
        fields = ('ids', 'status', 'value',)

    def create(self, validated_data):
        validated_data = self.initial_data
        if validated_data["status"] == "approved":
            try:
                Customer.objects.filter(id__in=validated_data['ids']).update(is_approved=validated_data["value"])
            except Exception as e:
                raise exceptions.ParseError(str(e))
            return validated_data
        elif validated_data["status"] == "active":
            try:
                Customer.objects.filter(id__in=validated_data['ids']).update(is_approved=validated_data["value"])
            except Exception as e:
                raise exceptions.ParseError(str(e))
            return validated_data
        raise exceptions.ParseError("Status can be approved or active")
