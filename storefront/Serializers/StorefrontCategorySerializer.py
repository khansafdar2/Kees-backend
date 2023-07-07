
from rest_framework import serializers
from products.models import MainCategory, SubCategory, SuperSubCategory, Media
from drf_yasg.utils import swagger_serializer_method


class SuperSubCategoriesListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = SuperSubCategory
        fields = ('id', 'name', 'handle','slug', 'seo_title', 'seo_description','seo_keywords')


class SubCategoriesListSerializer(serializers.ModelSerializer):
    super_sub_category = serializers.SerializerMethodField('get_supersubcategory_serializer')

    class Meta:
        model = SubCategory
        fields = ('id', 'name', 'handle', 'super_sub_category', 'slug', 'seo_title', 'seo_description','seo_keywords')

    @swagger_serializer_method(serializer_or_field=SuperSubCategoriesListSerializer(many=True))
    def get_supersubcategory_serializer(self, obj):
        serializer_context = {'request': self.context.get('request')}
        super_sub_category = SuperSubCategory.objects.filter(sub_category=obj, is_active=True, deleted=False)
        serializer = SuperSubCategoriesListSerializer(super_sub_category, many=True, context=serializer_context)
        return serializer.data


class CategoriesListSerializer(serializers.ModelSerializer):
    sub_category = serializers.SerializerMethodField('get_subcategory_serializer')

    class Meta:
        model = MainCategory
        fields = ('id', 'name', 'handle', 'position', 'sub_category', 'slug', 'seo_title', 'seo_description','seo_keywords')

    @swagger_serializer_method(serializer_or_field=SubCategoriesListSerializer(many=True))
    def get_subcategory_serializer(self, obj):
        serializer_context = {'request': self.context.get('request')}
        sub_category = SubCategory.objects.filter(main_category=obj, is_active=True, deleted=False)
        serializer = SubCategoriesListSerializer(sub_category, many=True, context=serializer_context)
        return serializer.data


class ImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ('id', 'file_name', 'file_path', 'cdn_link')


class SubCategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField('get_subcategory_image')

    class Meta:
        model = SubCategory
        fields = ('id', 'name', 'handle', 'image','slug', 'seo_title', 'seo_description','seo_keywords')

    def get_subcategory_image(self, obj):
        serializer_context = {'request': self.context.get('request')}
        sub_category = Media.objects.filter(sub_category=obj).first()
        serializer = ImagesSerializer(sub_category, context=serializer_context)
        return serializer.data


class MainSubCategoriesSerializer(serializers.ModelSerializer):
    sub_category = serializers.SerializerMethodField('get_subcategory_serializer')
    banner_image = serializers.SerializerMethodField('get_banner_image')

    class Meta:
        model = MainCategory
        fields = ('id', 'name', 'banner_image', 'sub_category','slug', 'seo_title', 'seo_description','seo_keywords')

    def get_subcategory_serializer(self, obj):
        serializer_context = {'request': self.context.get('request')}
        sub_category = SubCategory.objects.filter(main_category=obj, is_active=True, deleted=False)
        serializer = SubCategorySerializer(sub_category, many=True, context=serializer_context)
        return serializer.data

    @swagger_serializer_method(serializer_or_field=ImagesSerializer)
    def get_banner_image(self, obj):
        serializer_context = {'request': self.context.get('request')}
        banner_image = Media.objects.filter(main_category=obj, deleted=False).first()
        if banner_image is None:
            return None
        serializer = ImagesSerializer(banner_image, context=serializer_context)
        return serializer.data
