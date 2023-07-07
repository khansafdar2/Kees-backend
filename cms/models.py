
from django.db import models
from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import fields
from authentication.models import TimeStampedModel
import jsonfield


class Page(TimeStampedModel):
    title = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    publish_status = models.BooleanField(default=False, blank=True, null=True)
    publish_date = models.DateTimeField(default=datetime.now, blank=True)
    handle = models.TextField(blank=True, null=True)
    slug = models.CharField(blank=True, null=True, max_length=200)
    seo_title = models.CharField(blank=True, null=True, max_length=200)
    seo_description = models.TextField(blank=True, null=True)
    seo_keywords = models.TextField(blank=True, null=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        ordering = ('-title',)
        indexes = [
            models.Index(fields=['deleted', ]),
        ]


class PageHandle(TimeStampedModel):
    name = models.CharField(blank=True, null=True, max_length=250)
    count = models.IntegerField(default=0)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['id', 'name']),
        ]


class SEO(TimeStampedModel):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="PageSEO")
    title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    url_slug = models.TextField(blank=True, null=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        ordering = ('-title',)
        indexes = [
            models.Index(fields=['deleted', ]),
        ]


class Template(TimeStampedModel):
    name = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['deleted', ]),
        ]


class Preferences(TimeStampedModel):
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.TextField(blank=True, null=True)
    password = models.TextField(blank=True, null=True)
    enable_password = models.BooleanField(default=False)
    seo_title = models.CharField(blank=True, null=True, max_length=200)
    seo_description = models.TextField(blank=True, null=True)
    seo_keywords = models.TextField(blank=True, null=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['deleted', ]),
        ]


class MenuItem(TimeStampedModel):
    parent = models.ForeignKey("MenuItem", null=True, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = fields.GenericForeignKey('content_type', 'object_id')
    page_type = models.TextField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['deleted', ]),
        ]


class StoreFilter(TimeStampedModel):
    title = models.CharField(max_length=200, blank=True, null=True)
    type = models.CharField(max_length=200, blank=True, null=True)
    tags = models.TextField(null=True, blank=True)
    position = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['deleted', ]),
        ]


class PriceRangeFilter(TimeStampedModel):
    min_price = models.CharField(blank=True, null=True, max_length=200)
    max_price = models.CharField(blank=True, null=True, max_length=200)
    handle = models.CharField(blank=True, null=True, max_length=200)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['deleted', ]),
        ]


class PriceRangeHandle(TimeStampedModel):
    name = models.CharField(blank=True, null=True, max_length=250)
    count = models.IntegerField(default=0)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['id', 'name']),
        ]


class Newsletter(TimeStampedModel):
    email = models.CharField(blank=True, null=True, max_length=200)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['id', 'email']),
        ]


class Customization(TimeStampedModel):
    homepage_json = jsonfield.JSONField(blank=True, null=True)
    allowed_sections = jsonfield.JSONField(blank=True, null=True)
    header = jsonfield.JSONField(blank=True, null=True)
    footer = jsonfield.JSONField(blank=True, null=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['id']),
        ]


class Navigation(TimeStampedModel):
    title = models.CharField(blank=True, null=True, max_length=200)
    navigation_json = jsonfield.JSONField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['id']),
        ]


class BlogCategory(TimeStampedModel):
    title = models.CharField(blank=True, null=True, max_length=200)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)


class Blog(TimeStampedModel):
    blog_category = models.ForeignKey(BlogCategory, on_delete=models.CASCADE, blank=True, null=True, related_name='blog_blogcategory')
    title = models.TextField(blank=True, null=True)
    author = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    thumbnail_image = models.TextField(blank=True, null=True)
    handle = models.CharField(blank=True, null=True, max_length=200)
    status = models.CharField(max_length=200, default='draft')
    is_active = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    published_at = models.DateTimeField(default=None, null=True, blank=True)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['blog_category']),
        ]
