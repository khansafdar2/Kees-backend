from datetime import datetime
from rest_framework import serializers, exceptions
from cms.models import Blog, BlogCategory
from products.BusinessLogic.RemoveSpecialCharacters import remove_specialcharacters


class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = ('id', 'title', 'is_active')


class BlogListSerializer(serializers.ModelSerializer):
    blog_category_title = serializers.CharField(source='blog_category.title', allow_blank=True, allow_null=True)

    class Meta:
        model = Blog
        fields = '__all__'


class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = '__all__'

    def create(self, validated_data):
        status = validated_data.get('status')

        if status == "Publish":
            validated_data['published_at'] = datetime.now()

        # creating handle
        handle_name = remove_specialcharacters(validated_data['title'].replace(' ', '-').lower())
        blog_handles = Blog.objects.filter(is_deleted=False).values_list('handle', flat=True)

        count = 1
        handle = handle_name
        while handle in blog_handles:
            handle = handle_name + "-" + str(count)
            count += 1
        validated_data['handle'] = handle

        instance = Blog.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        status = validated_data.get('status')

        if status != instance.status:
            if status == "Publish":
                validated_data['published_at'] = datetime.now()

        if validated_data['title'] != instance.title:
            handle_name = remove_specialcharacters(validated_data['title'].replace(' ', '-').lower())
            blog_handles = Blog.objects.filter(is_deleted=False).values_list('handle', flat=True)

            count = 1
            handle = handle_name
            while handle in blog_handles:
                handle = handle_name + "-" + str(count)
                count += 1

            validated_data['handle'] = handle

        Blog.objects.filter(id=instance.id).update(**validated_data)
        return instance


class BlogStatusChangeSerializer(serializers.ModelSerializer):
    ids = serializers.ListField(required=True)
    status = serializers.CharField(max_length=50, allow_blank=False, allow_null=False)

    class Meta:
        model = Blog
        fields = ('ids', 'status')

    def create(self, validated_data):
        validated_data = self.initial_data

        published_at = None
        if validated_data["status"] == "Publish":
            published_at = datetime.now()

        try:
            Blog.objects.filter(id__in=validated_data['ids']).update(status=validated_data["status"], published_at=published_at)
        except Exception as e:
            raise exceptions.ParseError(str(e))

        return validated_data
