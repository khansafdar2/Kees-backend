from rest_framework import serializers, exceptions

from products.BusinessLogic.CategoriesAsTagsLogic import CategoriesAsTagsLogic
from products.BusinessLogic.ElasticSearch import ElasticSearch
from products.BusinessLogic.InventoryTrack import AddInventoryEvent
from products.models import Product, Variant, Option, Media, Feature, ProductHandle, ProductGroup, Tags
from setting.models import StoreInformation
from products.BusinessLogic.RemoveSpecialCharacters import remove_specialcharacters
from products.Views.Variants import CreateDefaultVariant
from drf_yasg.utils import swagger_serializer_method
from django.db import transaction
from datetime import datetime
from products.BusinessLogic.HideOutOfStock import hide_stock
from vendor.BussinessLogic.AddApproval import add_approval_entry
from vendor.models import Vendor, DataApproval
from rest_framework.response import Response


class AddVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        exclude = ['deleted', 'deleted_at', 'product', 'old_inventory_quantity', 'weight_unit']


class GetVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        exclude = ['deleted', 'deleted_at', 'product']


class AddOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        exclude = ['deleted', 'deleted_at', 'product']


class ImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        exclude = ['deleted', 'deleted_at', 'product']


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        exclude = ['deleted', 'deleted_at', 'product']


class ProductDetailSerializer(serializers.ModelSerializer):
    variants = serializers.SerializerMethodField('get_variants')
    options = serializers.SerializerMethodField('get_options')
    images = serializers.SerializerMethodField('get_images')
    features = serializers.SerializerMethodField('get_features')
    tags = serializers.SerializerMethodField('get_tags')
    reason = serializers.SerializerMethodField('get_reason')

    class Meta:
        model = Product
        exclude = ['deleted', 'deleted_at']

    @swagger_serializer_method(serializer_or_field=GetVariantSerializer)
    def get_variants(self, obj):
        serializer_context = {'request': self.context.get('request')}
        variants_data = Variant.objects.filter(product=obj, deleted=False)
        serializer = GetVariantSerializer(variants_data, many=True, context=serializer_context)
        return serializer.data

    @swagger_serializer_method(serializer_or_field=AddOptionsSerializer)
    def get_options(self, obj):
        serializer_context = {'request': self.context.get('request')}
        options_data = Option.objects.filter(product=obj, deleted=False).order_by('-id').reverse()
        serializer = AddOptionsSerializer(options_data, many=True, context=serializer_context)
        return serializer.data

    @swagger_serializer_method(serializer_or_field=ImagesSerializer)
    def get_images(self, obj):
        serializer_context = {'request': self.context.get('request')}
        images_data = Media.objects.filter(product=obj, deleted=False).order_by('position')
        serializer = ImagesSerializer(images_data, many=True, context=serializer_context)
        return serializer.data

    @swagger_serializer_method(serializer_or_field=FeatureSerializer)
    def get_features(self, obj):
        serializer_context = {'request': self.context.get('request')}
        images_data = Feature.objects.filter(product=obj, deleted=False)
        serializer = FeatureSerializer(images_data, many=True, context=serializer_context)
        return serializer.data

    def get_reason(self, obj):
        data = DataApproval.objects.filter(content_type__model='product', status='Disapproved', object_id=obj.id,
                                           deleted=False).first()
        if data:
            reason = data.reason
        else:
            reason = None
        return reason

    def get_tags(self, obj):
        tags = Tags.objects.filter(product_tags=obj, is_option=False).values_list('name', flat=True)
        tags = ','.join(tags)
        return tags


class ProductListSerializer(serializers.ModelSerializer):
    product_type_name = serializers.CharField(source='product_type.name', read_only=True, allow_null=True,
                                              allow_blank=True)
    vendor_name = serializers.CharField(source='vendor.name', read_only=True, allow_null=True, allow_blank=True)
    inventory = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'title', 'is_active', 'vendor_name', 'product_type_name', 'inventory', 'image', 'status')

    def get_inventory(self, obj):
        variants = Variant.objects.filter(product=obj, deleted=False)
        count = len(variants)
        qty = 0
        for variant in variants:
            qty = variant.inventory_quantity + qty
        if count == 1:
            return str(qty) + " in stock for " + str(count) + " variant"
        return str(qty) + " in stock for " + str(count) + " variants"

    def get_image(self, obj):
        image = Media.objects.filter(product=obj, position=1).first()
        if image is not None:
            return image.cdn_link
        else:
            return None


