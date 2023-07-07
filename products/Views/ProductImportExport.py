
import csv
import os
import shutil
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from products.BusinessLogic.ElasticSearch import ElasticSearch
from products.BusinessLogic.HideOutOfStock import hide_stock
from products.BusinessLogic.RemoveSpecialCharacters import remove_specialcharacters
from products.models import Product, Variant, Option, Media, Feature, Collection, Tags
from vendor.models import Vendor
from datetime import datetime
from email.mime.text import MIMEText
from django.db import connection, transaction
from email.mime.application import MIMEApplication
from django.core.mail import EmailMultiAlternatives


def send_email(to_email, email_subject, email_template=None, bcc_email=None):
    try:
        to = [to_email]
        email = EmailMultiAlternatives(
            subject=email_subject,
            from_email=settings.EMAIL_HOST_USER,
            to=to,
            bcc=[bcc_email]
        )
        body_part = MIMEText('Product Export', 'plain')
        # Add body to email
        email.attach(body_part)
        # open and read the file in binary
        file_path = os.path.abspath("Products_Export")
        print(file_path)
        with open(file_path + ".zip", 'rb') as file:
            email.attach(MIMEApplication(file.read(), Name='Products_Export.zip'))
        email.send()
        return True
    except Exception as e:
        print(e)
        return False


