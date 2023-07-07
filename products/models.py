
from django.db import models
from authentication.models import TimeStampedModel
from vendor.models import Vendor, Commission


class Tags(TimeStampedModel):
    name = models.CharField(blank=True, null=True, max_length=200)
    is_active = models.BooleanField(default=True)
    is_option = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True)


class ProductGroup(TimeStampedModel):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="product_group_vendor")
    title = models.CharField(blank=True, null=True, max_length=200)
    handle = models.CharField(blank=True, null=True, max_length=250)
    tat = models.CharField(blank=True, null=True, max_length=250)
    status = models.CharField(max_length=250, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['deleted', 'id']),
        ]


class ProductGroupHandle(TimeStampedModel):
    name = models.CharField(blank=True, null=True, max_length=250)
    count = models.IntegerField(default=0)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['id', 'name']),
        ]


class MainCategory(TimeStampedModel):
    name = models.CharField(blank=True, null=True, max_length=200)
    handle = models.CharField(blank=True, null=True, max_length=200)
    description = models.TextField(blank=True, null=True)
    availability = models.BooleanField(default=True)
    position = models.IntegerField(default=0)
    slug = models.CharField(blank=True, null=True, max_length=200)
    seo_title = models.CharField(blank=True, null=True, max_length=200)
    seo_description = models.TextField(blank=True, null=True)
    seo_keywords = models.TextField(blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['deleted', 'id', 'name']),
        ]


class CategoryHandle(TimeStampedModel):
    name = models.CharField(blank=True, null=True, max_length=250)
    count = models.IntegerField(default=0)
    category_type = models.CharField(blank=True, null=True, max_length=250)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['id', 'name']),
        ]


class MainCategoryMetaData(TimeStampedModel):
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE, related_name="main_category_meta_data")
    field = models.CharField(blank=True, null=True, max_length=200)
    value = models.TextField(blank=True, null=True)


class SubCategory(TimeStampedModel):
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE, related_name="sub_main_category")
    name = models.CharField(blank=True, null=True, max_length=200)
    handle = models.CharField(blank=True, null=True, max_length=200)
    description = models.TextField(blank=True, null=True)
    availability = models.BooleanField(default=True)
    position = models.IntegerField(default=0)
    slug = models.CharField(blank=True, null=True, max_length=200)
    seo_title = models.CharField(blank=True, null=True, max_length=200)
    seo_description = models.TextField(blank=True, null=True)
    seo_keywords = models.TextField(blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['deleted', 'id', 'name', 'main_category']),
        ]


class SubCategoryCondition(TimeStampedModel):
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='sub_category_condition')
    column = models.CharField(blank=True, null=True, max_length=200)  # For Example "tag"
    relation = models.CharField(blank=True, null=True, max_length=200)  # For Example "equals"
    condition = models.CharField(blank=True, null=True, max_length=200)  # For Example "Test Tag"

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['id', 'sub_category']),
        ]


class SubCategoryMetaData(TimeStampedModel):
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name="sub_category_meta_data")
    field = models.CharField(blank=True, null=True, max_length=200)
    value = models.TextField(blank=True, null=True)


class SuperSubCategory(TimeStampedModel):
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name="super_sub_category")
    name = models.CharField(blank=True, null=True, max_length=200)
    handle = models.CharField(blank=True, null=True, max_length=200)
    description = models.TextField(blank=True, null=True)
    availability = models.BooleanField(default=True)
    position = models.IntegerField(default=0)
    slug = models.CharField(blank=True, null=True, max_length=200)
    seo_title = models.CharField(blank=True, null=True, max_length=200)
    seo_description = models.TextField(blank=True, null=True)
    seo_keywords = models.TextField(blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['deleted', 'id', 'name', 'sub_category']),
        ]


class SuperSubCategoryMetaData(TimeStampedModel):
    super_sub_category = models.ForeignKey(SuperSubCategory, on_delete=models.CASCADE,
                                           related_name="super_sub_category_meta_data")
    field = models.CharField(blank=True, null=True, max_length=150)
    value = models.TextField(blank=True, null=True)


class Collection(TimeStampedModel):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, blank=True, related_name="collection_vendor")
    main_category = models.ManyToManyField(MainCategory, blank=True, related_name="collection_main_category")
    sub_category = models.ManyToManyField(SubCategory, blank=True, related_name="collection_sub_category")
    super_sub_category = models.ManyToManyField(SuperSubCategory, blank=True, related_name="collection_super_sub_category")
    title = models.CharField(blank=True, null=True, max_length=200)
    handle = models.CharField(blank=True, null=True, max_length=200)
    description = models.TextField(blank=True, null=True)
    collection_type = models.CharField(blank=True, null=True, max_length=200)
    slug = models.CharField(blank=True, null=True, max_length=200)
    seo_title = models.CharField(blank=True, null=True, max_length=200)
    seo_description = models.TextField(blank=True, null=True)
    seo_keywords = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=250, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['deleted', 'id', 'title', 'vendor']),
        ]


class CollectionHandle(TimeStampedModel):
    name = models.CharField(blank=True, null=True, max_length=250)
    count = models.IntegerField(default=0)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['id', 'name']),
        ]