class AddProductSerializer(serializers.ModelSerializer):
    variants = serializers.SerializerMethodField('get_variants')
    options = serializers.SerializerMethodField('get_options')
    features = serializers.SerializerMethodField('get_features')
    product_images = serializers.ListField(required=False)

    class Meta:
        model = Product
        exclude = ['deleted', 'deleted_at', 'handle', 'vendor', 'tag']

    @swagger_serializer_method(serializer_or_field=AddVariantSerializer)
    def get_variants(self, obj):
        serializer_context = {'request': self.context.get('request')}
        variants_data = Variant.objects.filter(product=obj, deleted=False)
        serializer = AddVariantSerializer(variants_data, many=True, context=serializer_context)
        return serializer.data

    @swagger_serializer_method(serializer_or_field=AddOptionsSerializer)
    def get_options(self, obj):
        serializer_context = {'request': self.context.get('request')}
        options_data = Option.objects.filter(product=obj)
        serializer = AddOptionsSerializer(options_data, many=True, context=serializer_context)
        return serializer.data

    @swagger_serializer_method(serializer_or_field=FeatureSerializer)
    def get_features(self, obj):
        serializer_context = {'request': self.context.get('request')}
        features_data = Feature.objects.filter(product=obj)
        serializer = FeatureSerializer(features_data, many=True, context=serializer_context)
        return serializer.data

    @transaction.atomic
    def create(self, validated_data):
        try:
            try:
                store = StoreInformation.objects.get(deleted=False)
            except Exception as e:
                print(e)
                raise exceptions.ParseError("Store Information is missing! Please configure your store settings "
                                            "before creating products!")
            validated_data = self.initial_data
            user = validated_data.pop('user')
            collection = validated_data.pop('collection')
            variants = validated_data.pop('variants')
            vendor = validated_data.pop('vendor')
            options = validated_data.pop('options')
            features = validated_data.pop('features')
            tags = validated_data.pop('tags', None)
            product_images = validated_data.pop('product_images')
            commission = validated_data.pop('commission', None)
            product_group = validated_data.pop('product_group', None)
            product_brand = validated_data.pop('product_brand', None)

            # Save Unique Product Handle
            handle_name = remove_specialcharacters(validated_data['title'].replace(' ', '-').lower())
            handle = ProductHandle.objects.filter(name=handle_name).first()
            if handle is not None:
                handle_name = handle_name + "-" + str(handle.count)
                handle.count = handle.count + 1
                handle.save()
            else:
                handle = ProductHandle()
                handle.name = handle_name
                handle.count = 1
                handle.save()
            validated_data['handle'] = handle_name

            if not product_group:
                validated_data['is_active'] = False

            product = Product.objects.create(
                vendor_id=vendor,
                commission_id=commission,
                product_group_id=product_group,
                product_brand_id=product_brand,
                **validated_data)

            elastic_search = ElasticSearch()
            elastic_search.insert_or_update(product)

            for item in variants:
                if item['is_physical']:
                    if item['weight'] == 0:
                        raise exceptions.ParseError("physical product weight cannot be null")
                else:
                    item['weight'] = 0

                if item['compare_at_price'] is None:
                    item['compare_at_price'] = item['price']
                else:
                    if float(item['compare_at_price']) < float(item['price']):
                        item['compare_at_price'] = item['price']

                item['weight_unit'] = store.weight_units
                item['old_inventory_quantity'] = 0
                variant = Variant.objects.create(product=product, **item)
                if validated_data['track_inventory']:
                    AddInventoryEvent(
                        variant=variant,
                        user=user,
                        event="Initial Inventory",
                        quantity=variant.inventory_quantity,
                        new_inventory=variant.inventory_quantity,
                        old_inventory=0)

            for item in options:
                Option.objects.create(product=product, **item)
            for item in features:
                Feature.objects.create(product=product, **item)
            for count, item in enumerate(product_images, 1):
                Media.objects.filter(id=item).update(product=product, position=count)
            product.collection.set(collection)

            tags_list = []
            if tags is not None:
                bl = CategoriesAsTagsLogic()
                tags = tags.split(',')
                tags = tags + bl.get_tags(product)
                for tag_name in tags:
                    tag = Tags.objects.filter(name__iexact=tag_name, is_option=False).first()
                    if not tag:
                        tag = Tags.objects.create(name=tag_name)
                    tags_list.append(tag.id)

            for option in options:
                values = option['values']
                values = values.split(',')
                for value in values:
                    tag = Tags.objects.filter(name__iexact=value, is_option=True).first()
                    if not tag:
                        tag = Tags.objects.create(name=value, is_option=True)
                    tags_list.append(tag.id)

            product.tag.set(tags_list)

            # approval entry
            add_approval_entry(title=product.title,
                               vendor=product.vendor,
                               instance=product,
                               )

            # check hide out of stock
            hide_stock(product)
            return product
        except Exception as e:
            print(e)
            raise Exception(str(e))


class UpdateProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)
    features = serializers.SerializerMethodField('get_features')
    options = serializers.SerializerMethodField('get_options')
    variants = serializers.SerializerMethodField('get_variants')

    @swagger_serializer_method(serializer_or_field=FeatureSerializer)
    def get_features(self, obj):
        serializer_context = {'request': self.context.get('request')}
        features_data = Feature.objects.filter(product=obj)
        serializer = FeatureSerializer(features_data, many=True, context=serializer_context)
        return serializer.data

    @swagger_serializer_method(serializer_or_field=AddOptionsSerializer)
    def get_options(self, obj):
        serializer_context = {'request': self.context.get('request')}
        options_data = Option.objects.filter(product=obj)
        serializer = AddOptionsSerializer(options_data, many=True, context=serializer_context)
        return serializer.data

    @swagger_serializer_method(serializer_or_field=AddVariantSerializer)
    def get_variants(self, obj):
        serializer_context = {'request': self.context.get('request')}
        variants_data = Variant.objects.filter(product=obj, deleted=False)
        serializer = AddVariantSerializer(variants_data, many=True, context=serializer_context)
        return serializer.data

    class Meta:
        model = Product
        exclude = ['deleted', 'deleted_at', 'handle', 'vendor', 'tag']

    @transaction.atomic
    def update(self, instance, validate_data):
        try:
            try:
                store = StoreInformation.objects.get(deleted=False)
            except Exception as e:
                print(e)
                raise exceptions.ParseError("Store Information is missing! Please configure your store settings "
                                            "before updating products!")
            validated_data = self.initial_data
            user = validated_data.pop('user')
            collection = validated_data.pop('collection')
            vendor = validated_data.pop('vendor')
            commission = validated_data.pop('commission', None)
            product_group = validated_data.pop('product_group', None)
            features = validated_data.pop('features')
            options = validated_data.pop('options')
            variants = validated_data.pop('variants')
            tags = validated_data.pop('tags', None)
            deleted_variants_id = validated_data.pop('deleted_variants_id', None)
            product_brand = validated_data.pop('product_brand', None)
            product_images = validated_data.pop('product_images')
            deleted_product_images = validated_data.pop('deleted_product_images')

            if not product_group:
                validated_data['is_active'] = False

            Product.objects.filter(id=instance.id).update(
                vendor_id=vendor,
                commission_id=commission,
                product_group_id=product_group,
                product_brand_id=product_brand,
                **validated_data)

            product = Product.objects.get(id=instance.id)

            title = validated_data.get('title')
            is_active = validated_data.get('is_active')
            status = validated_data.get('status')

            check = False
            if title is not None:
                if instance.title != title:
                    check = True
            if is_active is not None:
                if instance.is_active != is_active:
                    check = True
            if status is not None:
                if instance.status != status:
                    check = True

            if check:
                elastic_search = ElasticSearch()
                elastic_search.insert_or_update(product)

            product.collection.set(collection)
            Feature.objects.filter(product=product).delete()
            for item in features:
                Feature.objects.create(product=product, **item)
            product.tag.clear()
            Option.objects.filter(product=product).delete()
            for item in options:
                item.pop('new', None)
                Option.objects.create(product=product, **item)

            for item in variants:
                if item['is_physical']:
                    if item['weight'] == 0:
                        raise exceptions.ParseError("physical product weight cannot be null")
                else:
                    item['weight'] = 0

                if item['compare_at_price'] is None:
                    item['compare_at_price'] = item['price']
                else:
                    if float(item['compare_at_price']) < float(item['price']):
                        item['compare_at_price'] = item['price']

                if "id" in item:
                    Variant.objects.filter(id=item['id']).update(product=product, **item)
                else:
                    item['weight_unit'] = store.weight_units
                    item['old_inventory_quantity'] = 0
                    variant = Variant.objects.create(product=product, **item)
                    if validated_data['track_inventory']:
                        AddInventoryEvent(
                            variant=variant,
                            user=user,
                            event="Initial Inventory",
                            quantity=variant.inventory_quantity,
                            new_inventory=variant.inventory_quantity,
                            old_inventory=0)

            if len(deleted_variants_id) > 0:
                variants = Variant.objects.filter(product_id=product.id, deleted=False)
                if len(variants) == len(deleted_variants_id):
                    first_variant = variants.first()
                    CreateDefaultVariant(first_variant, product.id)
                    product.has_variants = False
                    product.save()
                variants.filter(id__in=deleted_variants_id).update(deleted=True, sku=None, deleted_at=datetime.now(),
                                                                   product=None, legacy_product=product.id)
            Media.objects.filter(id__in=deleted_product_images).update(product=None)
            for count, item in enumerate(product_images, 1):
                Media.objects.filter(id=item).update(product=product, position=count)

            tags_list = []
            if tags is not None:
                bl = CategoriesAsTagsLogic()
                tags = tags.split(',')
                tags = tags + bl.get_tags(product)
                for tag_name in tags:
                    tag = Tags.objects.filter(name__iexact=tag_name, is_option=False).first()
                    if not tag:
                        tag = Tags.objects.create(name=tag_name)
                    tags_list.append(tag.id)

            for option in options:
                values = option['values']
                values = values.split(',')
                for value in values:
                    tag = Tags.objects.filter(name__iexact=value, is_option=True).first()
                    if not tag:
                        tag = Tags.objects.create(name=value, is_option=True)
                    tags_list.append(tag.id)
            product.tag.set(tags_list)

            # approval entry
            add_approval_entry(title=product.title,
                               vendor=product.vendor,
                               instance=product,
                               )

            # hide out of stock
            hide_stock(product)
            return product
        except Exception as e:
            print(e)
            raise Exception(str(e))


class ProductDeleteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = Product
        fields = ('id',)


class ProductStatusChangeSerializer(serializers.ModelSerializer):
    ids = serializers.ListField(required=True)
    status = serializers.CharField(max_length=50, allow_blank=False, allow_null=False)
    value = serializers.BooleanField(default=False)

    class Meta:
        model = Product
        fields = ('ids', 'status', 'value')

    def create(self, validated_data):
        validated_data = self.initial_data
        user = validated_data['user']

        if validated_data["status"] == "approved":
            try:
                Product.objects.filter(id__in=validated_data['ids']).update(status=validated_data["value"])
            except Exception as e:
                raise exceptions.ParseError(str(e))

        elif validated_data["status"] == "active":
            try:
                if user.is_vendor:
                    Product.objects.filter(id__in=validated_data['ids'], vendor_id=user.vendor_id,
                                           product_group__isnull=False).update(is_active=validated_data["value"])
                else:
                    Product.objects.filter(id__in=validated_data['ids'], product_group__isnull=False).update(
                        is_active=validated_data["value"])

            except Exception as e:
                raise exceptions.ParseError(str(e))

        else:
            raise exceptions.ParseError("Status can be approved or active")

        elastic_search = ElasticSearch()
        obj = Product.objects.filter(id__in=validated_data['ids'])
        elastic_search.bulk_insert_or_update(obj)

        return validated_data




