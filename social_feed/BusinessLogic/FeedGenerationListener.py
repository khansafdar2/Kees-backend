
import re
import random
import os, sys
from django.db.models import Q
import boto3
from json2xml import json2xml
from authentication.BusinessLogic.Threading import start_new_thread
from products.models import Product, Variant, Tags, Media, Option, MainCategory, SubCategory, SuperSubCategory
from setting.models import StoreInformation
from social_feed.models import Feed, Setting
from rest_framework import exceptions
from django.conf import settings as django_setting
from datetime import datetime


@start_new_thread
def generate_feed(feed=None):
    print('social feed thread start')
    setting = Setting.objects.filter(is_active=True, deleted=False).first()

    if feed is not None:
        feeds = [feed]
    else:
        feeds = Feed.objects.filter(is_active=True, deleted=False)

    for feed in feeds:
        # Fetch Products
        products = None
        if setting.export_products == 'active':
            if feed.product_export == 'all':
                products = Product.objects.filter(is_active=True, status='Approved', deleted=False)
            elif feed.product_export == 'category':
                try:
                    main_categories = feed.main_category.all().values_list('id', flat=True)
                    sub_categories = feed.sub_category.all().values_list('id', flat=True)
                    super_sub_categories = feed.super_sub_category.all().values_list('id', flat=True)

                    products = Product.objects.filter(Q(collection__main_category__in=main_categories) |
                                                      Q(collection__sub_category__in=sub_categories) |
                                                      Q(collection__super_sub_category__in=super_sub_categories), is_active=True, status='Approved')
                except Exception as e:
                    print(e)
                    raise e

        elif setting.export_products == 'both':
            if feed.product_export == 'all':
                products = Product.objects.filter(status='Approved', deleted=False)
            elif feed.product_export == 'category':
                try:
                    main_categories = feed.main_category.all().values_list('id', flat=True)
                    sub_categories = feed.sub_category.all().values_list('id', flat=True)
                    super_sub_categories = feed.super_sub_category.all().values_list('id', flat=True)

                    products = Product.objects.filter(Q(collection__main_category__in=main_categories) |
                                                      Q(collection__sub_category__in=sub_categories) |
                                                      Q(collection__super_sub_category__in=super_sub_categories), status='Approved')
                except Exception as e:
                    print(e)
                    raise e
        else:
            raise exceptions.ParseError('No product Exist at store', code=404)

        result = get_products(products, setting, feed)
        xml_output = result["xml_output"]
        feed.no_of_products = len(products)
        now = datetime.now()
        if feed.ref_no is None:
            feed.ref_no = str(random.randint(100, 10000)) + now.strftime('%d%m%y%H%M%S')

        file_name = str(feed.ref_no) + '.xml'
        feed.save()
        path = os.path.abspath(f'social_feed/XmlFiles/{file_name}')
        try:
            file = open(path, 'w', encoding='utf-8-sig')
            file.write(xml_output)
            file.close()
        except Exception as e:
            print(e)
            raise e

        # Upload to S3
        s3 = boto3.client('s3', aws_access_key_id=django_setting.AWS_ACCESS_KEY_ID, aws_secret_access_key=django_setting.AWS_SECRET_ACCESS_KEY)
        s3.upload_file(path, django_setting.AWS_BUCKET_PATH, file_name,
                       ExtraArgs={'StorageClass': "STANDARD_IA", 'ACL': 'public-read'})
        feed.feed_link = "https://" + django_setting.AWS_BUCKET_PATH + ".s3.amazonaws.com/" + file_name
        feed.feed_status = "OK"
        feed.save()
        os.remove(path)
        print('Feed complete')


