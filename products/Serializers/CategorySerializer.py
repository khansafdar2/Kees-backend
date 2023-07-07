
from rest_framework import serializers, exceptions
from products.models import \
    MainCategory, \
    SubCategory, \
    SuperSubCategory, \
    MainCategoryMetaData, \
    SubCategoryMetaData, \
    SuperSubCategoryMetaData, \
    CategoryHandle, \
    Media
from drf_yasg.utils import swagger_serializer_method
from products.Serializers.ProductSerializer import ImagesSerializer
from products.BusinessLogic.RemoveSpecialCharacters import remove_specialcharacters


class MainCategoryMetaDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = MainCategoryMetaData
        fields = ('field', 'value')


class MainCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = MainCategory
        fields = ['id', 'name', 'handle', 'is_active']


class MainCategoryAddUpdateSerializer(serializers.ModelSerializer):
    meta_data = serializers.SerializerMethodField('get_metadata_serializer')
    banner_image = serializers.IntegerField(required=False, allow_null=True)
    thumbnail_image = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = MainCategory
        exclude = ['deleted', 'deleted_at', 'created_at', 'updated_at', 'handle']

    @swagger_serializer_method(serializer_or_field=MainCategoryMetaDataSerializer)
    def get_metadata_serializer(self, obj):
        serializer_context = {'request': self.context.get('request')}
        meta_data = MainCategoryMetaData.objects.all().filter(main_category=obj)
        serializer = MainCategoryMetaDataSerializer(meta_data, many=True, context=serializer_context)
        return serializer.data

    def create(self, validate_data):
        validated_data = self.initial_data
        meta_data = validated_data.pop('meta_data')
        banner_image = validated_data.pop('banner_image', None)
        thumbnail_image = validated_data.pop('thumbnail_image', None)
        alt_text = validated_data.pop('alt_text', None)

        handle_name = remove_specialcharacters(validated_data['name'].replace(' ', '-').lower())
        handle = CategoryHandle.objects.filter(name=handle_name).first()

        if handle is not None:
            handle = CategoryHandle()
            handle_name = handle_name + "-" + str(handle.count)
            handle.name = handle_name
            handle.category_type = 'main_category'
            handle.count = handle.count + 1
            handle.save()
        else:
            handle = CategoryHandle()
            handle.name = handle_name
            handle.category_type = 'main_category'
            handle.count = 1
            handle.save()

        validated_data['handle'] = handle_name
        main_category = MainCategory.objects.create(**validated_data)
        for item in meta_data:
            MainCategoryMetaData.objects.create(main_category=main_category, **item)
        if banner_image is not None:
            Media.objects.filter(id=banner_image).update(main_category=main_category, alt_text=alt_text)
        else:
            try:
                Media.objects.filter(main_category_id=main_category.id).update(main_category=None)
            except Exception as e:
                print(e)
                pass

        if thumbnail_image is not None:
            Media.objects.filter(id=thumbnail_image).update(main_category=main_category, file_name="maincategory_thumbnail_image")

        return main_category

    def update(self, instance, validate_data):
        validated_data = self.initial_data
        meta_data = validated_data.pop('meta_data')
        banner_image = validated_data.pop('banner_image', None)
        thumbnail_image = validated_data.pop('thumbnail_image', None)
        alt_text = validated_data.pop('alt_text', None)

        MainCategory.objects.filter(id=instance.id).update(**validated_data)
        MainCategoryMetaData.objects.filter(main_category_id=instance.id).delete()

        if len(meta_data) > 0:
            for item in meta_data:
                MainCategoryMetaData.objects.create(main_category_id=instance.id, **item)
        if banner_image is not None:
            Media.objects.filter(id=banner_image).update(main_category_id=instance.id, alt_text=alt_text)
        else:
            try:
                Media.objects.filter(main_category_id=instance.id).update(main_category=None)
            except Exception as e:
                print(e)
                pass

        if thumbnail_image is not None:
            Media.objects.filter(id=thumbnail_image).update(main_category=instance, file_name="maincategory_thumbnail_image")

        return instance

    def validate(self, data):
        return data


