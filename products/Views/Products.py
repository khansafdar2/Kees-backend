
from datetime import datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from ecomm_app.pagination import StandardResultSetPagination
from products.BusinessLogic.ElasticSearch import ElasticSearch
from products.models import Product, ProductGroup, Variant, Option, Media, Feature, MainCategory, SubCategory ,\
    SuperSubCategory
from products.Serializers.ProductSerializer import \
    ProductListSerializer, \
    ProductDeleteSerializer, \
    AddProductSerializer, \
    UpdateProductSerializer, \
    ProductDetailSerializer, \
    ProductStatusChangeSerializer, \
    ProductBulkOrganizeSerializer, \
    ProductBulkTagsSerializer
from drf_yasg.utils import swagger_auto_schema
from authentication.BusinessLogic.ActivityStream import SystemLogs
from authentication.BusinessLogic.ApiPermissions import AccessApi
from rest_framework import exceptions


class ProductListView(ListCreateAPIView):
    serializer_class = ProductListSerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "products")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to this Api")

            vendor = self.request.GET.get('vendor', None)
            collection = self.request.GET.get('collection', None)
            column = self.request.GET.get('column', None)
            search = self.request.GET.get('search', None)
            status = self.request.GET.get('status', None)
            approval_status = self.request.GET.get('approval_status', None)

            if self.request.user.is_vendor:
                vendor = self.request.user.vendor_id

            if vendor is None:
                queryset = Product.objects.filter(deleted=False)
            else:
                queryset = Product.objects.filter(deleted=False, vendor_id=vendor)

            if collection is not None:
                if collection != "":
                    queryset = queryset.filter(collection=collection)

            if column is not None:
                if column == "title":
                    queryset = queryset.filter(title__icontains=search)
                if column == "tags":
                    queryset = queryset.filter(tags__icontains=search)
                if column == "sku":
                    queryset = queryset.filter(product_variant__sku=search)
                if column == "barcode":
                    queryset = queryset.filter(product_variant__barcode=search)

            if status is not None:
                if status.lower() == 'active':
                    queryset = queryset.filter(is_active=True)
                elif status.lower() == 'inactive':
                    queryset = queryset.filter(is_active=False)
                else:
                    raise exceptions.ParseError("Invalid status filter")

            if approval_status is not None:
                if approval_status.lower() == 'approved':
                    queryset = queryset.filter(status='Approved')
                elif approval_status.lower() == 'disapproved':
                    queryset = queryset.filter(status='disapproved')
                else:
                    raise exceptions.ParseError("Invalid approval status filter")

            # Post Entry in Logs
            action_performed = self.request.user.username + " get list of Products"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            return queryset
        except Exception as e:
            print(e)
            raise exceptions.ParseError(str(e))