class ProductBulkOrganizeSerializer(serializers.ModelSerializer):
    ids = serializers.ListField(required=True)
    product_group = serializers.CharField(max_length=50, allow_blank=True, allow_null=True, required=False)
    collections = serializers.ListField(required=False)

    class Meta:
        model = Product
        fields = ('ids', 'collections', 'product_group')

    def create(self, validated_data):
        validated_data = self.initial_data

        if "vendor" not in validated_data or validated_data['vendor'] is None or len(
                str(validated_data['vendor'])) == 0:
            if "brand" in validated_data and validated_data['brand'] is not None:
                try:
                    Product.objects.filter(id__in=validated_data['ids'], deleted=False).update(
                        product_brand_id=validated_data['brand'])
                except Exception as e:
                    raise exceptions.ParseError(str(e))

        if "vendor" in validated_data and validated_data['vendor'] is not None:
            vendor = Vendor.objects.filter(id=validated_data['vendor'], deleted=False).first()

            for product_id in validated_data['ids']:
                product = Product.objects.filter(id=product_id, deleted=False).first()

                if product.vendor != vendor:
                    try:
                        product.product_group = None
                        product.brand = None
                        product.collection.remove(*product.collection.all())
                        product.vendor = vendor
                        product.save()
                    except Exception as e:
                        raise exceptions.ParseError(str(e))

                if "product_group" in validated_data and validated_data['product_group'] is not None and len(
                        validated_data['product_group']) > 0:
                    try:
                        product.product_group_id = validated_data["product_group"]
                        product.save()
                    except Exception as e:
                        raise exceptions.ParseError(str(e))

                if "brand" in validated_data and validated_data['brand'] is not None and len(
                        validated_data['brand']) > 0:
                    try:
                        product.brand_id = validated_data["brand"]
                        product.save()
                    except Exception as e:
                        raise exceptions.ParseError(str(e))

                if validated_data["collections"]:
                    try:
                        if validated_data["collection_type"] == 'replace':
                            product.collection.remove(*product.collection.all())
                            product.collection.set(validated_data["collections"])
                        elif validated_data["collection_type"] == 'append':
                            for i in validated_data["collections"]:
                                product.collection.add(i)
                    except Exception as e:
                        raise exceptions.ParseError(str(e))

        return Response({"Success": "Data updated Successfully"})


class ProductBulkTagsSerializer(serializers.ModelSerializer):
    ids = serializers.ListField(required=True)
    status = serializers.CharField(max_length=50, allow_blank=False, allow_null=False)
    value = serializers.CharField(max_length=50, allow_blank=False, allow_null=False)

    class Meta:
        model = Product
        fields = ('ids', 'status', 'value')

    def create(self, validated_data):
        validated_data = self.initial_data
        user = validated_data['user']

        tags_list = []
        if validated_data["value"] is not None:
            tags = validated_data["value"].split(',')
            for tag_name in tags:
                tag = Tags.objects.filter(name__iexact=tag_name, is_option=False).first()
                if not tag:
                    tag = Tags.objects.create(name=tag_name)
                tags_list.append(tag.id)

        if validated_data["status"] == "replace":
            try:
                if user.is_vendor:
                    products = Product.objects.filter(id__in=validated_data['ids'], vendor_id=user.vendor_id)
                else:
                    products = Product.objects.filter(id__in=validated_data['ids'])

                for product in products:
                    product.tag.set(tags_list)

                return validated_data
            except Exception as e:
                raise exceptions.ParseError(str(e))

        elif validated_data["status"] == "append":
            try:
                if user.is_vendor:
                    products = Product.objects.filter(id__in=validated_data['ids'], vendor_id=user.vendor_id)
                else:
                    products = Product.objects.filter(id__in=validated_data['ids'])

                for product in products:
                    for tag in tags_list:
                        product.tag.add(tag)

            except Exception as e:
                raise exceptions.ParseError(str(e))
            return validated_data
        raise exceptions.ParseError("Status can be append or replace")