def get_products(products, setting, feed):
    final_products = []

    for product in products:
        product_array = []
        client_domain = django_setting.STOREFRONT_URL
        price_format = int(setting.price_format)

        media = Media.objects.filter(product=product, position=1).first()
        if media:
            image_link = media.cdn_link
        else:
            continue

        if feed.export_mode == "all":
            variants = Variant.objects.filter(product=product, deleted=False)
            for variant in variants:
                if feed.in_stock == 'true':
                    if variant.inventory_quantity <= 0:
                        continue
                product_obj = final_variant_data(product, image_link, setting, feed, variant, price_format, client_domain)
                if product_obj:
                    product_array.append(product_obj)
        else:
            if feed.export_mode == "first variant":
                variant = Variant.objects.filter(product=product, deleted=False).first()
                if feed.in_stock == 'true':
                    if variant.inventory_quantity > 0:
                        product_obj = final_variant_data(product, image_link, setting, feed, variant, price_format, client_domain)
                        if product_obj:
                            product_array.append(product_obj)
                else:
                    product_obj = final_variant_data(product, image_link, setting, feed, variant, price_format, client_domain)
                    if product_obj:
                        product_array.append(product_obj)

        final_products.append(product_array)

    final_products_data = []
    for product in final_products:
        for item in product:
            final_products_data.append(item)

    if feed.feed_type == "facebook":
        store = StoreInformation.objects.filter(deleted=False).first()
        json_for_xml = {
            "title": store.store_name,
            "link": "",
            "entry": final_products_data
        }

        link = '<link rel="self" href="' + django_setting.STOREFRONT_URL + '"/>'

        xml_output = json2xml.Json2xml(json_for_xml, attr_type=False).to_xml()
        xml_output = xml_output.replace('</entry>', '')
        xml_output = xml_output.replace('<entry>', '')
        xml_output = xml_output.replace('<item>', '<entry>')
        xml_output = xml_output.replace('</item>', '</entry>')
        xml_output = xml_output.replace('<link/>', link)
        xml_output = xml_output.replace('<all>', '<feed xmlns="http://www.w3.org/2005/Atom" xmlns:g="http://base.google.com/ns/1.0">')
        xml_output = xml_output.replace('</all>', '</feed>')

        return {"xml_output": xml_output, "products": final_products_data}
    else:
        return final_products_data


