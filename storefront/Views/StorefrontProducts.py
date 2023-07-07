from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework import exceptions
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from ecomm_app.pagination import StandardResultSetPagination
from products.BusinessLogic.ElasticSearch import ElasticSearch
from storefront.Serializers.StorefrontProductSerializer import ProductListSerializer, ProductDetailSerializer, \
    BannerSerializer
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Q
from functools import reduce
from operator import or_
from django.db.models import IntegerField
from django.db.models.functions import Cast
from products.models import Collection, Product, CategoryHandle, MainCategory, SubCategory, SuperSubCategory, Media, \
    Brand, Option, Tags
from storefront.BussinessLogic.CheckDomain import check_domain
from itertools import chain
from collections import Iterable
import random
import requests


class ProductView(ListCreateAPIView):
    serializer_class = ProductListSerializer
    pagination_class = StandardResultSetPagination

    @swagger_auto_schema(responses={200: ProductListSerializer})
    def get_queryset(self):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        collections = False
        category_handle = self.request.GET.get('category_handle', None)
        brand_handle = self.request.GET.get('brand_handle', None)
        collections_filter = self.request.GET.get('collections', None)
        brand_list = self.request.GET.get('brands', None)
        price_range = self.request.GET.get('prices', None)
        tags = self.request.GET.get('tags', None)
        search_by_image = self.request.GET.get('search_by_image', None)
        product_options = self.request.GET.get('product_options', None)
        sorting = self.request.GET.get('sort', None)
        vendor_unique_id = self.request.GET.get('vendor_id', None)

        if category_handle and brand_handle:
            raise exceptions.ParseError("Please provide either category handle or brand handle")

        if category_handle is not None:
            category = CategoryHandle.objects.filter(name=category_handle).first()
            category_type = category.category_type

            if category_type == 'main_category':
                collections = Collection.objects.filter(main_category__handle=category_handle, is_active=True,
                                                        status="Approved", deleted=False)
            elif category_type == 'sub_category':
                collections = Collection.objects.filter(sub_category__handle=category_handle, is_active=True,
                                                        status="Approved", deleted=False)
            elif category_type == 'super_sub_category':
                collections = Collection.objects.filter(super_sub_category__handle=category_handle, is_active=True,
                                                        status="Approved", deleted=False)
            else:
                collections = False

        if collections_filter is not None:
            string_data = str(collections_filter)
            collections_filter = string_data.split()
            collections_list = []
            for i in collections_filter:
                collection = i.split('_')
                if type(collection) == list:
                    for j in collection:
                        collections_list.append(j)
                else:
                    collections_list.append(collection)

            collections = Collection.objects.filter(handle__in=collections_list, is_active=True, status="Approved",
                                                    deleted=False)

        # if collections:
        try:
            if collections:
                collection = [collection for collection in collections]
                products = Product.objects.filter(collection__in=collection, is_hidden=False, is_active=True,
                                                  deleted=False, status='Approved').distinct()
            elif brand_handle is not None:
                products = Product.objects.filter(product_brand__handle=brand_handle, is_hidden=False, is_active=True,
                                                  deleted=False, status='Approved').distinct()
            elif vendor_unique_id is not None:
                products = Product.objects.filter(vendor__unique_id=vendor_unique_id, is_hidden=False, is_active=True,
                                                  deleted=False, status='Approved').distinct()
            else:
                products = False

            if products:
                if brand_list is not None:
                    brand_list = brand_list.split()
                    products = products.filter(product_brand__handle__in=brand_list)

                if tags is not None:
                    tags = tags.split()
                    tag_list = []
                    for tag_name in tags:
                        tag_name = tag_name.replace('_', ' ')
                        tag = Tags.objects.filter(name__iexact=tag_name, is_option=False, deleted=False).first()
                        if tag:
                            tag_list.append(tag)
                    products = products.filter(tag__in=tag_list)

                if product_options is not None:
                    tags = product_options.split()
                    tag_list = []
                    for tag_name in tags:
                        tag_name = tag_name.replace('_', ' ')
                        tag = Tags.objects.filter(name__iexact=tag_name, is_option=True, deleted=False).first()
                        if tag:
                            tag_list.append(tag)
                    products = products.filter(tag__in=tag_list)

                if price_range is not None:
                    split_price = price_range.split()
                    price_range = []
                    for i in split_price:
                        split_value = i.split('-', 2)
                        price_range.append(int(split_value[0]))
                        price_range.append(int(split_value[1]))

                    min_price = min(price_range)
                    max_price = max(price_range)
                    product_ids = tuple(product.id for product in products)
                    if product_ids:
                        try:
                            raw_query = products.raw(
                                f'''select p.* from products_product p INNER JOIN products_variant v ON p.id = v.product_id where p.id in {product_ids} and convert(v.price, decimal) >= {min_price} and convert(v.price, decimal) <= {max_price} and p.is_active=1 and p.deleted=0''')
                            product_list = [i.id for i in raw_query]
                        except Exception as e:
                            print(e)
                            product_list = []
                        products = products.filter(id__in=product_list)

                if sorting is not None:
                    if sorting == 'A-Z':
                        products = products.order_by('title')
                    elif sorting == 'Z-A':
                        products = products.order_by('-title')
                    elif sorting == 'ascending':
                        products = products.annotate(
                            price=Cast('product_variant__price', output_field=IntegerField()), ).order_by('price')
                    elif sorting == 'descending':
                        products = products.annotate(
                            price=Cast('product_variant__price', output_field=IntegerField()), ).order_by('-price')
                    else:
                        return Response(exceptions.ParseError('Please enter valid sorting value'))

                return products
            else:
                products = []
                return products
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)


