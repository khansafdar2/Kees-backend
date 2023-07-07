
from rest_framework import serializers
from products.models import Product, Variant, Option, Media, Feature, MainCategory, SubCategory, SuperSubCategory
from drf_yasg.utils import swagger_serializer_method


class ProductListSerializer(serializers.ModelSerializer):
    sold_out = serializers.SerializerMethodField('get_soldout')
    inventory = serializers.SerializerMethodField('get_inventory')
    price = serializers.SerializerMethodField('get_price')
    image = serializers.SerializerMethodField('get_image')

    class Meta:
        model = Product
        fields = ('id', 'title', 'handle', 'sold_out', 'price', 'image', 'inventory','slug', 'seo_title', 'seo_description','seo_keywords')

    def get_soldout(self, obj):
        variants = Variant.objects.filter(product=obj, deleted=False)
        check_quantity = [True if variant.inventory_quantity == 0 else False for variant in variants]
        if all(check_quantity):
            return True
        return False

    def get_inventory(self, obj):
        variants = Variant.objects.filter(product=obj)
        count = len(variants)
        qty = 0
        for variant in variants:
            if variant.inventory_quantity is not None:
                qty = variant.inventory_quantity + qty
        if count == 1:
            return str(qty) + " in stock for " + str(count) + " variant"
        return str(qty) + " in stock for " + str(count) + " variants"

    def get_price(self, obj):
        price = dict()
        variants = Variant.objects.filter(product=obj).first()
        price['original_price'] = variants.price
        price['compare_price'] = variants.compare_at_price
        return price

    def get_image(self, obj):
        image = Media.objects.filter(product=obj, deleted=False, position=1).first()
        if image is not None:
            return image.cdn_link
        else:
            return None


class AddVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = ['price']


class GetVariantSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField('get_price')

    class Meta:
        model = Variant
        fields = ['id', 'title', 'price', 'sku', 'option1', 'option2', 'option3', 'inventory_quantity']

    def get_price(self, obj):
        price = dict()
        original_price = obj.price
        compare_price = obj.compare_at_price
        price['original_price'] = original_price
        price['compare_price'] = compare_price
        return price


class AddOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        exclude = ['deleted', 'deleted_at', 'product', 'created_at', 'updated_at']


class ImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        exclude = ['deleted', 'deleted_at', 'product', 'created_at', 'updated_at', 'collection']


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        exclude = ['deleted', 'deleted_at', 'product']


class ProductDetailSerializer(serializers.ModelSerializer):
    sold_out = serializers.SerializerMethodField('get_soldout')
    variants = serializers.SerializerMethodField('get_variants')
    options = serializers.SerializerMethodField('get_options')
    images = serializers.SerializerMethodField('get_images')
    inventory = serializers.SerializerMethodField('get_inventory')
    features = serializers.SerializerMethodField('get_features')
    related_products = serializers.SerializerMethodField('get_relatedproducts')
    brand = serializers.CharField(source='product_brand.name', allow_blank=True, allow_null=True)
    product_type = serializers.CharField(source='product_type.name', allow_blank=True, allow_null=True)
    vendor_id = serializers.CharField(source='vendor.id')
    vendor_name = serializers.CharField(source='vendor.name')
    vendor_key = serializers.CharField(source='vendor.unique_id', allow_blank=True, allow_null=True)
    tat = serializers.CharField(source='product_group.tat', allow_blank=True, allow_null=True)
    category = serializers.SerializerMethodField('get_category')

    class Meta:
        model = Product
        fields = ['id', 'title', 'handle', 'description', 'brand', 'product_type', 'tat', 'warranty', 'whatsapp', 'cod_available', 'sold_out', 'vendor_id',
                  'vendor_name', 'vendor_key', 'inventory', 'variants', 'features', 'options', 'images', 'related_products', 'category', 'slug', 'seo_title', 'seo_description','seo_keywords']

    def get_soldout(self, obj):
        variants = Variant.objects.filter(product=obj)
        check_quantity = [True if variant.inventory_quantity == 0 else False for variant in variants]
        if all(check_quantity):
            return True
        return False

    @swagger_serializer_method(serializer_or_field=GetVariantSerializer)
    def get_variants(self, obj):
        serializer_context = {'request': self.context.get('request')}
        variants_data = Variant.objects.filter(product=obj, deleted=False)
        serializer = GetVariantSerializer(variants_data, many=True, context=serializer_context)
        return serializer.data

    @swagger_serializer_method(serializer_or_field=AddOptionsSerializer)
    def get_options(self, obj):
        serializer_context = {'request': self.context.get('request')}
        options_data = Option.objects.filter(product=obj, deleted=False).order_by('id')
        serializer = AddOptionsSerializer(options_data, many=True, context=serializer_context)
        return serializer.data

    @swagger_serializer_method(serializer_or_field=ImagesSerializer)
    def get_images(self, obj):
        serializer_context = {'request': self.context.get('request')}
        images_data = Media.objects.filter(product=obj, deleted=False).order_by('position')
        serializer = ImagesSerializer(images_data, many=True, context=serializer_context)
        return serializer.data

    def get_inventory(self, obj):
        variants = Variant.objects.filter(product=obj)
        count = len(variants)
        qty = 0
        for variant in variants:
            qty = variant.inventory_quantity + qty
        if count == 1:
            return str(qty) + " in stock for " + str(count) + " variant"
        return str(qty) + " in stock for " + str(count) + " variants"

    @swagger_serializer_method(serializer_or_field=FeatureSerializer)
    def get_features(self, obj):
        serializer_context = {'request': self.context.get('request')}
        images_data = Feature.objects.filter(product=obj, deleted=False)
        serializer = FeatureSerializer(images_data, many=True, context=serializer_context)
        return serializer.data

    def get_relatedproducts(self, obj):
        serializer_context = {'request': self.context.get('request')}
        category = MainCategory.objects.filter(collection_main_category__product=obj, is_active=True, deleted=False)
        if not category:
            data = []
            return data
        products = Product.objects.filter(collection__main_category__in=category, is_active=True, deleted=False).distinct()[0:10]
        serializer = ProductListSerializer(products, many=True, context=serializer_context)
        return serializer.data

    def get_category(self, obj):
        super_sub_category = SuperSubCategory.objects.filter(collection_super_sub_category__product=obj).first()
        if super_sub_category:
            return super_sub_category.handle
        sub_category = SubCategory.objects.filter(collection_sub_category__product=obj).first()
        if sub_category:
            return sub_category.handle
        main_category = MainCategory.objects.filter(collection_main_category__product=obj).first()
        if main_category:
            return main_category.handle
        return None


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ('cdn_link',)
