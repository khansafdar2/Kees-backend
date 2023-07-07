
from products.models import MainCategory, SubCategory, SuperSubCategory
from social_feed.models import Feed
from rest_framework import serializers


class MainCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MainCategory
        fields = ['id', 'name', 'handle']


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'handle']


class SuperSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SuperSubCategory
        fields = ['id', 'name', 'handle']


class FeedListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        fields = ('id', 'feed_name', 'no_of_products', 'feed_status', 'created_at', 'updated_at', 'feed_link')


class FeedSerializer(serializers.ModelSerializer):
    main_category = serializers.SerializerMethodField('get_main_category')
    sub_category = serializers.SerializerMethodField('get_sub_category')
    super_sub_category = serializers.SerializerMethodField('get_super_sub_category')

    class Meta:
        model = Feed
        fields = "__all__"

    def get_main_category(self, obj):
        serializer_context = {'request': self.context.get('request')}
        main_category_data = MainCategory.objects.filter(main_category_feed=obj, deleted=False)
        serializer = MainCategorySerializer(main_category_data, many=True, context=serializer_context)
        return serializer.data

    def get_sub_category(self, obj):
        serializer_context = {'request': self.context.get('request')}
        sub_category_data = SubCategory.objects.filter(sub_category_feed=obj, deleted=False)
        serializer = SubCategorySerializer(sub_category_data, many=True, context=serializer_context)
        return serializer.data

    def get_super_sub_category(self, obj):
        serializer_context = {'request': self.context.get('request')}
        super_sub_category_data = SuperSubCategory.objects.filter(super_sub_category_feed=obj, deleted=False)
        serializer = SuperSubCategorySerializer(super_sub_category_data, many=True, context=serializer_context)
        return serializer.data

    def create(self, validate_data):
        validated_data = self.initial_data

        main_category = validated_data.pop('main_category')
        sub_category = validated_data.pop('sub_category')
        super_sub_category = validated_data.pop('super_sub_category')

        instance = Feed.objects.create(**validated_data)

        instance.main_category.set(main_category)
        instance.sub_category.set(sub_category)
        instance.super_sub_category.set(super_sub_category)

        return instance

    def update(self, instance, validate_data):
        validated_data = self.initial_data

        main_category = validated_data.pop('main_category')
        sub_category = validated_data.pop('sub_category')
        super_sub_category = validated_data.pop('super_sub_category')

        validated_data['feed_status'] = 'pending'
        validated_data['no_of_products'] = 0
        Feed.objects.filter(id=instance.id).update(**validated_data)
        feed = Feed.objects.filter(id=instance.id).first()

        feed.main_category.set(main_category)
        feed.sub_category.set(sub_category)
        feed.super_sub_category.set(super_sub_category)

        return instance
