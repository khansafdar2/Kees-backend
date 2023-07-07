
from rest_framework import exceptions
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from ecomm_app.pagination import StandardResultSetPagination
from storefront.Serializers.StorefrontPromotionProductSerializer import PromotionProductListSerializer
from drf_yasg.utils import swagger_auto_schema
from products.models import Product, Collection, Tags
from django.db.models import Q, F, IntegerField
from django.db.models.functions import Cast
from storefront.BussinessLogic.CheckDomain import check_domain


class PromotionProductView(ListCreateAPIView):
    serializer_class = PromotionProductListSerializer
    pagination_class = StandardResultSetPagination

    @swagger_auto_schema(responses={200: PromotionProductListSerializer})
    def get_queryset(self):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        collections_filter = self.request.GET.get('collections', None)
        tags = self.request.GET.get('tags', None)
        product_options = self.request.GET.get('product_options', None)
        brand_list = self.request.GET.get('brands', None)
        price_range = self.request.GET.get('prices', None)
        sorting = self.request.GET.get('sort', None)

        try:
            products = Product.objects.filter(~Q(product_variant__price= F('product_variant__compare_at_price')), is_active=True, deleted=False)

            if products:
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
                    collections = Collection.objects.filter(handle__in=collections_list, is_active=True, deleted=False)
                    # collection = [collection for collection in collections]
                    products = products.filter(collection__in=collections, deleted=False)

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
                    split_price = price_range.split('-')
                    min_price = split_price[0]
                    max_price = split_price[1]
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

        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)
