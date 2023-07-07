
from rest_framework import serializers
from crm.models import Customer, Address
from order.models import Order, ChildOrder
from products.models import Product, Variant, Option, Media, Feature


class GetVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = '__all__'


class AddOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = '__all__'


class ImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = '__all__'


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = '__all__'


class ProductListSerializer(serializers.ModelSerializer):
    variants = serializers.SerializerMethodField('get_variants')
    options = serializers.SerializerMethodField('get_options')
    images = serializers.SerializerMethodField('get_images')
    features = serializers.SerializerMethodField('get_features')

    class Meta:
        model = Product
        fields = '__all__'
        depth = 3

    def get_variants(self, obj):
        serializer_context = {'request': self.context.get('request')}
        variants_data = Variant.objects.filter(product=obj, deleted=False)
        serializer = GetVariantSerializer(variants_data, many=True, context=serializer_context)
        return serializer.data

    def get_options(self, obj):
        serializer_context = {'request': self.context.get('request')}
        options_data = Option.objects.filter(product=obj, deleted=False).order_by('-id').reverse()
        serializer = AddOptionsSerializer(options_data, many=True, context=serializer_context)
        return serializer.data

    def get_images(self, obj):
        serializer_context = {'request': self.context.get('request')}
        images_data = Media.objects.filter(product=obj, deleted=False).order_by('position')
        serializer = ImagesSerializer(images_data, many=True, context=serializer_context)
        return serializer.data

    def get_features(self, obj):
        serializer_context = {'request': self.context.get('request')}
        images_data = Feature.objects.filter(product=obj, deleted=False)
        serializer = FeatureSerializer(images_data, many=True, context=serializer_context)
        return serializer.data


class ChildOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChildOrder
        fields = '__all__'


class ParentOrderListSerializer(serializers.ModelSerializer):
    child_orders = serializers.SerializerMethodField('get_childorder')

    class Meta:
        model = Order
        fields = '__all__'
        depth = 3

    def get_childorder(self, obj):
        serializer_context = {'request': self.context.get('request')}
        child_orders = ChildOrder.objects.filter(order=obj)
        if child_orders:
            serializer = ChildOrderSerializer(child_orders, many=True, context=serializer_context)
            return serializer.data
        data = []
        return data


class AddressSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Address
        fields = '__all__'


class CustomerListSerializer(serializers.ModelSerializer):
    address = serializers.SerializerMethodField('get_address')

    class Meta:
        model = Customer
        fields = '__all__'

    def get_address(self, obj):
        serializer_context = {'request': self.context.get('request')}
        address = Address.objects.all().filter(customer=obj, deleted=False)
        serializer = AddressSerializer(address, many=True, context=serializer_context)
        return serializer.data
