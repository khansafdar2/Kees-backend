
from datetime import datetime
from django.db.models import Q
from discount.models import Discount
from products.models import Variant, ProductGroup, MainCategory, SubCategory, SuperSubCategory
from rest_framework import exceptions


def delete_discount(discount=None):
    if discount and discount.is_active:
        if discount.criteria == 'product':
            variants = Variant.objects.filter(product__product_discount=discount, deleted=False)
            if not variants:
                variants = Variant.objects.filter(product__is_active=True, deleted=False)

        elif discount.criteria == 'product_group':
            product_groups = ProductGroup.objects.filter(product_group_discount=discount, is_active=True, deleted=False)
            if not product_groups:
                vendor_id = discount.vendor_id
                product_groups = ProductGroup.objects.filter(vendor_id=vendor_id, is_active=True, deleted=False)

            variants = Variant.objects.filter(product__product_group__in=product_groups, deleted=False)

        elif discount.criteria == 'category':
            main_category = MainCategory.objects.filter(main_category_discount=discount, is_active=True, deleted=False)
            sub_category = SubCategory.objects.filter(sub_category_discount=discount, is_active=True, deleted=False)
            super_sub_category = SuperSubCategory.objects.filter(super_sub_category_discount=discount, is_active=True, deleted=False)

            if not main_category and not sub_category and not super_sub_category:
                main_category = MainCategory.objects.filter(is_active=True, deleted=False)
                sub_category = SubCategory.objects.filter(is_active=True, deleted=False)
                super_sub_category = SuperSubCategory.objects.filter(is_active=True, deleted=False)

            vendor_id = discount.vendor_id
            if vendor_id:
                variants = Variant.objects.filter((Q(product__collection__main_category__in=main_category) |
                                                  Q(product__collection__sub_category__in=sub_category) |
                                                  Q(product__collection__super_sub_category__in=super_sub_category)),
                                                  deleted=False, product__vendor_id=vendor_id).distinct()
            else:
                variants = Variant.objects.filter((Q(product__collection__main_category__in=main_category) |
                                                  Q(product__collection__sub_category__in=sub_category) |
                                                  Q(product__collection__super_sub_category__in=super_sub_category)),
                                                  deleted=False).distinct()
        else:
            raise exceptions.ParseError('Invalid criteria type', code=404)

        for variant in variants:
            variant.price = variant.compare_at_price
            variant.save()
