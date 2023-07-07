
from rest_framework import serializers
from products.models import Product, Variant, Media


class GetVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = ('id', 'title', 'price', 'compare_at_price', 'sku', 'inventory_quantity', 'product_id')


class ProductListSerializer(serializers.ModelSerializer):
    vendor_id = serializers.CharField(source='vendor.id', read_only=True, allow_null=True, allow_blank=True)
    vendor_name = serializers.CharField(source='vendor.name', read_only=True, allow_null=True, allow_blank=True)
    shipping = serializers.CharField(source='product_group.shipping.amount', read_only=True, allow_null=True, allow_blank=True)
    variants = serializers.SerializerMethodField('get_variants')
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'vendor_id', 'vendor_name', 'shipping', 'title', 'has_variants', 'image', 'variants')

    def get_variants(self, obj):
        serializer_context = {'request': self.context.get('request')}
        variants_data = Variant.objects.filter(product=obj, deleted=False)
        serializer = GetVariantSerializer(variants_data, many=True, context=serializer_context)
        return serializer.data

    def get_image(self, obj):
        image = Media.objects.filter(product=obj, position=1).first()
        if image is not None:
            return image.cdn_link
        else:
            return None
