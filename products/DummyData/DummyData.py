
import boto3, csv, requests, os, glob
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from products.models import Media, Product
from cms.models import StoreFilter
from cms.Serializers.PriceRangeSerializer import PriceFilterSerializer
from cms.Serializers.StoreFilterSerializer import StoreFilterSerializer
from products.Serializers.BrandSerializer import AddBrandSerializer
from products.Serializers.ProductSerializer import AddProductSerializer
from products.Serializers.ProductGroupSerializer import ProductGroupSerializer
from products.Serializers.CollectionSerializer import CollectionAddSerializer
from vendor.Serializers.VendorSerializer import DummyDataInsertSerializer
from setting.Serializers.StoreInfoSerializer import StoreInfoSerializer
from setting.models import StoreInformation
from products.Serializers.CategorySerializer import MainCategoryAddUpdateSerializer, SubCategoryAddUpdateSerializer, \
    SuperSubCategoryAddUpdateSerializer
from authentication.BusinessLogic.ApiPermissions import AccessApi
from rest_framework import exceptions


class DummyDataInsert(APIView):

    @swagger_auto_schema(responses={200: AddProductSerializer}, request_body=AddProductSerializer)
    def post(self, request):
        access = AccessApi(self.request.user, "products")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        store_information = {
            "store_name": "Alchemative",
            "store_contact_email": "Alchemative@gmail.com",
            "sender_email": "Alchemative@gmail.com",
            "store_industry": "Software",
            "company_name": "Alchemative",
            "phone_number": "03117865432",
            "address1": "Vogue Tower MMAlam Road",
            "address2": "Gulberg 3",
            "country": "Qatar",
            "postal_code": "54000",
            "time_zone": "Qatar (GMT+3)",
            "unit_system": "Standard",
            "weight_units": "kg",
            "main_order_prefix": "1000",
            "split_order_prefix": "1",
            "store_currency": "QAR"
        }

        storefilter = {
            "price": "True",
            "collection": "True",
            "brand": "True"
        }

        price_range_data = [
            {"min_price": "0", "max_price": "2000"},
            {"min_price": "2000", "max_price": "4000"},
            {"min_price": "4000", "max_price": "6000"},
            {"min_price": "6000", "max_price": "8000"},
            {"min_price": "8000", "max_price": "10000"}
        ]

        vendor_data = [
            {'name': 'kosac', 'email': 'kosact@comcast.net', 'phone': '+1-202-555-0103', 'city': 'lahore',
             'address': 'Gulberg 1', 'tax': '10', 'commercial_registration': '23000',
             'notes': 'Lorem Ipsum is simply dummy text of the printing and typesetting industry.'},
            {'name': 'dmouse', 'email': 'dmouse@verizon.net', 'phone': '+1-202-555-0149', 'city': 'Karachi',
             'address': 'Gulberg 2', 'tax': '10', 'commercial_registration': '34000',
             'notes': 'Lorem Ipsum is simply dummy text of the printing and typesetting industry.'},
            {'name': 'lishoy', 'email': 'lishoy@comcast.net', 'phone': '+1-202-555-0175', 'city': 'Islamabad',
             'address': 'Gulberg 4', 'tax': '10', 'commercial_registration': '56000',
             'notes': 'Lorem Ipsum is simply dummy text of the printing and typesetting industry.'},
            {'name': 'yenya', 'email': 'yenya@verizon.net', 'phone': '+1-202-555-0167', 'city': 'Sialkot',
             'address': 'Gulberg 5', 'tax': '10', 'commercial_registration': '6000',
             'notes': 'Lorem Ipsum is simply dummy text of the printing and typesetting industry.'},
            {'name': 'mobileip', 'email': 'mobileip@mac.com', 'phone': '+1-626-555-0104', 'city': 'Jhang',
             'address': 'Gulberg 6', 'tax': '10', 'commercial_registration': '9000',
             'notes': 'Lorem Ipsum is simply dummy text of the printing and typesetting industry.'},
            {'name': 'thaljef', 'email': 'thaljef@mac.com', 'phone': '+1-626-555-0143', 'city': 'Faisalabad',
             'address': 'Gulberg 7', 'tax': '10', 'commercial_registration': '29000',
             'notes': 'Lorem Ipsum is simply dummy text of the printing and typesetting industry.'},
            {'name': 'cgreuter', 'email': 'cgreuter@comcast.net', 'phone': '+1-626-555-0142', 'city': 'Gilgit',
             'address': 'Gulberg 8', 'tax': '10', 'commercial_registration': '914000',
             'notes': 'Lorem Ipsum is simply dummy text of the printing and typesetting industry.'},
            {'name': 'nicktrig', 'email': 'nicktrig@comcast.net', 'phone': '+1-626-555-0111', 'city': 'Skardu',
             'address': 'Gulberg 9', 'tax': '10', 'commercial_registration': '13000',
             'notes': 'Lorem Ipsum is simply dummy text of the printing and typesetting industry.'},
            {'name': 'jsbach', 'email': 'jsbach@att.net', 'phone': '+1-626-555-0164', 'city': 'lahore',
             'address': 'Gulberg 10', 'tax': '10', 'commercial_registration': '1300',
             'notes': 'Lorem Ipsum is simply dummy text of the printing and typesetting industry.'},
        ]

        product_brand = [
            {"name": "Apple"},
            {"name": "Google"},
            {"name": "Microsoft"},
            {"name": "Amazon"},
            {"name": "Facebook"},
            {"name": "Disney"},
            {"name": "Samsung"},
            {"name": "Intel"},
            {"name": "Cisco"},
            {"name": "Oracle"}
        ]

        product_group_data = [
            {"title": "Smartphone", "vendor": 1},
            {"title": "Laptop", "vendor": 1},
            {"title": "Electronics", "vendor": 1},
            {"title": "Health", "vendor": 2},
            {"title": "T-shirt", "vendor": 2},
            {"title": "Shirts", "vendor": 2},
            {"title": "Bikes", "vendor": 3},
            {"title": "Cars", "vendor": 4},
            {"title": "Shoes", "vendor": 5},
            {"title": "Glasses", "vendor": 5},
            {"title": "Caps", "vendor": 5},
            {"title": "Groceries", "vendor": 6},
            {"title": "Kitchen Accessories", "vendor": 6},
            {"title": "Supplements", "vendor": 7},
            {"title": "Furniture", "vendor": 8},
        ]

        main_category_data = [
            {"name": "Electronic Devices", "description": "devices", "availability": True, "is_active": True,
             "status": "Approved", "slug": "main_category",
             "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]},
            {"name": "Electronic Accessories", "description": "Accessories","is_active": True,
             "status": "Approved", "availability": True,
             "slug": "main_category",
             "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]},
            {"name": "Health & Beauty", "description": "Beauty", "is_active": True,
             "status": "Approved", "availability": True, "slug": "main_category",
             "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]},
            {"name": "Groceries & Pets", "description": "Groceries", "is_active": True,
             "status": "Approved", "availability": True, "slug": "main_category",
             "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]},
            {"name": "Home & Lifestyle", "description": "Lifestyle", "is_active": True,
             "status": "Approved", "availability": True, "slug": "main_category",
             "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]},
            {"name": "Men's Fashion", "description": "Fashion", "is_active": True,
             "status": "Approved", "availability": True, "slug": "main_category",
             "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]},
            {"name": "Women's Fashion", "description": "Fashion", "is_active": True,
             "status": "Approved", "availability": True, "slug": "main_category",
             "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]},
            {"name": "Watches & Bags", "description": "Bags", "is_active": True,
             "status": "Approved", "availability": True, "slug": "main_category",
             "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]},
            {"name": "Sports", "description": "Sports", "is_active": True,
             "status": "Approved", "availability": True, "slug": "main_category",
             "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]}
        ]

        sub_category_data = [
            {"name": "Smart Phone", "description": "devices", "main_category": "1", "availability": True, "is_active": True,
             "status": "Approved",
             "slug": "sub_category", "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]},
            {"name": "Feature phone", "description": "devices", "is_active": True,
             "status": "Approved", "main_category": "1", "availability": True,
             "slug": "sub_category", "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]},
            {"name": "Tablets", "description": "devices", "is_active": True,
             "status": "Approved", "main_category": "1", "availability": True,
             "slug": "sub_category", "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]},

            {"name": "Mobile Accessories", "description": "devices", "is_active": True,
             "status": "Approved", "main_category": "2", "availability": True,
             "slug": "sub_category", "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]},
            {"name": "Storage", "description": "devices", "is_active": True,
             "status": "Approved", "main_category": "2", "availability": True,
             "slug": "sub_category", "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]},
            {"name": "Computer Components", "description": "devices", "is_active": True,
             "status": "Approved", "main_category": "2", "availability": True,
             "slug": "sub_category", "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]},
            {"name": "Portable Speakers", "description": "devices", "is_active": True,
             "status": "Approved", "main_category": "2", "availability": True,
             "slug": "sub_category", "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]},

            {"name": "Beauty Tools", "description": "Beauty", "is_active": True,
             "status": "Approved", "main_category": "3", "availability": True,
             "slug": "sub_category", "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]},
            {"name": "Hair Care", "description": "Beauty", "is_active": True,
             "status": "Approved", "main_category": "3", "availability": True,
             "slug": "sub_category", "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]},

            {"name": "Fresh Products", "description": "Fashion", "is_active": True,
             "status": "Approved", "main_category": "4", "availability": True,
             "slug": "sub_category", "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]},
            {"name": "BreakFast", "description": "Fashion", "is_active": True,
             "status": "Approved", "main_category": "4", "availability": True,
             "slug": "sub_category", "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]},
            {"name": "Dairy & Chilled", "description": "Fashion", "is_active": True,
             "status": "Approved", "main_category": "4", "availability": True,
             "slug": "sub_category", "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]},

            {"name": "Furniture", "description": "Fashion", "is_active": True,
             "status": "Approved", "main_category": "5", "availability": True,
             "slug": "sub_category", "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]},
            {"name": "Lighting", "description": "Fashion", "is_active": True,
             "status": "Approved", "main_category": "5", "availability": True,
             "slug": "sub_category", "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]},

            {"name": "T-Shirts", "description": "Fashion", "is_active": True,
             "status": "Approved", "main_category": "6", "availability": True,
             "slug": "sub_category", "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]},
            {"name": "Shoes", "description": "Fashion", "is_active": True,
             "status": "Approved", "main_category": "6", "availability": True,
             "slug": "sub_category", "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]},
            {"name": "Jeans", "description": "Fashion", "is_active": True,
             "status": "Approved", "main_category": "6", "availability": True,
             "slug": "sub_category", "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]},
            {"name": "Kurtas", "description": "Fashion", "is_active": True,
             "status": "Approved", "main_category": "6", "availability": True,
             "slug": "sub_category", "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]},

            {"name": "Muslim Wear", "description": "Fashion", "is_active": True,
             "status": "Approved", "main_category": "7", "availability": True,
             "slug": "sub_category", "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]},
            {"name": "Tops", "description": "Fashion", "is_active": True,
             "status": "Approved", "main_category": "7", "availability": True,
             "slug": "sub_category", "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]},
            {"name": "Winter Clothing", "description": "Fashion", "is_active": True,
             "status": "Approved", "main_category": "7", "availability": True,
             "slug": "sub_category", "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]},

            {"name": "Men Watches", "description": "Fashion", "is_active": True,
             "status": "Approved", "main_category": "8", "availability": True,
             "slug": "sub_category", "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]},
            {"name": "Women Watches", "description": "Fashion", "is_active": True,
             "status": "Approved", "main_category": "8", "availability": True,
             "slug": "sub_category", "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]},
            {"name": "Kids Watches", "description": "Fashion", "is_active": True,
             "status": "Approved", "main_category": "8", "availability": True,
             "slug": "sub_category", "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]},

            {"name": "Fitness Gadgets", "description": "Fashion", "is_active": True,
             "status": "Approved", "main_category": "9", "availability": True,
             "slug": "sub_category", "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]},
            {"name": "Supplements", "description": "Fashion", "is_active": True,
             "status": "Approved", "main_category": "9", "availability": True,
             "slug": "sub_category", "seo_title": "", "seo_description": "", "meta_data": [{"field": "", "value": ""}]}
        ]

        super_sub_category_data = [
            {"name": "Nokia Phone", "description": "devices", "is_active": True,
             "status": "Approved", "sub_category": "1", "availability": True,
             "slug": "super_sub_category", "seo_title": "", "seo_description": "",
             "meta_data": [{"field": "", "value": ""}]},
            {"name": "Apple phone", "description": "devices", "is_active": True,
             "status": "Approved", "sub_category": "1", "availability": True,
             "slug": "super_sub_category", "seo_title": "", "seo_description": "",
             "meta_data": [{"field": "", "value": ""}]},

            {"name": "Phone Case", "description": "devices", "is_active": True,
             "status": "Approved", "sub_category": "4", "availability": True,
             "slug": "super_sub_category", "seo_title": "", "seo_description": "",
             "meta_data": [{"field": "", "value": ""}]},
            {"name": "Power Banks", "description": "devices", "is_active": True,
             "status": "Approved", "sub_category": "4", "availability": True,
             "slug": "super_sub_category", "seo_title": "", "seo_description": "",
             "meta_data": [{"field": "", "value": ""}]},

            {"name": "Graphics Cards", "description": "devices", "is_active": True,
             "status": "Approved", "sub_category": "5", "availability": True,
             "slug": "super_sub_category", "seo_title": "", "seo_description": "",
             "meta_data": [{"field": "", "value": ""}]},
            {"name": "Processors", "description": "devices", "is_active": True,
             "status": "Approved", "sub_category": "5", "availability": True,
             "slug": "super_sub_category", "seo_title": "", "seo_description": "",
             "meta_data": [{"field": "", "value": ""}]},

            {"name": "Flat Irons", "description": "Beauty", "is_active": True,
             "status": "Approved", "sub_category": "8", "availability": True,
             "slug": "super_sub_category", "seo_title": "", "seo_description": "",
             "meta_data": [{"field": "", "value": ""}]},
            {"name": "Hair Dryers", "description": "Beauty", "is_active": True,
             "status": "Approved", "sub_category": "8", "availability": True,
             "slug": "super_sub_category", "seo_title": "", "seo_description": "",
             "meta_data": [{"field": "", "value": ""}]},

            {"name": "Fresh Fruit", "description": "Fashion", "is_active": True,
             "status": "Approved", "sub_category": "10", "availability": True,
             "slug": "super_sub_category", "seo_title": "", "seo_description": "",
             "meta_data": [{"field": "", "value": ""}]},
            {"name": "Biscuit", "description": "Fashion", "is_active": True,
             "status": "Approved", "sub_category": "11", "availability": True,
             "slug": "super_sub_category", "seo_title": "", "seo_description": "",
             "meta_data": [{"field": "", "value": ""}]},

            {"name": "Bedroom", "description": "Fashion", "is_active": True,
             "status": "Approved", "sub_category": "13", "availability": True,
             "slug": "super_sub_category", "seo_title": "", "seo_description": "",
             "meta_data": [{"field": "", "value": ""}]},
            {"name": "Floor Lamps", "description": "Fashion", "is_active": True,
             "status": "Approved", "sub_category": "14", "availability": True,
             "slug": "super_sub_category", "seo_title": "", "seo_description": "",
             "meta_data": [{"field": "", "value": ""}]},

            {"name": "V-neck", "description": "Fashion", "is_active": True,
             "status": "Approved", "sub_category": "15", "availability": True,
             "slug": "super_sub_category", "seo_title": "", "seo_description": "",
             "meta_data": [{"field": "", "value": ""}]},
            {"name": "Sneakers", "description": "Fashion", "is_active": True,
             "status": "Approved", "sub_category": "16", "availability": True,
             "slug": "super_sub_category", "seo_title": "", "seo_description": "",
             "meta_data": [{"field": "", "value": ""}]},
            {"name": "Cargo", "description": "Fashion", "is_active": True,
             "status": "Approved", "sub_category": "17", "availability": True,
             "slug": "super_sub_category", "seo_title": "", "seo_description": "",
             "meta_data": [{"field": "", "value": ""}]},
            {"name": "Unstitched Fabrics", "description": "Fashion", "is_active": True,
             "status": "Approved", "sub_category": "18", "availability": True,
             "slug": "super_sub_category", "seo_title": "", "seo_description": "",
             "meta_data": [{"field": "", "value": ""}]},

            {"name": "Abayas", "description": "Fashion", "is_active": True,
             "status": "Approved", "sub_category": "19", "availability": True,
             "slug": "super_sub_category", "seo_title": "", "seo_description": "",
             "meta_data": [{"field": "", "value": ""}]},
            {"name": "T-Shirts", "description": "Fashion", "is_active": True,
             "status": "Approved", "sub_category": "20", "availability": True,
             "slug": "super_sub_category", "seo_title": "", "seo_description": "",
             "meta_data": [{"field": "", "value": ""}]},
            {"name": "Jackets", "description": "Fashion", "is_active": True,
             "status": "Approved", "sub_category": "21", "availability": True,
             "slug": "super_sub_category", "seo_title": "", "seo_description": "",
             "meta_data": [{"field": "", "value": ""}]},

            {"name": "Digital", "description": "Fashion", "is_active": True,
             "status": "Approved", "sub_category": "22", "availability": True,
             "slug": "super_sub_category", "seo_title": "", "seo_description": "",
             "meta_data": [{"field": "", "value": ""}]},
            {"name": "Digital", "description": "Fashion", "is_active": True,
             "status": "Approved", "sub_category": "23", "availability": True,
             "slug": "super_sub_category", "seo_title": "", "seo_description": "",
             "meta_data": [{"field": "", "value": ""}]},
            {"name": "Digital", "description": "Fashion", "is_active": True,
             "status": "Approved", "sub_category": "24", "availability": True,
             "slug": "super_sub_category", "seo_title": "", "seo_description": "",
             "meta_data": [{"field": "", "value": ""}]},

            {"name": "Trackers", "description": "Fashion", "is_active": True,
             "status": "Approved", "sub_category": "25", "availability": True,
             "slug": "super_sub_category", "seo_title": "", "seo_description": "",
             "meta_data": [{"field": "", "value": ""}]},
            {"name": "Proteins", "description": "Fashion", "is_active": True,
             "status": "Approved", "sub_category": "26", "availability": True,
             "slug": "super_sub_category", "seo_title": "", "seo_description": "",
             "meta_data": [{"field": "", "value": ""}]}
        ]

        collection_data = [
            {"meta_data": [{"field": "", "value": ""}],
             "title": "Best for Men", "description": "",
             "slug": "best-for-men", "seo_title": "", "seo_description": "",
             "is_active": True,
             "status": "Approved",
             "vendor": "1",
             "main_category": [6],
             "sub_category": [15, 16, 17, 18],
             "super_sub_category": [13]},

            {"meta_data": [{"field": "", "value": ""}],
             "title": "Style the Phone", "description": "",
             "slug": "style-the-phone", "seo_title": "", "seo_description": "",
             "is_active": True,
             "status": "Approved",
             "vendor": "1",
             "main_category": [2],
             "sub_category": [1, 2, 3],
             "super_sub_category": [1, 2, 3]},

            {"meta_data": [{"field": "", "value": ""}],
             "title": "Dress Well", "description": "",
             "slug": "dress-well", "seo_title": "", "seo_description": "",
             "is_active": True,
             "status": "Approved",
             "vendor": "2",
             "main_category": [6, 7],
             "sub_category": [18, 19],
             "super_sub_category": [17]},

            {"meta_data": [{"field": "", "value": ""}],
             "title": "Beauty Full", "description": "",
             "slug": "beauty-full", "seo_title": "", "seo_description": "",
             "is_active": True,
             "status": "Approved",
             "vendor": "2",
             "main_category": [3],
             "sub_category": [8, 9],
             "super_sub_category": [7, 8]},

            {"meta_data": [{"field": "", "value": ""}],
             "title": "Bestest Outfits", "description": "",
             "slug": "bestest-outfits", "seo_title": "", "seo_description": "",
             "is_active": True,
             "status": "Approved",
             "vendor": "2",
             "main_category": [6, 7],
             "sub_category": [17, 20],
             "super_sub_category": [18, 19]},

            {"meta_data": [{"field": "", "value": ""}],
             "title": "Muslim Clothing", "description": "",
             "slug": "muslim-clothing", "seo_title": "", "seo_description": "",
             "is_active": True,
             "status": "Approved",
             "vendor": "3",
             "main_category": [],
             "sub_category": [19],
             "super_sub_category": [17]},

            {"meta_data": [{"field": "", "value": ""}],
             "title": "Home Furniture", "description": "",
             "slug": "home-furniture", "seo_title": "", "seo_description": "",
             "is_active": True,
             "status": "Approved",
             "vendor": "3",
             "main_category": [],
             "sub_category": [13],
             "super_sub_category": [11]},

            {"meta_data": [{"field": "", "value": ""}],
             "title": "Western for Women", "description": "",
             "slug": "western-for-women", "seo_title": "", "seo_description": "",
             "is_active": True,
             "status": "Approved",
             "vendor": "4",
             "main_category": [7],
             "sub_category": [20, 21],
             "super_sub_category": [18]},

            {"meta_data": [{"field": "", "value": ""}],
             "title": "Fashion Star", "description": "",
             "slug": "fashion-star", "seo_title": "", "seo_description": "",
             "is_active": True,
             "status": "Approved",
             "vendor": "5",
             "main_category": [8],
             "sub_category": [20, 21, 22, 23, 24],
             "super_sub_category": [19, 20, 21, 22]},

            {"meta_data": [{"field": "", "value": ""}],
             "title": "Global Items", "description": "",
             "slug": "global-items", "seo_title": "", "seo_description": "",
             "is_active": True,
             "status": "Approved",
             "vendor": "5",
             "main_category": [],
             "sub_category": [3, 7, 25],
             "super_sub_category": [24]},

            {"meta_data": [{"field": "", "value": ""}],
             "title": "Traveling Things", "description": "",
             "slug": "traveling-things", "seo_title": "", "seo_description": "",
             "is_active": True,
             "status": "Approved",
             "vendor": "6",
             "main_category": [],
             "sub_category": [4, 5],
             "super_sub_category": [2, 4, 8, 19]},

            {"meta_data": [{"field": "", "value": ""}],
             "title": "Decorate Home", "description": "",
             "slug": "decorate-home", "seo_title": "", "seo_description": "",
             "is_active": True,
             "status": "Approved",
             "vendor": "7",
             "main_category": [5],
             "sub_category": [13, 14],
             "super_sub_category": [11, 12]},

            {"meta_data": [{"field": "", "value": ""}],
             "title": "Love Collections", "description": "",
             "slug": "love-collections", "seo_title": "", "seo_description": "",
             "is_active": True,
             "status": "Approved",
             "vendor": "7",
             "main_category": [1, 2],
             "sub_category": [4, 5, 9, 16, 25],
             "super_sub_category": [4, 5, 14, 24]},

            {"meta_data": [{"field": "", "value": ""}],
             "title": "Have Smart Life", "description": "",
             "slug": "smart-life", "seo_title": "", "seo_description": "",
             "is_active": True,
             "status": "Approved",
             "vendor": "8",
             "main_category": [1, 2],
             "sub_category": [1, 2, 3, 4, 5, 6, 7],
             "super_sub_category": [4, 8, 20, 21, 22]},

            {"meta_data": [{"field": "", "value": ""}],
             "title": "Yummy", "description": "",
             "slug": "vegetable-oil", "seo_title": "", "seo_description": "",
             "is_active": True,
             "status": "Approved",
             "vendor": "9",
             "main_category": [5],
             "sub_category": [10, 11, 12],
             "super_sub_category": [9, 10]}
        ]

        try:
            StoreInformation.objects.get(deleted=False)
        except Exception as e:
            print(e)
            store = StoreInfoSerializer(data=store_information)
            if store.is_valid(raise_exception=True):
                store.save()
            else:
                return Response(store.errors, status=422)

        query_set = StoreFilter.objects.filter(deleted=False).first()
        if not query_set:
            store_filter = StoreFilterSerializer(data=storefilter)
            if store_filter.is_valid(raise_exception=True):
                store_filter.save()
            else:
                return Response(store_filter.errors, status=422)

        for price in price_range_data:
            price_range = PriceFilterSerializer(data=price)
            if price_range.is_valid(raise_exception=True):
                price_range.save()
            else:
                return Response(price_range.errors, status=422)

        for i in vendor_data:
            vendor = DummyDataInsertSerializer(data=i)
            if vendor.is_valid(raise_exception=True):
                vendor.save()
            else:
                return Response(vendor.errors, status=422)

        for i in product_brand:
            brand = AddBrandSerializer(data=i)
            if brand.is_valid(raise_exception=True):
                brand.save()
            else:
                return Response(brand.errors, status=422)

        for i in product_group_data:
            product_group = ProductGroupSerializer(data=i)
            if product_group.is_valid(raise_exception=True):
                product_group.save()
            else:
                return Response(product_group.errors, status=422)

        for i in main_category_data:
            main_category = MainCategoryAddUpdateSerializer(data=i)
            if main_category.is_valid(raise_exception=True):
                main_category.save()
            else:
                return Response(main_category.errors, status=422)

        for i in sub_category_data:
            sub_category = SubCategoryAddUpdateSerializer(data=i)
            if sub_category.is_valid(raise_exception=True):
                sub_category.save()
            else:
                return Response(sub_category.errors, status=422)

        for i in super_sub_category_data:
            super_sub_category = SuperSubCategoryAddUpdateSerializer(data=i)
            if super_sub_category.is_valid(raise_exception=True):
                super_sub_category.save()
            else:
                return Response(super_sub_category.errors, status=422)

        for i in collection_data:
            collection = CollectionAddSerializer(data=i)
            if collection.is_valid(raise_exception=True):
                collection.save()
            else:
                return Response(collection.errors, status=422)

        with open('products/DummyData/product_data.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                product_data = {
                    "variants": [
                        {
                            "title": "Red/Large",
                            "price": f"{row['Variant Price']}",
                            "sku": f"{row['Sku']}",
                            "position": 1,
                            "compare_at_price": f"{row['Compare At Price']}",
                            "option1": "Red",
                            "option2": "Large",
                            "option3": None,
                            "taxable": True,
                            "barcode": f"{row['Barcode']}",
                            "is_physical": False,
                            "weight": "1",
                            "inventory_quantity": 100
                        },
                        {
                            "title": "Red/Medium",
                            "price": f"{row['Variant Price']}",
                            "sku": f"{row['Sku']}1",
                            "position": 2,
                            "compare_at_price": f"{row['Compare At Price']}",
                            "option1": "Red",
                            "option2": "Medium",
                            "option3": None,
                            "taxable": True,
                            "barcode": f"{row['Barcode']}",
                            "is_physical": True,
                            "weight": "1",
                            "inventory_quantity": 100
                        }
                    ],
                    "options": [
                        {
                            "name": "Color",
                            "position": 1,
                            "values": "Red"
                        },
                        {
                            "name": "Size",
                            "position": 1,
                            "values": "Large,Medium"
                        },
                    ],
                    "product_images": [],
                    "features": [
                        {
                            "feature_title": "Feature " + f"{row['id']}",
                            "feature_details": "Details " + f"{row['id']}"
                        }
                    ],
                    "title": f"{row['Title']}",
                    "description": f"{row['Description']}",
                    "hide_out_of_stock": f"{row['hide out of stock']}".capitalize(),
                    "track_inventory": f"{row['Track Inventory']}".capitalize(),
                    "tags": f"{row['Tags']}",
                    "has_variants": True,
                    "is_active": f"{row['Is Active']}".capitalize(),
                    "is_approved": f"{row['Is Approved']}".capitalize(),
                    "product_group": row['Product Group'],
                    "vendor": row['Vendor'],
                    "product_type": row['Product Type'],
                    "product_brand": row['Product Brand'],
                    "collection": [int(row['Collection'])],
                    "user": self.request.user
                }

                try:
                    if type(product_data['variants']) is dict:
                        raise Exception("Variants must be an array of objects")
                    if type(product_data['options']) is dict:
                        raise Exception("Options must be an array of objects")
                    if type(product_data['product_images']) is dict:
                        raise Exception("Product Images must be an array of objects")
                    if type(product_data['collection']) is dict:
                        raise Exception("Collection must be an array of objects")

                except Exception as e:
                    print(e)
                    return Response({"detail": str(e)}, status=404)

                product = AddProductSerializer(data=product_data)
                if product.is_valid(raise_exception=True):
                    product.save()
                else:
                    return Response(product.errors, status=422)

        # try:
        #     for i in range(2, 102):
        #         response = requests.get(f"http://placehold.it/2400x2400&text=Product {i}")
        #         raw_data = response.content
        #         file_name = f"Product-image-{i}.png"
        #         with open(file_name, 'wb') as new_file:
        #             new_file.write(raw_data)
        #
        #         try:
        #             media = Media.objects.get(file_name=file_name)
        #         except Exception as e:
        #             print(e)
        #             media = Media()
        #
        #         s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        #         bucket_path = settings.AWS_BUCKET_PATH
        #         file_path = "products/product_images/" + file_name
        #         s3.upload_file(file_name, bucket_path, file_path, ExtraArgs={'StorageClass': "STANDARD_IA", 'ACL': 'public-read'})
        #         file_url = settings.AWS_BASE_URL + "/" + file_path
        #         media.file_path = file_path
        #         media.cdn_link = file_url
        #         media.file_name = file_name
        #         media.position = 1
        #         media.product_id = i
        #         media.deleted = False
        #         media.deleted_at = None
        #         media.save()
        #
        #         files = glob.glob('.\*.png')
        #         os.remove(files[0])
        #
        # except Exception as e:
        #     print(e)
        #     return Response({"detail": str(e)}, status=404)

        return Response({'Data inserted Successfully'}, status=200)
