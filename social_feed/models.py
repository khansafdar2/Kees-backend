
from authentication.models import TimeStampedModel
from products.models import MainCategory, SubCategory, SuperSubCategory
from django.db import models


class Setting(TimeStampedModel):
    price_format = models.IntegerField(blank=True, null=True, default=2)
    export_products = models.CharField(max_length=200, blank=True, null=True)
    export_gender = models.CharField(max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)


class Feed(TimeStampedModel):
    main_category = models.ManyToManyField(MainCategory, related_name='main_category_feed')
    sub_category = models.ManyToManyField(SubCategory, related_name='sub_category_feed')
    super_sub_category = models.ManyToManyField(SuperSubCategory, related_name='super_sub_category_feed')
    feed_name = models.CharField(max_length=200, blank=True, null=True)
    feed_type = models.CharField(max_length=200, blank=True, null=True)
    export_mode = models.CharField(max_length=200, blank=True, null=True)
    export_variant = models.CharField(max_length=200, blank=True, null=True)
    use_price = models.CharField(max_length=200, blank=True, null=True)
    # currency = models.CharField(max_length=200, blank=True, null=True)
    product_export = models.CharField(max_length=200, blank=True, null=True)
    in_stock = models.CharField(max_length=200, blank=True, null=True)

    custom_label1 = models.CharField(max_length=200, blank=True, null=True)
    custom_label2 = models.CharField(max_length=200, blank=True, null=True)
    custom_label3 = models.CharField(max_length=200, blank=True, null=True)
    custom_label4 = models.CharField(max_length=200, blank=True, null=True)
    custom_label5 = models.CharField(max_length=200, blank=True, null=True)

    product_image = models.CharField(max_length=200, blank=True, null=True)

    exclude_tags = models.TextField(blank=True, null=True)
    feed_link = models.TextField(blank=True, null=True)
    feed_status = models.CharField(max_length=200, blank=True, null=True, default='pending')
    ref_no = models.CharField(max_length=200, blank=True, null=True)
    xml_output = models.TextField(blank=True, null=True)
    no_of_products = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)
