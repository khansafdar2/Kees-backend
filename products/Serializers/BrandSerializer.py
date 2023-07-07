
from products.models import Brand, Media, BrandHandle
from rest_framework import serializers
from drf_yasg.utils import swagger_serializer_method
from products.BusinessLogic.RemoveSpecialCharacters import remove_specialcharacters
from django.db.models import Q


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('id', 'name', 'handle')


class ImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ('id', 'file_name', 'file_path', 'cdn_link', 'brand')


class BrandDetailSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField('get_image')
    banner_image = serializers.SerializerMethodField('get_banner_image')

    class Meta:
        model = Brand
        fields = '__all__'

    @swagger_serializer_method(serializer_or_field=ImagesSerializer)
    def get_image(self, obj):
        serializer_context = {'request': self.context.get('request')}
        image = Media.objects.filter(~Q(file_name="brand_banner"), brand_id=obj.id, deleted=False).first()
        if image is None:
            return None
        serializer = ImagesSerializer(image, context=serializer_context)
        return serializer.data

    @swagger_serializer_method(serializer_or_field=ImagesSerializer)
    def get_banner_image(self, obj):
        serializer_context = {'request': self.context.get('request')}
        banner_image = Media.objects.filter(brand_id=obj.id, file_name="brand_banner", deleted=False).first()
        if banner_image is None:
            return None
        serializer = ImagesSerializer(banner_image, context=serializer_context)
        return serializer.data


class AddBrandSerializer(serializers.ModelSerializer):
    image = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Brand
        fields = ('id', 'name', 'handle', 'image')

    def create(self, validate_data):
        try:
            validated_data = self.initial_data
            image = validated_data.pop('image', None)
            banner_image = validated_data.pop('banner_image', None)

            # Save Unique Product Handle
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
            validated_data['handle'] = handle_name

            instance = Brand.objects.create(**validated_data)
            if image is not None:
                Media.objects.filter(id=image).update(brand=instance)
            else:
                try:
                    Media.objects.filter(brand_id=instance.id).update(brand=None)
                except Exception as e:
                    print(e)
                    pass

            if banner_image is not None:
                Media.objects.filter(id=banner_image).update(brand=instance, file_name="brand_banner")

            return instance

        except Exception as e:
            print(e)
            raise Exception(str(e))

    def update(self, instance, validate_data):
        try:
            validated_data = self.initial_data
            image = validated_data.pop('image', None)
            banner_image = validated_data.pop('banner_image', None)

            Brand.objects.filter(id=instance.id).update(**validated_data)

            if image is not None:
                Media.objects.filter(id=image).update(brand=instance)
            else:
                try:
                    Media.objects.filter(brand_id=instance.id).update(brand=None)
                except Exception as e:
                    print(e)
                    pass
            if banner_image is not None:
                Media.objects.filter(id=banner_image).update(brand=instance, file_name="brand_banner")

            return instance

        except Exception as e:
            print(e)
            raise Exception(str(e))