class MainCategoryDetailSerializer(serializers.ModelSerializer):
    meta_data = serializers.SerializerMethodField('get_meta_data_serializer')
    banner_image = serializers.SerializerMethodField('get_banner_image')
    thumbnail_image = serializers.SerializerMethodField('get_thumbnail_image')

    class Meta:
        model = MainCategory
        exclude = ['deleted', 'deleted_at']

    @swagger_serializer_method(serializer_or_field=MainCategoryMetaDataSerializer)
    def get_meta_data_serializer(self, obj):
        serializer_context = {'request': self.context.get('request')}
        meta_data = MainCategoryMetaData.objects.all().filter(main_category=obj)
        serializer = MainCategoryMetaDataSerializer(meta_data, many=True, context=serializer_context)
        return serializer.data

    @swagger_serializer_method(serializer_or_field=ImagesSerializer)
    def get_banner_image(self, obj):
        serializer_context = {'request': self.context.get('request')}
        banner_image = Media.objects.filter(main_category=obj, deleted=False).first()
        if banner_image is None:
            return None
        serializer = ImagesSerializer(banner_image, context=serializer_context)
        return serializer.data

    @swagger_serializer_method(serializer_or_field=ImagesSerializer)
    def get_thumbnail_image(self, obj):
        serializer_context = {'request': self.context.get('request')}
        banner_image = Media.objects.filter(main_category_id=obj.id, file_name="maincategory_thumbnail_image", deleted=False).first()
        if banner_image is None:
            return None
        serializer = ImagesSerializer(banner_image, context=serializer_context)
        return serializer.data


class SubCategoryMetaDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubCategoryMetaData
        fields = ('field', 'value')


class SubCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'handle', 'is_active', 'main_category']


class SubCategoryAddUpdateSerializer(serializers.ModelSerializer):
    meta_data = serializers.SerializerMethodField('get_metadata_serializer')
    banner_image = serializers.IntegerField(required=False, allow_null=True)
    thumbnail_image = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = SubCategory
        exclude = ['deleted', 'deleted_at', 'created_at', 'updated_at', 'handle']

    @swagger_serializer_method(serializer_or_field=SubCategoryMetaDataSerializer)
    def get_metadata_serializer(self, obj):
        serializer_context = {'request': self.context.get('request')}
        meta_data = SubCategoryMetaData.objects.all().filter(sub_category=obj)
        serializer = SubCategoryMetaDataSerializer(meta_data, many=True, context=serializer_context)
        return serializer.data

    def create(self, validate_data):
        validated_data = self.initial_data
        meta_data = validated_data.pop('meta_data')
        main_category_id = validated_data.pop('main_category')
        banner_image = validated_data.pop('banner_image', None)
        thumbnail_image = validated_data.pop('thumbnail_image', None)
        alt_text = validated_data.pop('alt_text', None)

        handle_name = remove_specialcharacters(validated_data['name'].replace(' ', '-').lower())
        handle = CategoryHandle.objects.filter(name=handle_name).first()

        if handle is not None:
            handle = CategoryHandle()
            handle_name = handle_name + "-" + str(handle.count)
            handle.name = handle_name
            handle.category_type = 'sub_category'
            handle.count = handle.count + 1
            handle.save()
        else:
            handle = CategoryHandle()
            handle.name = handle_name
            handle.category_type = 'sub_category'
            handle.count = 1
            handle.save()

        validated_data['handle'] = handle_name
        sub_category = SubCategory.objects.create(main_category_id=main_category_id, **validated_data)
        for item in meta_data:
            SubCategoryMetaData.objects.create(sub_category=sub_category, **item)
        if banner_image is not None:
            Media.objects.filter(id=banner_image).update(sub_category=sub_category, alt_text=alt_text)
        else:
            try:
                Media.objects.filter(sub_category_id=sub_category.id).update(sub_category=None)
            except Exception as e:
                print(e)
                pass

        if thumbnail_image is not None:
            Media.objects.filter(id=thumbnail_image).update(sub_category=sub_category, file_name="subcategory_thumbnail_image")

        return sub_category

    def update(self, instance, validate_data):
        validated_data = self.initial_data
        meta_data = validated_data.pop('meta_data')
        main_category_id = validated_data.pop('main_category')
        banner_image = validated_data.pop('banner_image', None)
        thumbnail_image = validated_data.pop('thumbnail_image', None)
        alt_text = validated_data.pop('alt_text', None)

        SubCategory.objects.filter(id=instance.id).update(main_category_id=main_category_id, **validated_data)
        SubCategoryMetaData.objects.filter(sub_category_id=instance.id).delete()
        if len(meta_data) > 0:
            for item in meta_data:
                SubCategoryMetaData.objects.create(sub_category_id=instance.id, **item)
        if banner_image is not None:
            Media.objects.filter(id=banner_image).update(sub_category_id=instance.id, alt_text=alt_text)
        else:
            try:
                Media.objects.filter(sub_category_id=instance.id).update(sub_category=None)
            except Exception as e:
                print(e)
                pass

        if thumbnail_image is not None:
            Media.objects.filter(id=thumbnail_image).update(sub_category=instance, file_name="subcategory_thumbnail_image")
        return instance

    def validate(self, data):
        return data


