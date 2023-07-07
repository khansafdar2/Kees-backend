
from rest_framework import serializers
from products.models import Collection, CollectionHandle, Media
from products.BusinessLogic.RemoveSpecialCharacters import remove_specialcharacters


class CollectionMigrationSerializer(serializers.ModelSerializer):
    main_category = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    sub_category = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    super_sub_category = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    vendor = serializers.CharField(required=False)

    class Meta:
        model = Collection
        fields = '__all__'

    def create(self, validate_data):
        validated_data = self.initial_data

        main_category = validated_data.pop('main_category', None)
        sub_category = validated_data.pop('sub_category', None)
        super_sub_category = validated_data.pop('super_sub_category', None)
        meta_data_field = validated_data.pop('meta_data_field', None)
        meta_data_value = validated_data.pop('meta_data_value', None)
        banner_image = validated_data.pop('image', None)

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

        collection_data = {
            "vendor_id": validated_data['vendor_id'],
            "title": validated_data['title'],
            "description": validated_data['description'],
            "handle": handle_name,
            "slug": validated_data['slug'],
            "seo_title": validated_data['seo_title'],
            "seo_description": validated_data['seo_description'],
            "status": "Approved",
            "is_active": f"{validated_data['active']}".capitalize(),
        }

        collection = Collection.objects.create(**collection_data)

        if len(main_category) > 0 and main_category[0] != '':
            main_category = main_category.split(',')
            collection.main_category.set(main_category)
        if len(sub_category) > 0 and sub_category[0] != '':
            sub_category = sub_category.split(',')
            collection.sub_category.set(sub_category)
        if len(super_sub_category) > 0 and super_sub_category[0] != '':
            super_sub_category = super_sub_category.split(',')
            collection.super_sub_category.set(super_sub_category)

        # meta_data = {
        #     "field": meta_data_field,
        #     "value": meta_data_value
        # }
        #
        # CollectionMetaData.objects.create(collection=collection, **meta_data)

        if len(banner_image) != 0:
            image_link = banner_image
            media_data = {}
            url_split = image_link.split('/')
            if url_split:
                media_data["cdn_link"] = image_link
                media_data["file_name"] = url_split[4]
                media_data["file_path"] = url_split[3] + '/' + url_split[4]
                media_data["collection"] = collection
                Media.objects.create(**media_data)

        return collection
