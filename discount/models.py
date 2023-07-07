
from django.db import models
from vendor.models import Vendor
from authentication.models import TimeStampedModel
from crm.models import Customer
from shipping.models import Shipping
from products.models import Product, ProductGroup, MainCategory, SubCategory, SuperSubCategory


class Discount(TimeStampedModel):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='vendor_discount', null=True, blank=True)
    main_category = models.ManyToManyField(MainCategory, related_name='main_category_discount')
    sub_category = models.ManyToManyField(SubCategory, related_name='sub_category_discount')
    super_sub_category = models.ManyToManyField(SuperSubCategory, related_name='super_sub_category_discount')
    product_group = models.ManyToManyField(ProductGroup, related_name='product_group_discount')
    product = models.ManyToManyField(Product, related_name='product_discount')

    y_main_category = models.ManyToManyField(MainCategory, related_name='y_main_category_discount')
    y_sub_category = models.ManyToManyField(SubCategory, related_name='y_sub_category_discount')
    y_super_sub_category = models.ManyToManyField(SuperSubCategory, related_name='y_super_sub_category_discount')
    y_product_group = models.ManyToManyField(ProductGroup, related_name='y_product_group_discount')
    y_product = models.ManyToManyField(Product, related_name='y_product_discount')

    customer = models.ManyToManyField(Customer, related_name='customer_discount')

    title = models.CharField(blank=True, null=True, max_length=200)
    discount_type = models.CharField(blank=True, null=True, max_length=200)
    criteria = models.CharField(blank=True, null=True, max_length=200)
    y_criteria = models.CharField(blank=True, null=True, max_length=200)
    promo_code = models.CharField(blank=True, null=True, max_length=200)
    value_type = models.CharField(blank=True, null=True, max_length=200)
    value = models.DecimalField(default=0.0, decimal_places=0, max_digits=10)
    check_minimum_purchase_amount = models.CharField(blank=True, null=True, max_length=200)
    minimum_purchase_amount = models.DecimalField(blank=True, null=True, decimal_places=0, max_digits=10)
    x_minimum_no_products = models.IntegerField(default=0)
    y_minimum_no_products = models.IntegerField(default=0)
    usage_limit = models.IntegerField(default=0)
    usage_count = models.IntegerField(default=0)
    handle = models.CharField(blank=True, null=True, max_length=200)
    customer_eligibility = models.CharField(blank=True, null=True, max_length=200)
    start_date = models.DateTimeField(default=None, blank=True, null=True)
    end_date = models.DateTimeField(default=None, blank=True, null=True)
    status = models.CharField(max_length=250, blank=True, null=True)
    is_active = models.BooleanField(default=False)

    no_limit = models.BooleanField(default=False)
    show_both_price = models.BooleanField(default=False)
    show_tag = models.BooleanField(default=False)
    apply_on_discounted_price = models.BooleanField(default=True)
    tags = models.TextField(blank=True, null=True)

    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['deleted', ]),
        ]


class DiscountHandle(TimeStampedModel):
    name = models.CharField(blank=True, null=True, max_length=250)
    count = models.IntegerField(default=0)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['id', 'name']),
        ]