class SubCategoryDetailSerializer(serializers.ModelSerializer):
    meta_data = serializers.SerializerMethodField('get_meta_data_serializer')
    banner_image = serializers.SerializerMethodField('get_banner_image')
    thumbnail_image = serializers.SerializerMethodField('get_thumbnail_image')

    class Meta:
        model = SubCategory
        exclude = ['deleted', 'deleted_at']

    @swagger_serializer_method(serializer_or_field=SubCategoryMetaDataSerializer)
    def get_meta_data_serializer(self, obj):
        serializer_context = {'request': self.context.get('request')}
        meta_data = SubCategoryMetaData.objects.filter(sub_category=obj)
        serializer = SubCategoryMetaDataSerializer(meta_data, many=True, context=serializer_context)
        return serializer.data

    @swagger_serializer_method(serializer_or_field=ImagesSerializer)
    def get_banner_image(self, obj):
        serializer_context = {'request': self.context.get('request')}
        banner_image = Media.objects.filter(sub_category=obj, deleted=False).exclude(file_name="subcategory_thumbnail_image").first()
        if banner_image is None:
            return None
        serializer = ImagesSerializer(banner_image, context=serializer_context)
        return serializer.data

    @swagger_serializer_method(serializer_or_field=ImagesSerializer)
    def get_thumbnail_image(self, obj):
        serializer_context = {'request': self.context.get('request')}
        banner_image = Media.objects.filter(sub_category_id=obj.id, file_name="subcategory_thumbnail_image",
                                            deleted=False).first()
        if banner_image is None:
            return None
        serializer = ImagesSerializer(banner_image, context=serializer_context)
        return serializer.data


class SuperSubCategoryMetaDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = SuperSubCategoryMetaData
        fields = ('field', 'value')


class SuperSubCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = SuperSubCategory
        fields = ['id', 'name', 'handle', 'is_active', 'sub_category']


class SuperSubCategoryAddUpdateSerializer(serializers.ModelSerializer):
    meta_data = serializers.SerializerMethodField('get_metadata_serializer')
    banner_image = serializers.IntegerField(required=False, allow_null=True)
    thumbnail_image = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = SuperSubCategory
        exclude = ['deleted', 'deleted_at', 'created_at', 'updated_at', 'handle']

    @swagger_serializer_method(serializer_or_field=SuperSubCategoryMetaDataSerializer)
    def get_metadata_serializer(self, obj):
        serializer_context = {'request': self.context.get('request')}
        meta_data = SuperSubCategoryMetaData.objects.all().filter(super_sub_category=obj)
        serializer = SuperSubCategoryMetaDataSerializer(meta_data, many=True, context=serializer_context)
        return serializer.data

    def create(self, validate_data):
        validated_data = self.initial_data
        meta_data = validated_data.pop('meta_data')
        sub_category_id = validated_data.pop('sub_category')
        banner_image = validated_data.pop('banner_image', None)
        thumbnail_image = validated_data.pop('thumbnail_image', None)
        alt_text = validated_data.pop('alt_text', None)

        handle_name = remove_specialcharacters(validated_data['name'].replace(' ', '-').lower())
        handle = CategoryHandle.objects.filter(name=handle_name).first()

        if handle is not None:
            handle = CategoryHandle()
            handle_name = handle_name + "-" + str(handle.count)
            handle.name = handle_name
            handle.category_type = 'super_sub_category'
            handle.count = handle.count + 1
            handle.save()
        else:
            handle = CategoryHandle()
            handle.name = handle_name
            handle.category_type = 'super_sub_category'
            handle.count = 1
            handle.save()

        validated_data['handle'] = handle_name
        super_sub_category = SuperSubCategory.objects.create(sub_category_id=sub_category_id, **validated_data)
        for item in meta_data:
            SuperSubCategoryMetaData.objects.create(super_sub_category=super_sub_category, **item)
        if banner_image is not None:
            Media.objects.filter(id=banner_image).update(super_sub_category=super_sub_category, alt_text=alt_text)
        else:
            try:
                Media.objects.filter(super_sub_category_id=super_sub_category.id).update(super_sub_category=None)
            except Exception as e:
                print(e)
                pass

        if thumbnail_image is not None:
            Media.objects.filter(id=thumbnail_image).update(super_sub_category=super_sub_category, file_name="supersubcategory_thumbnail_image")
        return super_sub_category

    def update(self, instance, validate_data):
        validated_data = self.initial_data
        meta_data = validated_data.pop('meta_data')
        sub_category_id = validated_data.pop('sub_category')
        banner_image = validated_data.pop('banner_image', None)
        thumbnail_image = validated_data.pop('thumbnail_image', None)
        alt_text = validated_data.pop('alt_text', None)

        SuperSubCategory.objects.filter(id=instance.id).update(sub_category_id=sub_category_id, **validated_data)
        SuperSubCategoryMetaData.objects.filter(super_sub_category_id=instance.id).delete()
        if len(meta_data) > 0:
            for item in meta_data:
                SuperSubCategoryMetaData.objects.create(super_sub_category_id=instance.id, **item)
        if banner_image is not None:
            Media.objects.filter(id=banner_image).update(super_sub_category_id=instance.id, alt_text=alt_text)
        else:
            try:
                Media.objects.filter(super_sub_category_id=instance.id).update(super_sub_category=None)
            except Exception as e:
                print(e)
                pass

        if thumbnail_image is not None:
            Media.objects.filter(id=thumbnail_image).update(super_sub_category=instance, file_name="supersubcategory_thumbnail_image")
        return instance

    def validate(self, data):
        return data


