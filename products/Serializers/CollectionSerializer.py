
from rest_framework import serializers, exceptions
from products.Serializers.ProductSerializer import ImagesSerializer
from products.models import Collection, CollectionMetaData, Product, CollectionHandle, Media
from drf_yasg.utils import swagger_serializer_method
from products.BusinessLogic.RemoveSpecialCharacters import remove_specialcharacters
from vendor.BussinessLogic.AddApproval import add_approval_entry
from vendor.models import DataApproval


class CollectionListSerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()
    vendor_name = serializers.CharField(source='vendor.name')

    class Meta:
        model = Collection
        fields = ('id', 'title', 'product_count', 'vendor_name', 'is_active', 'status', 'seo_title', 'seo_description','seo_keywords')

    def get_product_count(self, obj):
        return Product.objects.filter(collection=obj, deleted=False).count()


class CollectionMetaDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionMetaData
        fields = ('field', 'value')


class CollectionDetailSerializer(serializers.ModelSerializer):
    meta_data = serializers.SerializerMethodField('get_meta_data_serializer')
    banner_image = serializers.SerializerMethodField('get_banner_image')
    reason = serializers.SerializerMethodField('get_reason')

    class Meta:
        model = Collection
        exclude = ['deleted', 'deleted_at']

    @swagger_serializer_method(serializer_or_field=CollectionMetaDataSerializer(many=True))
    def get_meta_data_serializer(self, obj):
        serializer_context = {'request': self.context.get('request')}
        rules_data = CollectionMetaData.objects.all().filter(collection=obj)
        serializer = CollectionMetaDataSerializer(rules_data, many=True, context=serializer_context)
        return serializer.data

    @swagger_serializer_method(serializer_or_field=ImagesSerializer)
    def get_banner_image(self, obj):
        serializer_context = {'request': self.context.get('request')}
        banner_image = Media.objects.filter(collection=obj, deleted=False).first()
        if banner_image is None:
            return None
        serializer = ImagesSerializer(banner_image, context=serializer_context)
        return serializer.data

    def get_reason(self, obj):
        data = DataApproval.objects.filter(content_type__model='collection', status='Disapproved', object_id=obj.id, deleted=False).first()
        if data:
            reason = data.reason
        else:
            reason = None
        return reason


class CollectionAddSerializer(serializers.ModelSerializer):
    meta_data = serializers.SerializerMethodField('get_meta_data_serializer')
    banner_image = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Collection
        exclude = ['deleted', 'deleted_at', 'created_at', 'updated_at', 'collection_type', 'handle']

    @swagger_serializer_method(serializer_or_field=CollectionMetaDataSerializer)
    def get_meta_data_serializer(self, obj):
        serializer_context = {'request': self.context.get('request')}
        rules_data = CollectionMetaData.objects.all().filter(collection=obj)
        serializer = CollectionMetaDataSerializer(rules_data, many=True, context=serializer_context)
        return serializer.data

    def create(self, validate_data):
        try:
            validated_data = self.initial_data
            meta_data = validated_data.pop('meta_data')
            vendor = validated_data.pop('vendor')
            main_category = validated_data.pop('main_category', None)
            sub_category = validated_data.pop('sub_category', None)
            super_sub_category = validated_data.pop('super_sub_category', None)
            banner_image = validated_data.pop('banner_image', None)
            handle_name = remove_specialcharacters(validated_data['title'].replace(' ', '-').lower())
            handle = CollectionHandle.objects.filter(name=handle_name).first()
            if handle is not None:
                handle_name = handle_name + "-" + str(handle.count)
                handle.count = handle.count + 1
                handle.save()
            else:
                handle = CollectionHandle()
                handle.name = handle_name
                handle.count = 1
                handle.save()
            validated_data['handle'] = handle_name
            collection = Collection.objects.create(vendor_id=vendor, **validated_data)
            if len(main_category) > 0 or main_category is not None:
                collection.main_category.set(main_category)
            if len(sub_category) > 0 or sub_category is not None:
                collection.sub_category.set(sub_category)
            if len(super_sub_category) > 0 or super_sub_category is not None:
                collection.super_sub_category.set(super_sub_category)
            for item in meta_data:
                CollectionMetaData.objects.create(collection=collection, **item)
            if banner_image is not None:
                Media.objects.filter(id=banner_image).update(collection=collection)
            else:
                try:
                    Media.objects.filter(collection_id=collection.id).update(collection=None)
                except Exception as e:
                    print(e)
                    pass

            # approval entry
            add_approval_entry(title=collection.title,
                               vendor=collection.vendor,
                               instance=collection,
                               )

            return collection
        except Exception as e:
            print(e)
            raise Exception(str(e))

    def update(self, instance, validate_data):
        try:
            validated_data = self.initial_data
            meta_data = validated_data.pop('meta_data')
            vendor = validated_data.pop('vendor')
            main_category = validated_data.pop('main_category', None)
            sub_category = validated_data.pop('sub_category', None)
            super_sub_category = validated_data.pop('super_sub_category', None)
            banner_image = validated_data.pop('banner_image', None)
            Collection.objects.filter(id=instance.id).update(vendor=vendor, **validated_data)
            CollectionMetaData.objects.filter(collection_id=instance.id).delete()
            if len(meta_data) > 0:
                for item in meta_data:
                    CollectionMetaData.objects.create(collection_id=instance.id, **item)

            collection = Collection.objects.get(id=instance.id)
            collection.main_category.clear()
            collection.sub_category.clear()
            collection.super_sub_category.clear()
            collection.main_category.set(main_category)
            collection.sub_category.set(sub_category)
            collection.super_sub_category.set(super_sub_category)
            if banner_image is not None:
                Media.objects.filter(id=banner_image).update(collection=collection)
            else:
                try:
                    Media.objects.filter(collection_id=collection.id).update(collection=None)
                except Exception as e:
                    pass

            # approval entry
            add_approval_entry(title=collection.title,
                               vendor=collection.vendor,
                               instance=collection,
                               )
            return instance

        except Exception as e:
            print(e)
            raise Exception(str(e))

    def validate(self, data):
        return data


class DeleteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = Collection
        fields = ('id',)


class CollectionStatusChangeSerializer(serializers.ModelSerializer):
    ids = serializers.ListField(read_only=True)
    status = serializers.CharField(max_length=50, allow_blank=False, allow_null=False, read_only=True)
    value = serializers.BooleanField(default=False, read_only=True)

    class Meta:
        model = Collection
        fields = ('ids', 'status', 'value')

    def create(self, validated_data):
        validated_data = self.initial_data
        user = validated_data['user']

        if validated_data["status"] == "approved":
            try:
                Collection.objects.filter(id__in=validated_data['ids']).update(status=validated_data["value"])
            except Exception as e:
                raise exceptions.ParseError(str(e))
            return validated_data
        elif validated_data["status"] == "active":
            try:
                if user.is_vendor:
                    Collection.objects.filter(id__in=validated_data['ids'], vendor_id=user.vendor_id).update(is_active=validated_data["value"])
                else:
                    Collection.objects.filter(id__in=validated_data['ids']).update(is_active=validated_data["value"])
            except Exception as e:
                raise exceptions.ParseError(str(e))
            return validated_data
        raise exceptions.ParseError("Status can be approved or active")