class ProductExport(APIView):
    def get(self, request):
        ids = self.request.GET.get('ids', None)
        off_set = 0
        limit = 1000
        check_all = True
        csv_sheet_counter = str(0)
        while check_all:
            if ids != 'all':
                string_data = str(ids)
                ids = string_data.split(',')
                products = Product.objects.filter(id__in=ids, deleted=False)[off_set:limit]
                check_all = False
            else:
                products = Product.objects.filter(deleted=False).order_by('id')[off_set:limit]
                off_set += 1000
                limit += 1000

            if products is not None:
                # csv file number
                csv_sheet_counter = str(int(csv_sheet_counter) + 1)

                # making directory
                file_path = os.path.abspath("products/CsvExport/Products_Export")
                if not os.path.isdir(file_path):
                    os.makedirs(file_path)

                with open(file_path + "/product_export_" + csv_sheet_counter + ".csv", "w", encoding='utf-8', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(
                        ['Handle', 'Web Link', 'Title', 'Description', 'Vendor', 'Product Type', 'Cod Available', 'Track Inventory',
                         'Active', 'Hide Out Of Stock', 'Tags', 'Image Src', 'Image Position', 'Warranty',
                         'Feature Title', 'Feature Details', 'Option1 Name', 'Option1 Value', 'Option2 Name',
                         'Option2 Value',
                         'Option3 Name', 'Option3 Value', 'variant_id', 'Variant Sku', 'Variant Weight', 'Variant Inventory Quantity', 'Variant Price',
                         'Variant Compare At Price', 'Variant Cost Per Item', 'Variant Barcode', 'Physical Variant'])

                    # against each product getting its options
                    for product in products:
                        web_link = 'https://kees.qa/' + product.handle
                        # getting title and detail from features
                        features = Feature.objects.filter(product_id=product.id, deleted=False)
                        feature_title = [feature.feature_title for feature in features if
                                         feature.feature_title is not None]
                        feature_detail = [feature.feature_details for feature in features if
                                          feature.feature_details is not None]
                        joined_title = ",".join(feature_title)
                        joined_detail = ",".join(feature_detail)

                        # converting image cdn list to string
                        images = Media.objects.filter(product_id=product.id, deleted=False)
                        cdn_list = [image.cdn_link for image in images]
                        image_position = [str(image.position) for image in images]
                        joined_images = ",".join(cdn_list)
                        image_position = ",".join(image_position)

                        # handling Vendor
                        vendor = Vendor.objects.filter(id=product.vendor_id, deleted=False).first()

                        # product tags
                        tags = Tags.objects.filter(product_tags=product, is_option=False).values_list('name', flat=True)
                        tags = ','.join(tags)

                        # handling options
                        options = Option.objects.filter(product_id=product.id, deleted=False).order_by('id')
                        if len(options) == 1:
                            option1_name = options[0].name
                            option2_name = None
                            option3_name = None
                        elif len(options) == 2:
                            option1_name = options[0].name
                            option2_name = options[1].name
                            option3_name = None
                        elif len(options) == 3:
                            option1_name = options[0].name
                            option2_name = options[1].name
                            option3_name = options[2].name
                        else:
                            option1_name = None
                            option2_name = None
                            option3_name = None

                        counter = 1
                        # handling variants
                        variants = Variant.objects.filter(product_id=product.id, deleted=False)
                        for variant in variants:
                            if variant.option1 == 'Default Title':
                                option1_value = None
                            else:
                                option1_value = variant.option1

                            if counter == 1:
                                writer.writerow(
                                    [product.handle, web_link, product.title, product.description, vendor.name,
                                     product.product_type, product.cod_available, product.track_inventory,
                                     product.is_active,
                                     product.hide_out_of_stock, tags, joined_images, image_position,
                                     product.warranty, joined_title,
                                     joined_detail, option1_name, option1_value, option2_name, variant.option2,
                                     option3_name,
                                     variant.option3, variant.id, variant.sku, variant.weight, variant.inventory_quantity,
                                     variant.price, variant.compare_at_price, variant.cost_per_item,
                                     variant.barcode, variant.is_physical])
                                counter += 1
                            else:
                                writer.writerow(
                                    [product.handle, None, None, None, None, None, None, None, None, None, None, None,
                                     None, None, None,
                                     None, option1_name, variant.option1, option2_name, variant.option2, option3_name,
                                     variant.option3, variant.id, variant.sku, variant.weight,
                                     variant.inventory_quantity, variant.price, variant.compare_at_price,
                                     variant.cost_per_item, variant.barcode, variant.is_physical])
            if products.count() < 1000:
                break
        file_path = os.path.abspath("products/CsvExport/Products_Export")
        shutil.make_archive('Products_Export', 'zip', file_path)
        email = self.request.user.email
        send_email(
            to_email=email,
            email_subject="Products Export",
        )
        zip_path = os.path.abspath("Products_Export")
        if os.path.exists(file_path):
            shutil.rmtree(file_path)
        else:
            print("File not found in the directory")
        if os.path.exists(zip_path+".zip"):
            os.remove(zip_path+".zip")
        else:
            print("zip file not found")
        return Response({'detail': 'Product Send on Email'}, status=200)


def create_variant(row, product, variant_id=None):
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
            option_data.append({'name': row['Option1 Name'], 'values': row['Option1 Value'], 'product': product})
            option_data.append({'name': row['Option2 Name'], 'values': row['Option2 Value'], 'product': product})
            option_data.append({'name': row['Option3 Name'], 'values': row['Option3 Value'], 'product': product})

            title = row['Option1 Value'] + '/' + row['Option2 Value'] + '/' + row['Option3 Value']
            option1 = row['Option1 Value']
            option2 = row['Option2 Value']
            option3 = row['Option3 Value']

        elif len(row['Option1 Name']) != 0 and len(row['Option2 Name']) != 0:
            option_data.append({'name': row['Option1 Name'], 'values': row['Option1 Value'], 'product': product})
            option_data.append({'name': row['Option2 Name'], 'values': row['Option2 Value'], 'product': product})

            title = row['Option1 Value'] + '/' + row['Option2 Value']
            option1 = row['Option1 Value']
            option2 = row['Option2 Value']
            option3 = None

        elif len(row['Option1 Name']) != 0:
            option_data.append({'name': row['Option1 Name'], 'values': row['Option1 Value'], 'product': product})

            title = row['Option1 Value']
            option1 = row['Option1 Value']
            option2 = None
            option3 = None

        else:
            title = 'Default Title'
            option1 = 'Default Title'
            option2 = None
            option3 = None

    if not f'{row["Physical Variant"]}'.capitalize():
        weight = 0.0
    else:
        weight = float(row["Variant Weight"])

    if len(row['Variant Compare At Price']) <= 0 or row['Variant Compare At Price'] == '' or row['Variant Compare At Price'] < row['Variant Price']:
        row['Variant Compare At Price'] = row['Variant Price']

    variant_data = {
        "title": title,
        "price": row["Variant Price"],
        "sku": row["Variant Sku"],
        "compare_at_price": row["Variant Compare At Price"],
        "cost_per_item": row["Variant Cost Per Item"],
        "option1": option1,
        "option2": option2,
        "option3": option3,
        "barcode": row["Variant Barcode"],
        "is_physical": f'{row["Physical Variant"]}'.capitalize(),
        "weight": weight,
        "inventory_quantity": row["Variant Inventory Quantity"],
        "product": product}

    if variant_id is not None:
        variant_data['id'] = variant_id

    Variant.objects.create(**variant_data)
    if option_data:
        for option in option_data:
            Option.objects.create(**option)


def remove_duplicate_optionvalues(product):
    options = Option.objects.filter(product=product, deleted=False)
    for option in options:
        option_value = option.values.split(',')
        option_value = list(dict.fromkeys(option_value))
        option_value = ','.join(option_value)
        Option.values = option_value
        option.save()


class ProductImport(APIView):
    # @transaction.atomic
    def post(self, request):
        try:
            file = request.data['file']
            file = file.read().decode('utf-8-sig').splitlines()
            csv_files = csv.DictReader(file)
            csv_file = [dict(i) for i in csv_files]
            error_list = []

            cursor = connection.cursor()
            cursor.execute('''set foreign_key_checks=0;''')
            bl = ElasticSearch()
            product_ids_lst = []

            for row in csv_file:
                try:
                    row['Handle'] = remove_specialcharacters(row['Handle'].replace(' ', '-').lower())
                    handle = row['Handle']
                    product = Product.objects.filter(handle=handle, deleted=False).first()

                    # check vendor
                    if len(row['Vendor']) > 0 and row['Vendor'] != '':
                        vendor_name = row["Vendor"]
                        vendor_lower = vendor_name.lower()
                        vendor = Vendor.objects.filter(name__iexact=vendor_lower).first()
                        if not vendor:
                            continue
                    else:
                        vendor = None

                    if product:
                        if len(row['Vendor']) > 0 and row['Vendor'] != '':
                            if vendor:
                                # delete media
                                Media.objects.filter(product_id=product.id, deleted=False).delete()

                                # create media
                                media = row["Image Src"]
                                image_position = row["Image Position"].split(',')

                                if media:
                                    urls_list = media.split(',')

                                    for count, url in enumerate(urls_list):
                                        try:
                                            position = image_position[count]
                                        except Exception as e:
                                            print(e)
                                            position = None

                                        media_data = {}
                                        url_split = url.split('/')
                                        if url_split:
                                            media_data["cdn_link"] = url
                                            media_data["file_name"] = url_split[-1]
                                            media_data["position"] = position
                                            media_data["product"] = product
                                            Media.objects.create(**media_data)

                                # Delete features
                                Feature.objects.filter(product_id=product.id, deleted=False).delete()

                                # create features
                                if (len(row['Feature Title']) > 0 and row['Feature Title'] != '') and \
                                        (len(row['Feature Details']) > 0 and row['Feature Details'] != ''):
                                    feature_title = row["Feature Title"].split(",")
                                    feature_details = row["Feature Details"].split(",")

                                    for i in range(len(feature_title)):
                                        try:
                                            if len(feature_details[i]) == 0 or feature_details[i] == '' or \
                                                    feature_details[i] == '\'':
                                                feature_detail = None
                                            elif feature_details[i][0] == "'" and feature_details[i][-1] == "'":
                                                feature_detail = feature_details[i][1:-1]
                                            else:
                                                feature_detail = feature_details[i]
                                        except Exception as e:
                                            print(e)
                                            feature_detail = None

                                        feature_data = {"feature_title": feature_title[i],
                                                        "feature_details": feature_detail,
                                                        "product": product}
                                        Feature.objects.create(**feature_data)

                                variant_id = row['variant_id']
                                Variant.objects.filter(product_id=product.id).delete()
                                Option.objects.filter(product_id=product.id).delete()

                                try:
                                    create_variant(row, product, variant_id)
                                except Exception as e:
                                    print(e)
                                    Product.objects.filter(id=product.id).update(deleted=True, deleted_at=datetime.now())
                                    continue

                                remove_duplicate_optionvalues(product)
                                hide_stock(product)

                                # update product
                                product_update = {
                                    "title": row["Title"],
                                    "description": row["Description"],
                                    "product_type": row["Product Type"],
                                    "cod_available": f'{row["Cod Available"]}'.capitalize(),
                                    "handle": row["Handle"],
                                    "track_inventory": f'{row["Track Inventory"]}'.capitalize(),
                                    "is_active": f'{row["Active"]}'.capitalize(),
                                    'warranty': row['Warranty'],
                                    "status": 'Approved',
                                    "has_variants": 'False',
                                    "hide_out_of_stock": f'{row["Hide Out Of Stock"]}'.capitalize(),
                                    "vendor": vendor,
                                }
                                Product.objects.filter(id=product.id, deleted=False).update(**product_update)
                            else:
                                # remove attachments in case of vendor does not exist
                                Product.objects.filter(id=product.id).update(product_group_id=None)
                                collections = Collection.objects.filter(product__collection__product=product).distinct()
                                for collection in collections:
                                    product.collection.remove(collection)

                        else:
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

                                        if len(row['Option2 Name']) > 0:
                                            if row['Option2 Name'] == single_option.name:
                                                if len(row['Option2 Value']) != 0:
                                                    option_values = single_option.values
                                                    option_values = option_values.split(',')
                                                    check_option = [row['Option2 Value'] for i in option_values if
                                                                    row['Option2 Value'] != i]
                                                    if check_option:
                                                        single_option_object = Option.objects.filter(
                                                            id=single_option.id).first()
                                                        option_values.append(check_option[0])
                                                        single_option_object.values = ",".join(option_values)
                                                        single_option_object.save()

                                        if len(row['Option3 Name']) > 0:
                                            if row['Option3 Name'] == single_option.name:
                                                if len(row['Option3 Value']) != 0:
                                                    option_values = single_option.values
                                                    option_values = option_values.split(',')
                                                    check_option = [row['Option3 Value'] for i in option_values if
                                                                    row['Option3 Value'] != i]
                                                    if check_option:
                                                        single_option_object = Option.objects.filter(
                                                            id=single_option.id).first()
                                                        option_values.append(check_option[0])
                                                        single_option_object.values = ",".join(option_values)
                                                        single_option_object.save()

                            if len(row['Option1 Name']) != 0 and len(row['Option2 Name']) != 0 and len(
                                    row['Option3 Name']) != 0:
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

                            else:
                                title = 'Default Title'
                                option1 = 'Default Title'
                                option2 = None
                                option3 = None
                                product.has_variants = False
                                product.save()

                            if not f'{row["Physical Variant"]}'.capitalize():
                                weight = 0
                            else:
                                weight = row["Variant Weight"]

                            if len(row['Variant Compare At Price']) <= 0 or row['Variant Compare At Price'] == '' or row['Variant Compare At Price'] < row['Variant Price']:
                                row['Variant Compare At Price'] = row['Variant Price']

                            variant_data = {
                                "title": title,
                                "price": row["Variant Price"],
                                "sku": row["Variant Sku"],
                                "compare_at_price": row["Variant Compare At Price"],
                                "cost_per_item": row["Variant Cost Per Item"],
                                "option1": option1,
                                "option2": option2,
                                "option3": option3,
                                "barcode": row["Variant Barcode"],
                                "is_physical": f'{row["Physical Variant"]}'.capitalize(),
                                "weight": weight,
                                "inventory_quantity": row["Variant Inventory Quantity"],
                                "product": product}

                            Variant.objects.create(**variant_data)
                            # create_variant(row, product)
                            remove_duplicate_optionvalues(product)
                            hide_stock(product)

                        product_ids_lst.append(product.id)

                    else:
                        # create product
                        product_data = {
                            "title": row["Title"],
                            "description": row["Description"],
                            "product_type": row["Product Type"],
                            "cod_available": f'{row["Cod Available"]}'.capitalize(),
                            "handle": row["Handle"],
                            "track_inventory": f'{row["Track Inventory"]}'.capitalize(),
                            "is_active": 'False',
                            "status": 'Approved',
                            "warranty": row['Warranty'],
                            "vendor": vendor,
                        }
                        product = Product.objects.create(**product_data)

                        # create media
                        media = row["Image Src"]
                        image_position = row["Image Position"].split(',')

                        if media:
                            urls_list = media.split(',')

                            for count, url in enumerate(urls_list):
                                try:
                                    position = image_position[count]
                                except Exception as e:
                                    print(e)
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
                        if (len(row['Feature Title']) > 0 and row['Feature Title'] != '') and \
                                (len(row['Feature Details']) > 0 and row['Feature Details'] != ''):
                            feature_title = row["Feature Title"].split(",")
                            feature_details = row["Feature Details"].split(",")

                            for i in range(len(feature_title)):
                                try:
                                    if len(feature_details[i]) == 0 or feature_details[i] == '' or \
                                            feature_details[i] == '\'':
                                        feature_detail = None
                                    elif feature_details[i][0] == "'" and feature_details[i][-1] == "'":
                                        feature_detail = feature_details[i][1:-1]
                                    else:
                                        feature_detail = feature_details[i]
                                except Exception as e:
                                    print(e)
                                    feature_detail = None

                                feature_data = {"feature_title": feature_title[i],
                                                "feature_details": feature_detail,
                                                "product": product}
                                Feature.objects.create(**feature_data)

                        create_variant(row, product)
                        remove_duplicate_optionvalues(product)
                        hide_stock(product)
                        product_ids_lst.append(product.id)

                    bl.bulk_pagination(product_ids_lst)

                except Exception as e:
                    print(e)
                    # error_list.append(str(e))
                    # print(traceback.format_exc())
                    # continue

            # if len(error_list) > 0:
            #     return Response({'detail': error_list}, status=402)
            return Response({'detail': 'Inserted'}, status=200)
        except Exception as e:
            print(e)
            return Response("Failed to upload CSV", status=404)
