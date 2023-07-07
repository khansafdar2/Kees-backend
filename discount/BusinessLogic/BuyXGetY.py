
from django.db.models import Q
from products.models import Variant, ProductGroup, MainCategory, SubCategory, SuperSubCategory


def get_x_lineitem(discount, line_item):
    variant = None
    if discount.criteria == 'product':
        variant = Variant.objects.filter(id=line_item.variant_id, product__product_discount=discount,
                                         deleted=False).first()

    elif discount.criteria == 'product_group':
        vendor_id = discount.vendor_id
        product_group = ProductGroup.objects.filter(product_group__product_variant_id=line_item.variant_id).first()
        product_groups = ProductGroup.objects.filter(product_group_discount=discount, is_active=True,
                                                     deleted=False)
        if not product_groups:
            product_groups = ProductGroup.objects.filter(vendor_id=vendor_id, is_active=True,
                                                         deleted=False)

        if product_group in product_groups:
            variant = Variant.objects.filter(id=line_item.variant_id).first()

    elif discount.criteria == 'category':
        main_category = MainCategory.objects.filter(main_category_discount=discount, is_active=True,
                                                    deleted=False)
        sub_category = SubCategory.objects.filter(sub_category_discount=discount, is_active=True,
                                                  deleted=False)
        super_sub_category = SuperSubCategory.objects.filter(super_sub_category_discount=discount,
                                                             is_active=True, deleted=False)

        if not main_category and not sub_category and not super_sub_category:
            main_category = MainCategory.objects.filter(is_active=True, deleted=False)
            sub_category = SubCategory.objects.filter(is_active=True, deleted=False)
            super_sub_category = SuperSubCategory.objects.filter(is_active=True, deleted=False)

        vendor_id = discount.vendor_id
        if vendor_id:
            variant = Variant.objects.filter((Q(product__collection__main_category__in=main_category) |
                                              Q(product__collection__sub_category__in=sub_category) |
                                              Q(product__collection__super_sub_category__in=super_sub_category)),
                                             deleted=False, id=line_item.variant_id, product__vendor_id=vendor_id).first()
        else:
            variant = Variant.objects.filter((Q(product__collection__main_category__in=main_category) |
                                              Q(product__collection__sub_category__in=sub_category) |
                                              Q(product__collection__super_sub_category__in=super_sub_category)),
                                             deleted=False, id=line_item.variant_id).first()

    return variant


def get_y_lineitem(discount, line_item):
    variant = None
    if discount.y_criteria == 'product':
        variant = Variant.objects.filter(id=line_item.variant_id, product__y_product_discount=discount,
                                         deleted=False).first()

    elif discount.y_criteria == 'product_group':
        vendor_id = discount.vendor_id
        product_group = ProductGroup.objects.filter(product_group__product_variant_id=line_item.variant_id).first()
        product_groups = ProductGroup.objects.filter(y_product_group_discount=discount, is_active=True,
                                                     deleted=False)
        if not product_groups:
            product_groups = ProductGroup.objects.filter(vendor_id=vendor_id, is_active=True,
                                                         deleted=False)

        if product_group in product_groups:
            variant = Variant.objects.filter(id=line_item.variant_id).first()

    elif discount.y_criteria == 'category':
        main_category = MainCategory.objects.filter(y_main_category_discount=discount, is_active=True,
                                                    deleted=False)
        sub_category = SubCategory.objects.filter(y_sub_category_discount=discount, is_active=True,
                                                  deleted=False)
        super_sub_category = SuperSubCategory.objects.filter(y_super_sub_category_discount=discount,
                                                             is_active=True, deleted=False)

        if not main_category and not sub_category and not super_sub_category:
            main_category = MainCategory.objects.filter(is_active=True, deleted=False)
            sub_category = SubCategory.objects.filter(is_active=True, deleted=False)
            super_sub_category = SuperSubCategory.objects.filter(is_active=True, deleted=False)

        vendor_id = discount.vendor_id
        if vendor_id:
            variant = Variant.objects.filter((Q(product__collection__main_category__in=main_category) |
                                              Q(product__collection__sub_category__in=sub_category) |
                                              Q(product__collection__super_sub_category__in=super_sub_category)),
                                             deleted=False, id=line_item.variant_id, product__vendor_id=vendor_id).first()
        else:
            variant = Variant.objects.filter((Q(product__collection__main_category__in=main_category) |
                                              Q(product__collection__sub_category__in=sub_category) |
                                              Q(product__collection__super_sub_category__in=super_sub_category)),
                                             deleted=False, id=line_item.variant_id).first()

    return variant
