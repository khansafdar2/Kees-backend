
from django.db.models import Q
from order.models import LineItems
from discount.models import Discount
from rest_framework import serializers, exceptions
from products.models import Variant, ProductGroup, MainCategory, SubCategory, SuperSubCategory


def apply_promo(checkout, line_item, variant, obj):
    if variant:
        initial_price = line_item.total_price
        if obj.value_type == 'fixed_amount':
            discount_value = obj.value
            if discount_value < line_item.total_price:
                discount_price = line_item.total_price - discount_value
            else:
                discount_price = 0

        elif obj.value_type == 'percentage':
            discount_value = obj.value
            discount_price = line_item.total_price * (discount_value / 100)
            discount_price = line_item.total_price - discount_price
        else:
            raise exceptions.ParseError('Invalid discount value type')

        line_item.total_price = discount_price
        line_item.promo_code = obj.promo_code
        line_item.discount_id = obj.id
        line_item.save()

        checkout.subtotal_price -= (initial_price-discount_price)
        checkout.save()


def remove_promo(checkout, line_item, variant, obj):
    if variant:
        if obj.value_type == 'fixed_amount':
            discount_price = obj.value
            line_item_total = line_item.total_price + discount_price
            # if discount_value < line_item.total_price:
            #     discount_price = line_item.total_price + discount_value
            # else:
            #     discount_price = 0

        elif obj.value_type == 'percentage':
            discount_value = obj.value
            discount_price = (line_item.price * line_item.quantity) * (discount_value / 100)
            line_item_total = line_item.total_price + discount_price
        else:
            raise exceptions.ParseError('Invalid discount value type')

        line_item.total_price = line_item_total
        line_item.promo_code = None
        line_item.discount_id = None
        line_item.save()

    checkout.subtotal_price = float(checkout.subtotal_price) + float(discount_price)
    # checkout.subtotal_price = float(checkout.subtotal_price) + float(line_item.total_price)
    checkout.save()


class PromoCodeSerializer(serializers.ModelSerializer):
    list_items = serializers.SerializerMethodField('get_items')

    class Meta:
        model = Discount
        fields = ('list_items',)

    def get_items(self, obj):
        checkout = self.context['checkout']
        promo_code = self.context['promo_code']

        add_promo_checkout = False

        variant_list = []
        line_items = LineItems.objects.filter(checkout=checkout)
        for line_item in line_items:
            if line_item.promo_code is None:
                if not obj.apply_on_discounted_price:
                    if line_item.variant.price != line_item.variant.compare_at_price:
                        add_promo_checkout = True
                        continue

                if obj.criteria == 'product':
                    variant = Variant.objects.filter(id=line_item.variant_id, product__product_discount=obj,
                                                     deleted=False).first()

                elif obj.criteria == 'product_group':
                    vendor_id = obj.vendor_id
                    product_group = ProductGroup.objects.filter(
                        product_group__product_variant_id=line_item.variant_id).first()
                    product_groups = ProductGroup.objects.filter(product_group_discount=obj, is_active=True,
                                                                 deleted=False)
                    if not product_groups:
                        product_groups = ProductGroup.objects.filter(vendor_id=vendor_id, is_active=True, deleted=False)

                    if product_group in product_groups:
                        variant = Variant.objects.filter(id=line_item.variant_id).first()
                    else:
                        variant = None

                elif obj.criteria == 'category':
                    main_category = MainCategory.objects.filter(main_category_discount=obj, is_active=True,
                                                                deleted=False)
                    sub_category = SubCategory.objects.filter(sub_category_discount=obj, is_active=True, deleted=False)
                    super_sub_category = SuperSubCategory.objects.filter(super_sub_category_discount=obj,
                                                                         is_active=True, deleted=False)

                    if not main_category and not sub_category and not super_sub_category:
                        main_category = MainCategory.objects.filter(is_active=True, deleted=False)
                        sub_category = SubCategory.objects.filter(is_active=True, deleted=False)
                        super_sub_category = SuperSubCategory.objects.filter(is_active=True, deleted=False)

                    vendor_id = obj.vendor_id
                    if vendor_id:
                        variant = Variant.objects.filter((Q(product__collection__main_category__in=main_category) |
                                                          Q(product__collection__sub_category__in=sub_category) |
                                                          Q(product__collection__super_sub_category__in=super_sub_category)),
                                                         deleted=False, id=line_item.variant_id, product__vendor_id=vendor_id)
                    else:
                        variant = Variant.objects.filter((Q(product__collection__main_category__in=main_category) |
                                                          Q(product__collection__sub_category__in=sub_category) |
                                                          Q(product__collection__super_sub_category__in=super_sub_category)),
                                                         deleted=False, id=line_item.variant_id)
                else:
                    raise exceptions.ParseError('Invalid criteria type', code=404)

                if variant:
                    variant_list.append(variant)

                apply_promo(checkout, line_item, variant, obj)

        if not add_promo_checkout:
            if len(variant_list) == 0:
                raise exceptions.ParseError('Invalid Promo code', code=404)

            if checkout.promo_code:
                checkout.promo_code = checkout.promo_code + f',{promo_code}'
            else:
                checkout.promo_code = promo_code

        checkout.save()
        return 'promo applied'


