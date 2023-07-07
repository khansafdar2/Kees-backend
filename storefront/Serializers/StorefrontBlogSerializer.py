
from rest_framework import serializers
from cms.models import Blog


class BlogListSerializer(serializers.ModelSerializer):
    blog_category_title = serializers.CharField(source='blog_category.title', read_only=True)
    # blog_category_id = serializers.CharField(source='blog_category.id', read_only=True)

    class Meta:
        model = Blog
        fields = ('title', 'author', 'content', 'published_at', 'handle', 'thumbnail_image', 'blog_category_title', 'blog_category_id')


class BlogDetailSerializer(serializers.ModelSerializer):
    blog_category_id = serializers.CharField(source='blog_category.id', read_only=True)
    blog_category_title = serializers.CharField(source='blog_category.title', read_only=True)

    class Meta:
        model = Blog
        exclude = ['id',]
