import json

from django.db.models import Q, F
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
    def get(self, request):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        data = list()

        storefront_filters = StoreFilter.objects.filter(deleted=False, is_active=True).order_by('position')

        if storefront_filters:
            variants = Variant.objects.filter(~Q(price=F('compare_at_price')),
                                              product__is_active=True,
                                              product__deleted=False, deleted=False).distinct()

            for storefront_filter in storefront_filters:
                if storefront_filter.type == 'price':
                    if variants:
                        products = variants.values('price').order_by('price')
                        min_amount = int(products.first()['price'])
                        max_amount = int(products.last()['price'])

                        data.append({'type': 'price', 'title': storefront_filter.title, 'min': min_amount, 'max': max_amount})
                    else:
                        data.append({'type': 'price', 'title': storefront_filter.title, 'min': 0, 'max': 0})

                if storefront_filter.type == 'collection':
                    collections = Collection.objects.filter(product__product_variant__in=variants,
                                                            is_active=True, deleted=False).distinct()

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

                if storefront_filter.type == 'tags':
                    tags = Tags.objects.filter(product_tags__product_variant__in=variants, is_option=False, deleted=False).values_list('name', flat=True).distinct()
                elif storefront_filter.type == 'product_options':
                    tags = Tags.objects.filter(product_tags__product_variant__in=variants, is_option=True, deleted=False).values_list('name', flat=True).distinct()
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

                if storefront_filter.type == 'brand':
                    brand_query_set = Brand.objects.filter(product_brand__product_variant__in=variants, deleted=False).order_by('name').distinct()

                    if not brand_query_set:
                        data.append({'type': 'brands', 'title': storefront_filter.title, 'data': []})
                    else:
                        serializer = BrandSerializer(brand_query_set, many=True)
                        data.append({'type': 'brands', 'title': storefront_filter.title, 'data': serializer.data})
        else:
            raise exceptions.ParseError("Please configure your filters")

        return Response(data, status=200)
