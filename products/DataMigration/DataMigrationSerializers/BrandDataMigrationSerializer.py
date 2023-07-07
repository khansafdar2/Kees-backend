
from products.models import Brand, Media, BrandHandle
from rest_framework import serializers
from products.BusinessLogic.RemoveSpecialCharacters import remove_specialcharacters


class BrandMigrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'

    def create(self, validate_data):
        validated_data = self.initial_data

        handle_name = remove_specialcharacters(validated_data['name'].replace(' ', '-').lower())
        handle = BrandHandle.objects.filter(name=handle_name).first()
        if handle is not None:
            handle_name = handle_name + "-" + str(handle.count)
            handle.count = handle.count + 1
            handle.save()
        else:
            handle = BrandHandle()
            handle.name = handle_name
            handle.count = 1
            handle.save()

        brand_data = {
            "name": validated_data['name'],
            "handle": handle_name
        }

        brand = Brand.objects.create(**brand_data)

        if len(validated_data['image']) != 0:
            image_link = validated_data['image']
            media_data = {}
            url_split = image_link.split('/')
            if url_split:
                media_data["cdn_link"] = image_link
                media_data["file_name"] = url_split[4]
                media_data["file_path"] = url_split[3] + '/' + url_split[4]
                media_data["brand"] = brand
                Media.objects.create(**media_data)

        return brand