class ProductView(APIView):

    @swagger_auto_schema(responses={200: AddProductSerializer}, request_body=AddProductSerializer)
    def post(self, request):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "products")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to this Api")
            else:
                request.data['vendor'] = self.request.user.vendor_id

            request_data = request.data
            if type(request_data['variants']) is dict:
                raise Exception("Variants must be an array of objects")
            if type(request_data['options']) is dict:
                raise Exception("Options must be an array of objects")
            if type(request_data['product_images']) is dict:
                raise Exception("Product Images must be an array of objects")
            if type(request_data['collection']) is dict:
                raise Exception("Collection must be an array of objects")

            request_data['user'] = self.request.user

            product = AddProductSerializer(data=request_data)
            if product.is_valid(raise_exception=True):
                product.save()

                # Post Entry in Logs
                action_performed = request.user.username + " created product"
                SystemLogs.post_logs(self, request, request.user, action_performed)

                return Response(product.data, status=200)
            else:
                return Response(product.errors, status=422)

        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)

    @swagger_auto_schema(responses={200: UpdateProductSerializer}, request_body=UpdateProductSerializer)
    def put(self, request):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "products")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to this Api")
            else:
                request.data['vendor'] = self.request.user.vendor_id

            request_data = request.data

            try:
                obj_id = request.data["id"]
            except Exception as e:
                return Response({'detail': str(e)}, status=404)

            request_data['user'] = self.request.user

            if type(request_data['options']) is dict:
                raise Exception("Options must be an array of objects")
            if type(request_data['collection']) is not list:
                raise Exception("Collection must be an array of objects")
            if type(request_data['features']) is not list:
                raise Exception("Features must be an array of objects")

            if self.request.user.is_vendor:
                vendor_id = self.request.user.vendor_id
                product = Product.objects.filter(id=obj_id, vendor_id=vendor_id).first()
            else:
                product = Product.objects.filter(id=obj_id).first()

            serializer = UpdateProductSerializer(product, data=request_data)

            if serializer.is_valid():
                serializer.save()

                # Post Entry in Logs
                action_performed = request.user.username + " update Product"
                SystemLogs.post_logs(self, request, request.user, action_performed)

                return Response(serializer.data, status=200)
            else:
                return Response(serializer.errors, status=422)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=400)

    @swagger_auto_schema(responses={200: ProductDeleteSerializer}, request_body=ProductDeleteSerializer)
    def delete(self, request):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "products")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

        obj_ids = request.GET.get('ids', None)
        if obj_ids:
            obj_ids = obj_ids.split(',')
            try:
                if self.request.user.is_vendor:
                    vendor_id = self.request.user.vendor_id
                    Product.objects.filter(id__in=obj_ids, vendor_id=vendor_id).update(deleted=True, deleted_at=datetime.now())
                    Variant.objects.filter(product_id__in=obj_ids).update(deleted=True, sku=None, deleted_at=datetime.now())
                    Option.objects.filter(product_id__in=obj_ids).update(deleted=True, deleted_at=datetime.now())
                    Media.objects.filter(product_id__in=obj_ids).update(deleted=True, deleted_at=datetime.now())
                    Feature.objects.filter(product_id__in=obj_ids).update(deleted=True, deleted_at=datetime.now())
                else:
                    Product.objects.filter(id__in=obj_ids).update(deleted=True, deleted_at=datetime.now())
                    Variant.objects.filter(product_id__in=obj_ids).update(deleted=True, sku=None,
                                                                          deleted_at=datetime.now())
                    Option.objects.filter(product_id__in=obj_ids).update(deleted=True, deleted_at=datetime.now())
                    Media.objects.filter(product_id__in=obj_ids).update(deleted=True, deleted_at=datetime.now())
                    Feature.objects.filter(product_id__in=obj_ids).update(deleted=True, deleted_at=datetime.now())

                bl = ElasticSearch()
                obj = Product.objects.filter(id__in=obj_ids)
                bl.bulk_insert_or_update(obj)

            except Exception as e:
                return Response({"detail": str(e)}, status=404)
        else:
            return Response({"detail": "Product ID not found in request"}, status=404)

        # Post Entry in Logs
        action_performed = request.user.username + " deleted customer"
        SystemLogs.post_logs(self, request, request.user, action_performed)

        return Response({"detail": "Deleted Product Successfully!"}, status=200)


class ProductDetailView(APIView):
    @swagger_auto_schema(responses={200: ProductDetailSerializer})
    def get(self, request, pk):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "products")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            if self.request.user.is_vendor:
                vendor_id = self.request.user.vendor_id
                instance = Product.objects.get(id=pk, vendor_id=vendor_id, deleted=False)
            else:
                instance = Product.objects.get(id=pk, deleted=False)

        except Exception as e:
            return Response({"detail": str(e)}, status=404)

        serializer = ProductDetailSerializer(instance)

        # Post Entry in Logs
        action_performed = request.user.username + " fetched single product detail"
        SystemLogs.post_logs(self, request, request.user, action_performed)

        return Response(serializer.data, status=200)


class ProductStatusChange(APIView):
    @swagger_auto_schema(responses={200: ProductStatusChangeSerializer}, request_body=ProductStatusChangeSerializer)
    def put(self, request):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "products")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

        request.data['user'] = self.request.user
        serializer = ProductStatusChangeSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            # Post Entry in Logs
            action_performed = request.user.username + " update products status"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response({"detail": True}, status=200)
        else:
            return Response(serializer.errors, status=422)


class ProductBulkOrganize(APIView):

    @swagger_auto_schema(responses={200: ProductBulkOrganizeSerializer}, request_body=ProductBulkOrganizeSerializer)
    def put(self, request):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "products")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

        serializer = ProductBulkOrganizeSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            # Post Entry in Logs
            action_performed = request.user.username + " update products organizations in bulk"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response({"detail": True}, status=200)
        else:
            return Response(serializer.errors, status=422)


class ProductBulkTags(APIView):

    @swagger_auto_schema(responses={200: ProductBulkTagsSerializer}, request_body=ProductBulkTagsSerializer)
    def put(self, request):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "products")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

        request.data['user'] = self.request.user
        serializer = ProductBulkTagsSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            # Post Entry in Logs
            action_performed = request.user.username + " update products tags in bulk"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response({"detail": True}, status=200)
        else:
            return Response(serializer.errors, status=422)