def final_variant_data(product, image_link, setting, feed, variant, price_format, client_domain):
    options = Option.objects.filter(product=product, deleted=False)

    product_tags = Tags.objects.filter(product_tags=product, is_option=False).values_list('name', flat=True)
    product_tags = [x.lower() for x in product_tags]

    if feed.exclude_tags is not None:
        exclude_tags = feed.exclude_tags.split(',')
        exclude_tags = [x.lower() for x in exclude_tags]
        final_tags = [i for i in product_tags + exclude_tags if i not in product_tags or i not in exclude_tags]
    else:
        final_tags = product_tags

    final_tags = ', '.join(final_tags)
    gender = "Male"

    # if settiing_information.export_gender == 'Export vendor as gender field (default)':
    #     gender = product['vendor']
    # elif settiing_information.export_gender == 'Export product type as gender field':
    #     gender = product['product_type']
    # else:
    #     if product['tags'] is not None:
    #         gender_list = product['tags'].split(',')
    #         new_gender_list = [x.lower() for x in gender_list]
    #         if 'female' in new_gender_list:
    #             gender = "Female"
    #         elif 'male' in new_gender_list:
    #             gender = "Male"
    #         else:
    #             gender = ''
    #     else:
    #         gender = ''

    price_format = "%." + str(price_format) + "f"
    price = float(variant.price)
    price = price_format % price

    inventory_quantity = variant.inventory_quantity
    sale_price = float(variant.compare_at_price)
    sale_price = price_format % sale_price

    if variant.title == 'Default Title':
        data = {
            'size': "",
            'color': "",
            'material': ""
        }
    else:
        data = {
            'size': '',
            'color': '',
            'material': ''
        }
        if options:
            for option in options:
                if option.name.lower() == 'size':
                    data['size'] = option.values
                elif option.name.lower() == 'color' or option.name.lower() == 'colour':
                    data['color'] = option.values
                elif option.name.lower() == 'material' or option.name.lower() == 'fabric':
                    data['material'] = option.values

    product_link = client_domain + '/product/' + product.handle

    if inventory_quantity > 0:
        availability = "in stock"
    else:
        availability = "out of stock"

    if product.product_brand is not None:
        brand = product.product_brand.name
    else:
        brand = ""

    feed.custom_label5 = 'category'
    feed.save()

    category = MainCategory.objects.filter(collection_main_category__product=product).first()
    if not category:
        category = SubCategory.objects.filter(collection_sub_category__product=product).first()
        if not category:
            category = SuperSubCategory.objects.filter(collection_super_sub_category__product=product).first()

    if category:
        category = category.name
    else:
        category = ' '

    if feed.custom_label1 == "tags":
        custom_label_0 = final_tags
    elif feed.custom_label1 == "sku":
        custom_label_0 = variant.sku
    elif feed.custom_label1 == "barcode":
        custom_label_0 = variant.barcode
    elif feed.custom_label1 == "product handle":
        custom_label_0 = product.handle
    elif feed.custom_label1 == "category":
        custom_label_0 = category
    else:
        custom_label_0 = ' '

    if feed.custom_label2 == "tags":
        custom_label_1 = final_tags
    elif feed.custom_label2 == "sku":
        custom_label_1 = variant.sku
    elif feed.custom_label2 == "barcode":
        custom_label_1 = variant.barcode
    elif feed.custom_label2 == "product handle":
        custom_label_1 = product.handle
    elif feed.custom_label2 == "category":
        custom_label_1 = category
    else:
        custom_label_1 = ' '

    if feed.custom_label3 == "tags":
        custom_label_2 = final_tags
    elif feed.custom_label3 == "sku":
        custom_label_2 = variant.sku
    elif feed.custom_label3 == "barcode":
        custom_label_2 = variant.barcode
    elif feed.custom_label3 == "product handle":
        custom_label_2 = product.handle
    elif feed.custom_label3 == "category":
        custom_label_2 = category
    else:
        custom_label_2 = ' '

    if feed.custom_label4 == "tags":
        custom_label_3 = final_tags
    elif feed.custom_label4 == "sku":
        custom_label_3 = variant.sku
    elif feed.custom_label4 == "barcode":
        custom_label_3 = variant.barcode
    elif feed.custom_label4 == "product handle":
        custom_label_3 = product.handle
    elif feed.custom_label4 == "category":
        custom_label_3 = category
    else:
        custom_label_3 = ' '

    if feed.custom_label5 == "tags":
        custom_label_4 = final_tags
    elif feed.custom_label5 == "sku":
        custom_label_4 = variant.sku
    elif feed.custom_label5 == "barcode":
        custom_label_4 = variant.barcode
    elif feed.custom_label5 == "product handle":
        custom_label_4 = product.handle
    elif feed.custom_label5 == "category":
        custom_label_4 = category
    else:
        custom_label_4 = ' '

    description = product.description
    if description is not None:
        description = re.sub(re.compile('<.*?>'), '', product.description)
    else:
        description = 'product description'

    data = {
        "id": variant.id,
        "item_group_id": product.id,
        "title": product.title,
        "description": description,
        "link": product_link,
        "image_link": image_link,
        "barcode": variant.barcode,
        "brand": brand,
        "condition": "new",
        "availability": availability,
        "inventory": inventory_quantity,
        "price": price,
        "sale_price": sale_price,
        "google_product_category": "",
        "product_type": product.product_type,
        "size": data['size'],
        "color": data['color'],
        "material": data['material'],
        "custom_label_0": custom_label_0,
        "custom_label_1": custom_label_1,
        "custom_label_2": custom_label_2,
        "custom_label_3": custom_label_3,
        "custom_label_4": custom_label_4,
        "identifier_exists": False,
        "shipping_weight": variant.weight,
        "gender": gender
    }
    return data