class RemovePromoCodeSerializer(serializers.ModelSerializer):
    list_items = serializers.SerializerMethodField('get_items')

    class Meta:
        model = Discount
        fields = ('list_items',)

    def get_items(self, obj):
        checkout = self.context['checkout']
        promo_code = self.context['promo_code']

        remove_promo_checkout = False

        variant_list = []
        line_items = LineItems.objects.filter(checkout=checkout)
        for line_item in line_items:
            if line_item.promo_code is not None:
                if not obj.apply_on_discounted_price:
                    if line_item.variant.price != line_item.variant.compare_at_price:
                        remove_promo_checkout = True
                        continue

                if obj.criteria == 'product':
                    variant = Variant.objects.filter(id=line_item.variant_id, product__product_discount=obj,
                                                     deleted=False).first()

                elif obj.criteria == 'product_group':
                    vendor_id = obj.vendor_id
                    product_group = ProductGroup.objects.filter(
                        product_group__product_variant_id=line_item.variant_id).first()
                    product_groups = ProductGroup.objects.filter(product_group_discount=obj, is_active=True,
                                                                 deleted=False)
                    if not product_groups:
                        product_groups = ProductGroup.objects.filter(vendor_id=vendor_id, is_active=True, deleted=False)

                    if product_group in product_groups:
                        variant = Variant.objects.filter(id=line_item.variant_id).first()
                    else:
                        variant = None

                elif obj.criteria == 'category':
                    main_category = MainCategory.objects.filter(main_category_discount=obj, is_active=True,
                                                                deleted=False)
                    sub_category = SubCategory.objects.filter(sub_category_discount=obj, is_active=True, deleted=False)
                    super_sub_category = SuperSubCategory.objects.filter(super_sub_category_discount=obj,
                                                                         is_active=True, deleted=False)

                    if not main_category and not sub_category and not super_sub_category:
                        main_category = MainCategory.objects.filter(is_active=True, deleted=False)
                        sub_category = SubCategory.objects.filter(is_active=True, deleted=False)
                        super_sub_category = SuperSubCategory.objects.filter(is_active=True, deleted=False)

                    vendor_id = obj.vendor_id
                    if vendor_id:
                        variant = Variant.objects.filter((Q(product__collection__main_category__in=main_category) |
                                                          Q(product__collection__sub_category__in=sub_category) |
                                                          Q(product__collection__super_sub_category__in=super_sub_category)),
                                                         deleted=False, id=line_item.variant_id, product__vendor_id=vendor_id)
                    else:
                        variant = Variant.objects.filter((Q(product__collection__main_category__in=main_category) |
                                                          Q(product__collection__sub_category__in=sub_category) |
                                                          Q(product__collection__super_sub_category__in=super_sub_category)),
                                                         deleted=False, id=line_item.variant_id)
                else:
                    raise exceptions.ParseError('Invalid criteria type', code=404)

                remove_promo(checkout, line_item, variant, obj)

        if not remove_promo_checkout:
            if checkout.promo_code:
                promo_list = checkout.promo_code.split(',')
                if promo_code in promo_list:
                    promo_list.remove(promo_code)
                    promo_list = ','.join(promo_list)
                    if promo_list == '':
                        promo_list = None
            else:
                return 'Promo code already removed'

            checkout.promo_code = promo_list
            checkout.save()
        return 'promo removed'