class ProductDetailView(APIView):
    @swagger_auto_schema(responses={200: ProductDetailSerializer})
    def get(self, request, slug):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            instance = Product.objects.get(handle=slug, is_active=True, deleted=False, status='Approved')
        except Exception as e:
            return Response({"detail": str(e)}, status=404)

        serializer = ProductDetailSerializer(instance)

        return Response(serializer.data, status=200)


class ProductSearchView(ListCreateAPIView):
    serializer_class = ProductListSerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        search = self.request.GET.get('q', None)
        category_handle = self.request.GET.get('category', None)
        limit = self.request.GET.get('limit', None)

        if limit is not None and int(limit) > 50:
            raise exceptions.ParseError('pagination limit out of range')

        if search is None:
            data = []
            return data

        if category_handle is not None:
            main_category = MainCategory.objects.filter(handle=category_handle, deleted=False, is_active=True)
            sub_category = SubCategory.objects.filter(main_category__in=main_category, deleted=False, is_active=True)
            supersub_category = SuperSubCategory.objects.filter(sub_category__in=sub_category, deleted=False,
                                                                is_active=True)

            products_list = []
            product = Product.objects.filter((Q(title__icontains=search) | Q(tag__name__icontains=search)),
                                             is_active=True, deleted=False, status='Approved').distinct()
            products_list.extend(product)
            products = Product.objects.filter((Q(collection__main_category__in=main_category) | Q(
                collection__sub_category__in=sub_category) | Q(collection__super_sub_category__in=supersub_category)),
                                              is_active=True, deleted=False, status='Approved').distinct()
            products_list.extend(products)
        else:
            bl = ElasticSearch()
            products_ids = bl.search(search)
            products = Product.objects.filter(id__in=products_ids)

            products = list(products)
            products.sort(key=lambda album: products_ids.index(album.id))

        return products


class BannerView(APIView):
    def get(self, request):
        access_domain = check_domain(self.request)
        if access_domain:
            raise exceptions.ParseError("This user does not have permission to this Api")

        category_handle = self.request.GET.get('category_handle', None)
        brand_handle = self.request.GET.get('brand_handle', None)

        media = False
        category_object = False
        brand_object = False

        if category_handle is not None:
            category = CategoryHandle.objects.filter(name=category_handle).first()
            if category:
                category_type = category.category_type
            else:
                raise exceptions.ParseError('Category not found')

            if category_type == 'main_category':
                category_object = MainCategory.objects.filter(handle=category_handle, is_active=True,
                                                              deleted=False).first()
                if category_object:
                    media = Media.objects.filter(main_category=category_object, deleted=False).exclude(
                        file_name="maincategory_thumbnail_image").first()
            elif category_type == 'sub_category':
                category_object = SubCategory.objects.filter(handle=category_handle, is_active=True,
                                                             deleted=False).first()
                if category_object:
                    media = Media.objects.filter(sub_category=category_object, deleted=False).exclude(
                        file_name="subcategory_thumbnail_image").first()
            elif category_type == 'super_sub_category':
                category_object = SuperSubCategory.objects.filter(handle=category_handle, is_active=True,
                                                                  deleted=False).first()
                if category_object:
                    media = Media.objects.filter(super_sub_category=category_object, deleted=False).exclude(
                        file_name="supersubcategory_thumbnail_image").first()
            else:
                media = False

        if brand_handle is not None:
            brand_object = Brand.objects.filter(handle=brand_handle, deleted=False).first()
            if brand_object:
                media = Media.objects.filter(brand=brand_object, file_name='brand_banner', deleted=False).first()

        try:
            serializer = BannerSerializer(media)
            data = serializer.data
            if category_object:
                data['seo_details'] = {
                    'seo_title': category_object.seo_title,
                    'seo_description': category_object.seo_description,
                    'seo_keywords': category_object.seo_keywords,
                    'title': category_object.name
                }
            elif brand_object:
                data['seo_details'] = {
                    'seo_title': brand_object.seo_title,
                    'seo_description': brand_object.seo_description,
                    'seo_keywords': brand_object.seo_keywords,
                    'title': brand_object.name
                }
            return Response(data, status=200)
        except Exception as e:
            return Response({"detail": str(e)}, status=404)


def convert_list_in_1d(lis):
    for item in lis:
        if isinstance(item, Iterable) and not isinstance(item, str):
            for x in convert_list_in_1d(item):
                yield x
        else:
            yield item


class MostVisitedProducts(APIView):
    def post(self, request):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            category_handle = request.data['category_handles']

            length = len(category_handle)
            if length > 0:
                if 20 % length != 0:
                    length = length + 1
                product_count = 20 // length
            else:
                return Response({"detail": "you are not sending any category"}, status=400)

            product_list = []
            for category in category_handle:
                if category:
                    category = category.strip()
                    categories = CategoryHandle.objects.filter(name=category).first()
                    if categories:
                        category_type = categories.category_type
                        if category_type == 'main_category':
                            products = Product.objects.filter(collection__main_category__handle=category,
                                                              deleted=False, is_active=True,
                                                              status='Approved').distinct()[:product_count]
                        elif category_type == 'sub_category':
                            products = Product.objects.filter(collection__sub_category__handle=category,
                                                              deleted=False, is_active=True,
                                                              status='Approved').distinct()[:product_count]
                        elif category_type == 'super_sub_category':
                            products = Product.objects.filter(collection__super_sub_category__handle=category,
                                                              deleted=False, is_active=True,
                                                              status='Approved').distinct()[:product_count]
                        else:
                            products = None

                        if products:
                            product_list.append(products)
            product_list = convert_list_in_1d(product_list)
            result_list = list(chain(product_list))
            random.shuffle(result_list)

            serializers = ProductListSerializer(result_list, many=True)
            return Response(serializers.data, status=200)
        except Exception as e:
            return Response({"detail": str(e)}, status=404)
