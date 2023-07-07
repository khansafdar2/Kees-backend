
from datetime import datetime
import pytz
from django.db.models import Q
from discount.models import Discount
from products.models import Variant, ProductGroup, MainCategory, SubCategory, SuperSubCategory
from rest_framework import exceptions
from authentication.BusinessLogic.Threading import start_new_thread
from apscheduler.schedulers.background import BackgroundScheduler
from setting.models import StoreInformation


# @start_new_thread
# def start():
#     print('Scheduler start')
#     scheduler = BackgroundScheduler()
#     scheduler.add_job(apply_discount, 'interval', seconds=300)
#     scheduler.start()


def set_discount(discount, variants):
    for variant in variants:
        try:
            if discount.value_type == 'fixed_amount':
                discount_value = discount.value
                if discount_value < variant.compare_at_price:
                    discount_price = variant.compare_at_price - discount_value
                else:
                    discount_price = variant.compare_at_price

            elif discount.value_type == 'percentage':
                discount_value = discount.value
                discount_price = variant.compare_at_price * (discount_value / 100)
                discount_price = variant.compare_at_price - discount_price
            else:
                raise exceptions.ParseError('Invalid discount value type')

            variant.price = discount_price
            variant.save()

            print(f"{variant.id} with poduct {variant.product.id} apply")
        except Exception as e:
            print(e)


def delete_discount(variants):
    for variant in variants:
        variant.price = variant.compare_at_price
        variant.save()


def apply_discount(discounts=None):
    store_information = StoreInformation.objects.filter(deleted=False).first()
    if not store_information:
        raise exceptions.ParseError('Please save store information first')
    if not store_information.time_zone:
        raise exceptions.ParseError('Please save time zone in store information first')
    today = datetime.now(pytz.timezone(store_information.time_zone))
    today = today.replace(tzinfo=None)
    utc = pytz.UTC
    # today = utc.localize(today)

    if discounts is None:
        discounts = Discount.objects.filter(discount_type='simple_discount', status='Approved', deleted=False)

    for discount in discounts:
        if discount.start_date is not None and discount.end_date is not None:
            if discount.start_date <= today < discount.end_date:
                discount.is_active = True
                discount.save()
            elif today > discount.end_date:
                discount.is_active = False
                discount.save()
            else:
                break

        if discount.criteria == 'product':
            variants = Variant.objects.filter(product__product_discount=discount, deleted=False)
            if not variants:
                vendor_id = discount.vendor_id
                if vendor_id:
                    variants = Variant.objects.filter(product__is_active=True, vendor_id=vendor_id, deleted=False)
                else:
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
            super_sub_category = SuperSubCategory.objects.filter(super_sub_category_discount=discount, is_active=True,
                                                                 deleted=False)

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

        if discount.start_date is None and discount.end_date is None:
            if discount.is_active:
                set_discount(discount, variants)
            else:
                delete_discount(variants)
        else:
            if discount.start_date <= today < discount.end_date:
                set_discount(discount, variants)
            elif today > discount.end_date:
                delete_discount(variants)
