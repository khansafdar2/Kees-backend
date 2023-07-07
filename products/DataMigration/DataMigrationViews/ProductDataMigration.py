
import os, csv, glob
import random
import traceback
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from rest_framework import exceptions

from authentication.models import User
from crm.models import Customer, Wallet, Notes
from discount.BusinessLogic.ApplyDiscount import apply_discount
from discount.models import Discount
from products.BusinessLogic.RemoveSpecialCharacters import remove_specialcharacters
from products.models import Product, Variant, Option, Media, Feature, ProductGroup, ProductHandle, Collection, \
    Tags
from order.models import LineItems, ChildOrderLineItems, Order
from setting.BusinessLogic.LoyaltyCalculation import calculate_points
from vendor.models import Vendor
from datetime import datetime


class ProductImport(APIView):
    def post(self, request):
        try:
            file = request.data['file']
            file = file.read().decode('latin1').splitlines()
            csv_files = csv.DictReader(file)
            csv_file = [dict(i) for i in csv_files]

            for row in csv_file:
                try:
                    row['Handle'] = remove_specialcharacters(row['Handle'].replace(' ', '-').lower())
                    handle = row['Handle']
                    product = Product.objects.filter(handle=handle, deleted=False).first()
                    if product:
                        # Delete Default Variant
                        if len(row['Option1 Value']) > 0:
                            if not product.has_variants:
                                Variant.objects.filter(product=product, title='Default Title').update(deleted=True, deleted_at=datetime.now())
                                product.has_variants = True
                                product.save()

                            # create options
                            options = Option.objects.filter(product=product, deleted=False).order_by('id')
                            if options:
                                for single_option in options:
                                    if len(row['Option1 Name']) > 0:
                                        if row['Option1 Name'] == single_option.name:
                                            if len(row['Option1 Value']) != 0:
                                                option_values = single_option.values
                                                option_values = option_values.split(',')
                                                check_option = [row['Option1 Value'] for i in option_values if row['Option1 Value'] != i]
                                                if check_option:
                                                    single_option_object = Option.objects.filter(id=single_option.id).first()
                                                    option_values.append(check_option[0])
                                                    single_option_object.values = ",".join(option_values)
                                                    single_option_object.save()
                                        # else:
                                        #     option_data = {'name': row['Option1 Name'], 'values': row['Option1 Value'], 'product': product}
                                        #     Option.objects.create(**option_data)

                                        if len(row['Option2 Name']) > 0:
                                            if row['Option2 Name'] == single_option.name:
                                                if len(row['Option2 Value']) != 0:
                                                    option_values = single_option.values
                                                    option_values = option_values.split(',')
                                                    check_option = [row['Option2 Value'] for i in option_values if row['Option2 Value'] != i]
                                                    if check_option:
                                                        single_option_object = Option.objects.filter(id=single_option.id).first()
                                                        option_values.append(check_option[0])
                                                        single_option_object.values = ",".join(option_values)
                                                        single_option_object.save()

                                        if len(row['Option3 Name']) > 0:
                                            if row['Option3 Name'] == single_option.name:
                                                if len(row['Option3 Value']) != 0:
                                                    option_values = single_option.values
                                                    option_values = option_values.split(',')
                                                    check_option = [row['Option3 Value'] for i in option_values if row['Option3 Value'] != i]
                                                    if check_option:
                                                        single_option_object = Option.objects.filter(id=single_option.id).first()
                                                        option_values.append(check_option[0])
                                                        single_option_object.values = ",".join(option_values)
                                                        single_option_object.save()

                        if len(row['Option1 Name']) != 0 and len(row['Option2 Name']) != 0 and len(row['Option3 Name']) != 0:
                            title = row['Option1 Value'] + '/' + row['Option2 Value'] + '/' + row['Option3 Value']
                            option1 = row['Option1 Value']
                            option2 = row['Option2 Value']
                            option3 = row['Option3 Value']

                        elif len(row['Option1 Name']) != 0 and len(row['Option2 Name']) != 0:
                            title = row['Option1 Value'] + '/' + row['Option2 Value']
                            option1 = row['Option1 Value']
                            option2 = row['Option2 Value']
                            option3 = None

                        elif len(row['Option1 Name']) != 0:
                            title = row['Option1 Value']
                            option1 = row['Option1 Value']
                            option2 = None
                            option3 = None

                        if not f'{row["Physical Variant"]}'.capitalize():
                            weight = 0.0
                        else:
                            weight = float(row["Variant Weight"])

                        if len(row['Variant Compare At Price']) <= 0 or row['Variant Compare At Price'] == '':
                            row['Variant Compare At Price'] = row['Variant Price']

                        variant_data = {
                            "title": title,
                            "price": row["Variant Price"],
                            "sku": row["variant sku"],
                            "compare_at_price": row["Variant Compare At Price"],
                            "cost_per_item": row["Cost per item"],
                            "option1": option1,
                            "option2": option2,
                            "option3": option3,
                            "barcode": row["Variant Barcode"],
                            "is_physical": f'{row["Physical Variant"]}'.capitalize(),
                            "weight": weight,
                            "inventory_quantity": row["Variant Inventory Qty"],
                            "product": product}

                        Variant.objects.create(**variant_data)
                    else:
                        # check vendor
                        if len(row['Vendor']) > 0 and row['Vendor'] != '':
                            vendor_id = row['Vendor']
                        else:
                            return Response({'detail': 'vendor can not be null'})

                        if len(row['Product group']) > 0 and row['Product group'] != '':
                            product_group = row['Product group']
                            active = f'{row["Active"]}'.capitalize()
                        else:
                            product_group = None
                            active = False

                        if len(row['Brand']) > 0 and row['Brand'] != '':
                            brand_id = row['Brand']
                        else:
                            brand_id = None

                        if len(row['Collections']) > 0 and row['Collections'] != '':
                            collection = row['Collections'].split(',')
                        else:
                            collection = False

                        handle = ProductHandle()
                        handle.name = row['Handle']
                        handle.count = 1
                        handle.save()

                        # create product
                        product_data = {
                            "title": row["Title"],
                            "description": row["Description"],
                            "product_type": row["Product Type"],
                            "cod_available": f'{row["COD Available"]}'.capitalize(),
                            "handle": row["Handle"],
                            "track_inventory": f'{row["Track Inventory"]}'.capitalize(),
                            "is_active": active,
                            "is_approved": True,
                            "warranty": row["Warranty"],
                            "hide_out_of_stock": f'{row["Hide out of Stock"]}'.capitalize(),
                            "tags": row["Tags"]
                        }

                        product = Product.objects.create(vendor_id=vendor_id, product_group_id=product_group, product_brand_id=brand_id, **product_data)

                        if collection:
                            product.collection.set(collection)

                        # create media
                        media = row["Image Src"]
                        image_position = row["Image position"].split(',')
                        if media:
                            urls_list = media.split(',')

                            for count, url in enumerate(urls_list):
                                try:
                                    position = image_position[count]
                                except:
                                    position = None

                                media_data = {}
                                url_split = url.split('/')
                                if url_split:
                                    media_data["cdn_link"] = url
                                    media_data["file_name"] = url_split[-1]
                                    media_data["position"] = position
                                    media_data["product"] = product
                                    Media.objects.create(**media_data)

                        # create features
                        if (len(row['Feature Title']) > 0 and row['Feature Title'] != '') and (len(row['Feature Details']) > 0 and row['Feature Details'] != ''):
                            feature_title = row["Feature Title"].split(",")
                            feature_details = row["Feature Details"].split(",")

                            # if len(feature_title) == len(feature_details):
                            for i in range(len(feature_title)):
                                try:
                                    if len(feature_details[i]) == 0 or feature_details[i] == '' or feature_details[i] == '\'':
                                        feature_detail = None
                                    elif feature_details[i][0] == "'" and feature_details[i][-1] == "'":
                                        feature_detail = feature_details[i][1:-1]
                                    else:
                                        feature_detail = feature_details[i]
                                except:
                                    feature_detail = None

                                feature_data = {"feature_title": feature_title[i],
                                                "feature_details": feature_detail,
                                                "product": product}
                                Feature.objects.create(**feature_data)

                        # create variants
                        if len(row['Option1 Name']) == 0:
                            option_data = False
                            title = 'Default Title'
                            option1 = 'Default Title'
                            option2 = None
                            option3 = None
                        else:
                            product.has_variants = True
                            product.save()

                            option_data = []
                            if len(row['Option1 Name']) != 0 and len(row['Option2 Name']) != 0 and len(row['Option3 Name']) != 0:
                                option_data.append({'name': row['Option1 Name'], 'values': row['Option1 Value'], 'product':product})
                                option_data.append({'name': row['Option2 Name'], 'values': row['Option2 Value'], 'product':product})
                                option_data.append({'name': row['Option3 Name'], 'values': row['Option3 Value'], 'product':product})

                                title = row['Option1 Value'] + '/' + row['Option2 Value'] + '/' + row['Option3 Value']
                                option1 = row['Option1 Value']
                                option2 = row['Option2 Value']
                                option3 = row['Option3 Value']

                            elif len(row['Option1 Name']) != 0 and len(row['Option2 Name']) != 0:
                                option_data.append({'name': row['Option1 Name'], 'values': row['Option1 Value'], 'product':product})
                                option_data.append({'name': row['Option2 Name'], 'values': row['Option2 Value'], 'product':product})

                                title = row['Option1 Value'] + '/' + row['Option2 Value']
                                option1 = row['Option1 Value']
                                option2 = row['Option2 Value']
                                option3 = None

                            elif len(row['Option1 Name']) != 0:
                                option_data.append({'name': row['Option1 Name'], 'values': row['Option1 Value'], 'product':product})

                                title = row['Option1 Value']
                                option1 = row['Option1 Value']
                                option2 = None
                                option3 = None

                        if not f'{row["Physical Variant"]}'.capitalize():
                            weight = 0.0
                        else:
                            weight = float(row["Variant Weight"])

                        if len(row['Variant Compare At Price']) <= 0 or row['Variant Compare At Price'] == '':
                            row['Variant Compare At Price'] = row['Variant Price']

                        variant_data = {
                            "title": title,
                            "price": row["Variant Price"],
                            "sku": row["variant sku"],
                            "compare_at_price": row["Variant Compare At Price"],
                            "cost_per_item": row["Cost per item"],
                            "option1": option1,
                            "option2": option2,
                            "option3": option3,
                            "barcode": row["Variant Barcode"],
                            "is_physical": f'{row["Physical Variant"]}'.capitalize(),
                            "weight": weight,
                            "inventory_quantity": row["Variant Inventory Qty"],
                            "product": product}

                        Variant.objects.create(**variant_data)

                        if option_data:
                            for option in option_data:
                                Option.objects.create(**option)

                except Exception as e:
                    print(e)
                    print(traceback.format_exc())
                    continue
                    # return Response({'detail': str(e)}, status=422)

            return Response({'detail': 'Inserted'}, status=200)

        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return Response("Failed to upload CSV", status=404)


class ProductMigrationDataUpdate(APIView):
    def put(self, request):
        # file = request.data['file']
        # file = file.read().decode('latin1').splitlines()
        # csv_files = csv.DictReader(file)
        # csv_file = [dict(i) for i in csv_files]

        total_no_of_order = Order.objects.filter(customer_id=251).count()
        orders = Order.objects.filter(customer_id=251)
        total_orders_sum = 0
        for order_obejct in orders:
            total_orders_sum += order_obejct.total_price

        try:
            calculate_points(251, total_no_of_order, total_orders_sum, 1406, 'Unpaid')
        except Exception as e:
            pass
        return Response({'Data inserted Successfully'}, status=200)
