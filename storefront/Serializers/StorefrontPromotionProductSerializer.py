
from rest_framework import serializers
from rest_framework import exceptions
from products.models import Product, Variant, Media
from drf_yasg.utils import swagger_serializer_method


class PromotionProductListSerializer(serializers.ModelSerializer):
    inventory = serializers.SerializerMethodField('get_inventory')
    price = serializers.SerializerMethodField('get_price')
    image = serializers.SerializerMethodField('get_image')

    class Meta:
        model = Product
        fields = ('id', 'title', 'handle', 'price', 'image', 'inventory','slug', 'seo_title', 'seo_description','seo_keywords')

    def get_inventory(self, obj):
        variants = Variant.objects.filter(product=obj)
        count = len(variants)
        qty = 0
        for variant in variants:
            qty = variant.inventory_quantity + qty
        if count == 1:
            return str(qty) + " in stock for " + str(count) + " variant"
        return str(qty) + " in stock for " + str(count) + " variants"

    def get_price(self, obj):
        price = dict()
        variants = Variant.objects.filter(product=obj).first()
        original_price = int(variants.price)
        compare_price = int(variants.compare_at_price)
        discount_percentage = 100 - ((original_price / compare_price) * 100)

        price['original_price'] = original_price
        price['compare_price'] = compare_price
        price['discount_percentage'] = round(discount_percentage, 1)

        return price

    def get_image(self, obj):
        image = Media.objects.filter(product=obj, position=1).first()
        if image is not None:
            return image.cdn_link
        else:
            return None
