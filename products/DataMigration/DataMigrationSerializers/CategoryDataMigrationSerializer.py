
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


class MainCategoryMigrateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainCategory
        exclude = ['deleted', 'deleted_at', 'created_at', 'updated_at', 'handle']

    def create(self, validate_data):
        validated_data = self.initial_data

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

        main_category_data = {
            "name": validated_data['name'],
            "handle": handle_name,
            "description": validated_data['description'],
            "is_active": f"{validated_data['active']}".capitalize(),
            "slug": validated_data['slug'],
            "seo_title": validated_data['seo title'],
            "seo_description": validated_data['seo description'],
        }

        main_category = MainCategory.objects.create(**main_category_data)

        # meta_data = {
        #     "field": validated_data['meta data field'],
        #     "value": validated_data['meta data value']
        # }
        #
        # MainCategoryMetaData.objects.create(main_category=main_category, **meta_data)

        if len(validated_data['category image']) != 0:
            image_link = validated_data['category image']
            media_data = {}
            url_split = image_link.split('/')
            if url_split:
                media_data["cdn_link"] = image_link
                media_data["file_name"] = url_split[4]
                media_data["file_path"] = url_split[3] + '/' + url_split[4]
                media_data["main_category"] = main_category
                Media.objects.create(**media_data)

        return main_category


class SubCategoryMigrateSerializer(serializers.ModelSerializer):
    main_category = serializers.CharField(required=False)

    class Meta:
        model = SubCategory
        exclude = ['deleted', 'deleted_at', 'created_at', 'updated_at', 'handle']

    def create(self, validate_data):
        validated_data = self.initial_data

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

        sub_category_data = {
            "name": validated_data['name'],
            "handle": handle_name,
            "description": validated_data['description'],
            "is_active": f"{validated_data['active']}".capitalize(),
            "slug": validated_data['slug'],
            "seo_title": validated_data['seo title'],
            "seo_description": validated_data['seo description'],
            "main_category_id": validated_data['main category id']
        }

        sub_category = SubCategory.objects.create(**sub_category_data)

        # meta_data = {
        #     "field": validated_data['meta data field'],
        #     "value": validated_data['meta data value']
        #     }
        # SubCategoryMetaData.objects.create(sub_category=sub_category, **meta_data)

        if len(validated_data['category image']) != 0:
            image_link = validated_data['category image']
            media_data = {}
            url_split = image_link.split('/')
            if url_split:
                media_data["cdn_link"] = image_link
                media_data["file_name"] = url_split[4]
                media_data["file_path"] = url_split[3] + '/' + url_split[4]
                media_data["sub_category"] = sub_category
                Media.objects.create(**media_data)

        return sub_category


class SuperSubCategoryMigrateSerializer(serializers.ModelSerializer):
    sub_category = serializers.CharField(required=False)

    class Meta:
        model = SuperSubCategory
        exclude = ['deleted', 'deleted_at', 'created_at', 'updated_at', 'handle']

    def create(self, validate_data):
        validated_data = self.initial_data

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

        supersub_category_data = {
            "name": validated_data['name'],
            "handle": handle_name,
            "description": validated_data['description'],
            "is_active": f"{validated_data['active']}".capitalize(),
            "slug": validated_data['slug'],
            "seo_title": validated_data['seo title'],
            "seo_description": validated_data['seo description'],
            "sub_category_id": validated_data['sub category id']
        }

        super_sub_category = SuperSubCategory.objects.create(**supersub_category_data)

        # meta_data = {
        #     "field": validated_data['meta data field'],
        #     "value": validated_data['meta data value']
        #     }
        # SuperSubCategoryMetaData.objects.create(super_sub_category=super_sub_category, **meta_data)

        if len(validated_data['category image']) != 0:
            image_link = validated_data['category image']
            media_data = {}
            url_split = image_link.split('/')
            if url_split:
                media_data["cdn_link"] = image_link
                media_data["file_name"] = url_split[4]
                media_data["file_path"] = url_split[3] + '/' + url_split[4]
                media_data["super_sub_category"] = super_sub_category
                Media.objects.create(**media_data)

        return super_sub_category