class SuperSubCategoryDetailSerializer(serializers.ModelSerializer):
    meta_data = serializers.SerializerMethodField('get_meta_data_serializer')
    banner_image = serializers.SerializerMethodField('get_banner_image')
    thumbnail_image = serializers.SerializerMethodField('get_thumbnail_image')

    class Meta:
        model = SuperSubCategory
        exclude = ['deleted', 'deleted_at']

    @swagger_serializer_method(serializer_or_field=SuperSubCategoryMetaDataSerializer)
    def get_meta_data_serializer(self, obj):
        serializer_context = {'request': self.context.get('request')}
        meta_data = SuperSubCategoryMetaData.objects.all().filter(super_sub_category=obj)
        serializer = SuperSubCategoryMetaDataSerializer(meta_data, many=True, context=serializer_context)
        return serializer.data

    @swagger_serializer_method(serializer_or_field=ImagesSerializer)
    def get_banner_image(self, obj):
        serializer_context = {'request': self.context.get('request')}
        banner_image = Media.objects.filter(super_sub_category=obj, deleted=False).first()
        if banner_image is None:
            return None
        serializer = ImagesSerializer(banner_image, context=serializer_context)
        return serializer.data

    @swagger_serializer_method(serializer_or_field=ImagesSerializer)
    def get_thumbnail_image(self, obj):
        serializer_context = {'request': self.context.get('request')}
        banner_image = Media.objects.filter(super_sub_category_id=obj.id, file_name="supersubcategory_thumbnail_image",
                                            deleted=False).first()
        if banner_image is None:
            return None
        serializer = ImagesSerializer(banner_image, context=serializer_context)
        return serializer.data


class MainCategoriesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainCategory
        fields = ('id', 'name')


class SubCategoriesListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = SubCategory
        fields = ('id', 'name')


class SuperSubCategoriesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuperSubCategory
        fields = ('id', 'name')


class CategoryAvailabilityChangeSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    category_type = serializers.CharField(max_length=50, allow_blank=False, allow_null=False)
    is_active = serializers.BooleanField(required=True)

    def create(self, validated_data):
        validated_data = self.initial_data

        if validated_data["category_type"].lower() == "main":
            try:
                MainCategory.objects.filter(id=validated_data['id']).update(is_active=validated_data["is_active"])
            except Exception as e:
                raise exceptions.ParseError(str(e))
            return validated_data
        elif validated_data["category_type"].lower() == "sub":
            try:
                SubCategory.objects.filter(id=validated_data['id']).update(is_active=validated_data["is_active"])
            except Exception as e:
                raise exceptions.ParseError(str(e))
            return validated_data
        elif validated_data["category_type"].lower() == "supersub":
            try:
                SuperSubCategory.objects.filter(id=validated_data['id']).update(is_active=validated_data["is_active"])
            except Exception as e:
                raise exceptions.ParseError(str(e))
            return validated_data
        raise exceptions.ParseError("Invalid 'category_type'. Category Type can be main, sub or supersub")



