
from datetime import datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from products.models import ProductGroup, Product
from vendor.models import Vendor
from products.Serializers.ProductGroupSerializer import \
    ProductGroupSerializer, \
    ProductGroupStatusChangeSerializer, \
    ProductGroupListSerializer, ProductGroupDetailSerializer
from ecomm_app.pagination import StandardResultSetPagination
from drf_yasg.utils import swagger_auto_schema
from authentication.BusinessLogic.ActivityStream import SystemLogs
from authentication.BusinessLogic.ApiPermissions import AccessApi
from rest_framework import exceptions


class ProductGroupListView(ListCreateAPIView):
    serializer_class = ProductGroupListSerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "products")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to this Api")

            vendor = self.request.GET.get('vendor', None)
            column = self.request.GET.get('column', None)
            search = self.request.GET.get('search', None)
            status = self.request.GET.get('status', None)
            approval_status = self.request.GET.get('approval_status', None)

            if self.request.user.is_vendor:
                vendor = self.request.user.vendor_id

            if vendor is None:
                queryset = ProductGroup.objects.filter(deleted=False)
            else:
                queryset = ProductGroup.objects.filter(deleted=False, vendor_id=vendor)
            if column is not None:
                if column == "title":
                    queryset = queryset.filter(title__icontains=search)
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
                    queryset = queryset.filter(status='Disapproved')
                else:
                    raise exceptions.ParseError("Invalid approval status filter")

            # Post Entry in Logs
            action_performed = self.request.user.username + " get list of Product Group"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            return queryset
        except Exception as e:
            print(e)
            raise exceptions.ParseError(str(e))


class ProductGroupView(APIView):

    @swagger_auto_schema(responses={200: ProductGroupSerializer}, request_body=ProductGroupSerializer)
    def post(self, request):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "products")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to this Api")
            else:
                request.data['vendor'] = self.request.user.vendor_id

            request_data = request.data
            serializer = ProductGroupSerializer(data=request_data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

                # Post Entry in Logs
                action_performed = request.user.username + " created Product Group"
                SystemLogs.post_logs(self, request, request.user, action_performed)

                return Response(serializer.data, status=200)
            else:
                return Response(serializer.errors, status=422)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=400)

    @swagger_auto_schema(responses={200: ProductGroupSerializer}, request_body=ProductGroupSerializer)
    def put(self, request):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "products")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to this Api")
            else:
                request.data['vendor'] = self.request.user.vendor_id

            try:
                obj_id = request.data["id"]
            except Exception as e:
                return Response({'detail': str(e)}, status=404)

            if self.request.user.is_vendor:
                vendor_id = self.request.user.vendor_id
                product_group = ProductGroup.objects.filter(id=obj_id, vendor_id=vendor_id).first()
            else:
                product_group = ProductGroup.objects.filter(id=obj_id, deleted=False).first()

            serializer = ProductGroupSerializer(product_group, data=request.data)
            if serializer.is_valid():
                serializer.save()

                # Post Entry in Logs
                action_performed = request.user.username + " update Product Group"
                SystemLogs.post_logs(self, request, request.user, action_performed)

                return Response(serializer.data, status=200)
            else:
                return Response(serializer.errors, status=422)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=400)


class ProductGroupDetail(APIView):
    @swagger_auto_schema(responses={200: ProductGroupSerializer})
    def get(self, request, pk):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "products")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            if self.request.user.is_vendor:
                vendor_id = self.request.user.vendor_id
                instance = ProductGroup.objects.get(id=pk, vendor_id=vendor_id)
            else:
                instance = ProductGroup.objects.get(pk=pk)
        except Exception as e:
            return Response({"detail": str(e)}, status=404)

        serializer = ProductGroupDetailSerializer(instance)

        # Post Entry in Logs
        action_performed = request.user.username + " fetched single product_group"
        SystemLogs.post_logs(self, request, request.user, action_performed)

        return Response(serializer.data, status=200)

    def delete(self, request, pk):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "products")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            new_product_group = request.GET.get('product_group', None)
            if pk is not None:
                if new_product_group is not None:
                    vendor = Vendor.objects.filter(product_group_vendor__in=[pk, new_product_group])
                    if vendor[0] == vendor[1]:
                        if self.request.user.is_vendor:
                            requested_vendor = self.request.user.vendor
                            if vendor[0] == vendor[1] == requested_vendor:
                                Product.objects.filter(product_group=pk, vendor=requested_vendor).update(product_group=new_product_group)
                                ProductGroup.objects.filter(id=pk, vendor=requested_vendor).update(deleted=True, deleted_at=datetime.now())
                        else:
                            Product.objects.filter(product_group=pk).update(product_group=new_product_group)
                            ProductGroup.objects.filter(id=pk).update(deleted=True, deleted_at=datetime.now())
                    else:
                        raise exceptions.ParseError("Both product groups are not of same vendor")
                else:
                    raise exceptions.ParseError("Product Group is mandatory")
                return Response({"detail": "Deleted Product Group Successfully!"}, status=200)
            else:
                return Response({"detail": "Product Group ID not found in request"}, status=404)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)


class ProductGroupStatusChange(APIView):
    @swagger_auto_schema(responses={200: ProductGroupStatusChangeSerializer}, request_body=ProductGroupStatusChangeSerializer)
    def put(self, request):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "products")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            request_data = request.data
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=400)

        request_data['user'] = self.request.user
        serializer = ProductGroupStatusChangeSerializer(data=request_data)

        if serializer.is_valid():
            serializer.save()

            # Post Entry in Logs
            action_performed = request.user.username + " update product group status"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response({"detail": True}, status=200)
        else:
            return Response(serializer.errors, status=422)