class CollectionRule(TimeStampedModel):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='collection_rules')
    column = models.CharField(blank=True, null=True, max_length=200)  # For Example "tag"
    relation = models.CharField(blank=True, null=True, max_length=200)  # For Example "equals"
    condition = models.CharField(blank=True, null=True, max_length=200)  # For Example "Test Tag"

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['id', 'collection']),
        ]


class CollectionMetaData(TimeStampedModel):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name="collection_meta_data")
    field = models.CharField(blank=True, null=True, max_length=200)
    value = models.TextField(blank=True, null=True)


class Brand(TimeStampedModel):
    name = models.CharField(blank=True, null=True, max_length=200)
    handle = models.CharField(blank=True, null=True, max_length=200)
    seo_title = models.CharField(blank=True, null=True, max_length=200)
    seo_description = models.TextField(blank=True, null=True)
    seo_keywords = models.TextField(blank=True, null=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['deleted', 'id', 'name', ]),
        ]


class BrandHandle(TimeStampedModel):
    name = models.CharField(blank=True, null=True, max_length=250)
    count = models.IntegerField(default=0)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['id', 'name']),
        ]


class Product(TimeStampedModel):
    collection = models.ManyToManyField(Collection, blank=True)
    tag = models.ManyToManyField(Tags, related_name='product_tags')
    product_group = models.ForeignKey(ProductGroup, null=True, on_delete=models.CASCADE, related_name="product_group")
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="product_vendor")
    product_brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="product_brand", null=True)
    commission = models.ForeignKey(Commission, on_delete=models.RESTRICT, null=True, blank=True, related_name="product_commission")

    product_type = models.CharField(blank=True, null=True, max_length=200)
    title = models.CharField(blank=True, null=True, max_length=200)
    description = models.TextField(blank=True, null=True)
    warranty = models.CharField(blank=True, null=True, max_length=200)
    status = models.CharField(max_length=250, blank=True, null=True)
    slug = models.CharField(blank=True, null=True, max_length=200)
    seo_title = models.CharField(blank=True, null=True, max_length=200)
    seo_description = models.TextField(blank=True, null=True)
    seo_keywords = models.TextField(blank=True, null=True)
    has_variants = models.BooleanField(default=False)
    whatsapp = models.BooleanField(default=True)
    track_inventory = models.BooleanField(default=False)
    cod_available = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    hide_out_of_stock = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
    handle = models.CharField(blank=True, null=True, max_length=200)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['deleted', 'id', 'product_group']),
        ]


class ProductHandle(TimeStampedModel):
    name = models.CharField(blank=True, null=True, max_length=250)
    count = models.IntegerField(default=0)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['id', 'name']),
        ]


class Variant(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_variant", null=True)
    title = models.CharField(blank=True, null=True, max_length=200)
    price = models.DecimalField(blank=True, null=True, decimal_places=0, max_digits=10)
    sku = models.CharField(max_length=200, null=True, unique=True)
    position = models.IntegerField(blank=True, null=True)
    compare_at_price = models.DecimalField(blank=True, null=True, decimal_places=0, max_digits=10)
    cost_per_item = models.CharField(blank=True, null=True, max_length=200)
    option1 = models.CharField(blank=True, null=True, max_length=200, default=None)
    option2 = models.CharField(blank=True, null=True, max_length=200, default=None)
    option3 = models.CharField(blank=True, null=True, max_length=200, default=None)
    taxable = models.BooleanField(default=True)
    barcode = models.CharField(blank=True, null=True, max_length=200)
    is_physical = models.BooleanField(default=True)
    weight = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    weight_unit = models.CharField(blank=True, null=True, max_length=200)
    inventory_quantity = models.IntegerField(default=0)
    old_inventory_quantity = models.IntegerField(default=0)
    legacy_product = models.IntegerField(blank=True, null=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['deleted', 'id', 'title', 'product']),
        ]


class Feature(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_feature")
    feature_title = models.CharField(blank=True, null=True, max_length=200)
    feature_details = models.TextField(null=True, blank=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['deleted', 'id', 'product']),
        ]


class Option(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_options")
    name = models.CharField(blank=True, null=True, max_length=200)
    position = models.IntegerField(blank=True, null=True)
    values = models.TextField(blank=True, null=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['deleted', 'id', 'product']),
        ]


class Media(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_media", null=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="brand_media", null=True)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name="collection_media", null=True)
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE, related_name="main_category_media",
                                      null=True)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name="sub_category_media",
                                     null=True)
    super_sub_category = models.ForeignKey(SuperSubCategory, on_delete=models.CASCADE,
                                           related_name="super_sub_category_media", null=True)
    file_name = models.TextField(blank=True, null=True)
    file_path = models.TextField(blank=True, null=True)
    cdn_link = models.TextField(blank=True, null=True)
    alt_text = models.TextField(blank=True, null=True)
    position = models.IntegerField(default=0)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(
                fields=['id', 'brand', 'collection', 'product', 'main_category', 'sub_category', 'super_sub_category']),
        ]


class InventoryHistory(TimeStampedModel):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name="variant_inventory_history")
    event = models.TextField(blank=True, null=True)
    adjusted_by = models.TextField(blank=True, null=True)
    adjustment = models.IntegerField(blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['id']),
        ]
