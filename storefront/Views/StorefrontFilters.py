
import json
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from cms.models import StoreFilter
from products.models import Brand, Collection, CategoryHandle, Variant, Tags
from storefront.Serializers.StorefrontCollectionSerializer import CollectionSerializer, BrandSerializer
from cms.Serializers.PriceRangeSerializer import PriceFilterSerializer
from storefront.BussinessLogic.CheckDomain import check_domain
from rest_framework import exceptions


class FiltersList(APIView):
    @swagger_auto_schema(responses={200: PriceFilterSerializer(many=True)})
    def post(self, request):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        data = list()
        collections = False

        storefront_filters = StoreFilter.objects.filter(deleted=False, is_active=True).order_by('position')

        if storefront_filters:
            for storefront_filter in storefront_filters:
                if storefront_filter.type == 'price':

                    if 'brand_handle' in request.data:
                        brand_handle = request.data["brand_handle"]
                        products = Variant.objects.filter(product__product_brand__handle=brand_handle,
                                                          product__is_active=True, product__status='Pending',
                                                          product__deleted=False, deleted=False).values(
                            'price').order_by('price').distinct()
                    else:
                        products = False

                    if 'category_handle' in request.data:
                        if 'category_handle' in self.request.data:
                            category_handle = self.request.data["category_handle"]
                            category = CategoryHandle.objects.filter(name=category_handle).first()
                            category_type = category.category_type

                            if category_type == 'main_category':
                                products = Variant.objects.filter(
                                    product__collection__main_category__handle=category_handle,
                                    product__is_active=True,
                                    product__deleted=False, deleted=False).values('price').order_by('price').distinct()

                            elif category_type == 'sub_category':
                                products = Variant.objects.filter(
                                    product__collection__sub_category__handle=category_handle,
                                    product__is_active=True,
                                    product__deleted=False, deleted=False).values('price').order_by('price').distinct()

                            elif category_type == 'super_sub_category':
                                products = Variant.objects.filter(
                                    product__collection__super_sub_category__handle=category_handle,
                                    product__is_active=True,
                                    product__deleted=False, deleted=False).values('price').order_by('price').distinct()
                            else:
                                products = False

                    if products:
                        min_amount = int(products.first()['price'])
                        max_amount = int(products.last()['price'])

                        data.append({'type': 'price', 'title': storefront_filter.title, 'min': min_amount, 'max': max_amount})
                    else:
                        data.append({'type': 'price', 'title': storefront_filter.title, 'min': 0, 'max': 0})

                if (storefront_filter.type == 'collection') or (storefront_filter.type == 'brand') or (storefront_filter.type == 'tags'):
                    if 'brand_handle' in request.data:
                        brand_handle = request.data["brand_handle"]
                        collections = Collection.objects.filter(product__product_brand__handle=brand_handle,
                                                                is_active=True, status='Approved',
                                                                deleted=False).distinct()

                    if 'category_handle' in self.request.data:
                        category_handle = self.request.data["category_handle"]
                        category = CategoryHandle.objects.filter(name=category_handle).first()
                        category_type = category.category_type

                        if category_type == 'main_category':
                            collections = Collection.objects.filter(main_category__handle=category_handle,
                                                                    is_active=True, status='Approved',
                                                                    deleted=False).distinct()
                        elif category_type == 'sub_category':
                            collections = Collection.objects.filter(sub_category__handle=category_handle,
                                                                    is_active=True, status='Approved',
                                                                    deleted=False).distinct()
                        elif category_type == 'super_sub_category':
                            collections = Collection.objects.filter(super_sub_category__handle=category_handle,
                                                                    is_active=True, status='Approved',
                                                                    deleted=False).distinct()
                        else:
                            collections = False

                if storefront_filter.type == 'tags':
                    tags = Tags.objects.filter(product_tags__collection__in=collections, is_option=False, deleted=False).values_list('name', flat=True).distinct()
                elif storefront_filter.type == 'product_options':
                    tags = Tags.objects.filter(product_tags__collection__in=collections, is_option=True, deleted=False).values_list('name', flat=True).distinct()
                else:
                    tags = None

                if tags:
                    tags = [tag.lower() for tag in tags]
                    tags_list = []
                    if storefront_filter.tags:
                        filter_tags = storefront_filter.tags.split(',')
                        for tag in filter_tags:
                            if tag.lower() in tags:
                                tags_list.append(tag)
                        if len(tags_list) > 0:
                            tags_list = ','.join(tags_list)
                            data.append({'type': storefront_filter.type, 'title': storefront_filter.title, 'data': tags_list})

                # if storefront_filter.type == 'product_options':
                #     tags_list = []
                #     if storefront_filter.tags:
                #         filter_tags = storefront_filter.tags.split(',')
                #         for tag in filter_tags:
                #             if tag in tags:
                #                 tags_list.append(tag)
                #         if len(tags_list) > 0:
                #             tags_list = ','.join(tags_list)
                #             data.append({'type': 'product_options', 'title': storefront_filter.title, 'data': tags_list})

                if storefront_filter.type == 'collection':
                    if not collections:
                        data.append({'type': 'collections', 'title': storefront_filter.title, 'data': []})
                    else:
                        serializer = CollectionSerializer(collections, many=True)
                        serializer = json.loads(json.dumps(serializer.data))

                        collection_data = {}
                        for i in serializer:
                            if i['title'] in collection_data.keys():
                                collection_data[i['title']] = collection_data[i['title']] + '_' + i['handle']
                            else:
                                collection_data[i['title']] = i['handle']

                        collection_list = [{'title': key, 'handle': value} for key, value in collection_data.items()]

                        data.append({'type': 'collections', 'title': storefront_filter.title, 'data': collection_list})

                if storefront_filter.type == 'brand':
                    if 'brand_handle' in request.data:
                        brand_handle = request.data["brand_handle"]
                        brand_query_set = Brand.objects.filter(handle=brand_handle, deleted=False)

                    elif collections:
                        brand_query_set = Brand.objects.filter(product_brand__collection__in=collections,
                                                               deleted=False).distinct()

                    else:
                        brand_query_set = None

                    if not brand_query_set:
                        data.append({'type': 'brands', 'title': storefront_filter.title, 'data': []})
                    else:
                        serializer = BrandSerializer(brand_query_set, many=True)
                        data.append({'type': 'brands', 'title': storefront_filter.title, 'data': serializer.data})
        else:
            raise exceptions.ParseError("Please configure your filters")

        return Response(data, status=200)
