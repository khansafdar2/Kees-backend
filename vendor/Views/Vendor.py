
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from datetime import datetime
from vendor.models import Vendor, Commission
from products.models import Product, ProductGroup, Collection
from rest_framework.generics import ListCreateAPIView
from authentication.BusinessLogic.ActivityStream import SystemLogs
from ecomm_app.pagination import StandardResultSetPagination
from vendor.Serializers.VendorSerializer import \
    AddVendorSerializer, \
    VendorDetailSerializer, \
    VendorListSerializer, \
    DeleteSerializer, \
    UpdateVendorSerializer, \
    VendorStatusChangeSerializer, \
    AddExternalVendorSerializer, \
    VendorApprovalSerializer, CommissionListSerializer
from authentication.BusinessLogic.ApiPermissions import AccessApi
from rest_framework import exceptions
from storefront.BussinessLogic.MediaUpload import media_upload
import json


class VendorListView(ListCreateAPIView):
    serializer_class = VendorListSerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        access = AccessApi(self.request.user, "vendor")
        if not access:
            raise exceptions.ParseError("This user does not have permission to access vendor")

        column = self.request.GET.get('column', None)
        search = self.request.GET.get('search', None)
        status = self.request.GET.get('status', None)
        approval_status = self.request.GET.get('approval_status', None)

        queryset = Vendor.objects.filter(deleted=False).order_by('-id')

        if column is not None:
            if column == "name":
                queryset = queryset.filter(name__icontains=search)

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
        action_performed = self.request.user.username + " get list of Vendors"
        SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

        return queryset


class VendorView(APIView):
    @swagger_auto_schema(responses={200: AddVendorSerializer}, request_body=AddVendorSerializer)
    def post(self, request):
        access = AccessApi(self.request.user, "vendor")
        if not access:
            raise exceptions.ParseError("This user does not have permission to access vendor")

        request_data = request.data
        vendor = AddVendorSerializer(data=request_data)
        if vendor.is_valid(raise_exception=True):
            vendor.save()

            # Post Entry in Logs
            action_performed = request.user.username + " created vendor"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(vendor.data, status=200)
        else:
            return Response(vendor.errors, status=422)

    @swagger_auto_schema(responses={200: UpdateVendorSerializer}, request_body=UpdateVendorSerializer)
    def put(self, request):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "vendor")
            if not access:
                raise exceptions.ParseError("This user does not have permission to access vendor")

        try:
            request_data = request.data
            obj_id = request_data["id"]
            vendor = Vendor.objects.filter(id=obj_id).first()

            if not self.request.user.is_vendor:
                serializer = UpdateVendorSerializer(vendor, data=request_data)
            else:
                if self.request.user.vendor_id == obj_id:
                    # request_data = json.loads(request_data)

                    if vendor.cancel_check:
                        request_data.pop('cancel_check', None)

                    if vendor.trade_license:
                        request_data.pop('trade_license', None)

                    if vendor.national_id:
                        request_data.pop('national_id', None)

                    request_data.pop('email', None)
                    request_data.pop('commissions', None)

                    # request_data = json.dumps(request_data)
                    serializer = UpdateVendorSerializer(vendor, data=request_data)

                else:
                    raise Exception('You cannot edit any other vendor')

            if serializer.is_valid():
                serializer.save()

                # Post Entry in Logs
                action_performed = request.user.username + " update vendor"
                SystemLogs.post_logs(self, request, request.user, action_performed)

                return Response(serializer.data, status=200)
            else:
                return Response(serializer.errors, status=422)

        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=400)


class VendorDetailView(APIView):
    @swagger_auto_schema(responses={200: VendorDetailSerializer})
    def get(self, request, pk):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "vendor")
            if not access:
                raise exceptions.ParseError("This user does not have permission to access vendor")

        try:
            instance = Vendor.objects.get(pk=pk)
        except Exception as e:
            return Response({"detail": str(e)}, status=404)

        serializer = VendorDetailSerializer(instance)

        # Post Entry in Logs
        action_performed = request.user.username + " fetched single vendor"
        SystemLogs.post_logs(self, request, request.user, action_performed)

        return Response(serializer.data, status=200)

    @swagger_auto_schema(responses={200: DeleteSerializer}, request_body=DeleteSerializer)
    def delete(self, request, pk):
        access = AccessApi(self.request.user, "vendor")
        if not access:
            raise exceptions.ParseError("This user does not have permission to access vendor")

        try:
            new_vendor = self.request.GET.get('new_vendor', None)
            products = self.request.GET.get('products', None)
            product_groups = self.request.GET.get('product_groups', None)
            collections = self.request.GET.get('collections', None)

            if new_vendor is None:
                Vendor.objects.filter(id=pk).update(deleted=True, deleted_at=datetime.now())
                Product.objects.filter(vendor_id=pk).update(deleted=True, deleted_at=datetime.now())
                ProductGroup.objects.filter(vendor_id=pk).update(deleted=True, deleted_at=datetime.now())
                Collection.objects.filter(vendor_id=pk).update(deleted=True, deleted_at=datetime.now())
            else:
                Vendor.objects.filter(id=pk).update(deleted=True, deleted_at=datetime.now())
                if product_groups is not None:
                    if product_groups == 'delete':
                        if products == 'reassign':
                            Product.objects.filter(vendor_id=pk, deleted=False).update(product_group=None)
                        ProductGroup.objects.filter(vendor_id=pk, deleted=False).update(deleted=True,
                                                                                        deleted_at=datetime.now())
                    elif product_groups == 'reassign':
                        ProductGroup.objects.filter(vendor_id=pk, deleted=False).update(vendor_id=new_vendor)
                    else:
                        print('undefine product group attribute')

                if collections is not None:
                    if collections == 'delete':
                        if products == 'reassign':
                            product = Product.objects.filter(vendor_id=pk, deleted=False)
                            for prod in product:
                                prod.collection.remove(*prod.collection.all())
                        Collection.objects.filter(vendor_id=pk, deleted=False).update(deleted=True,
                                                                                      deleted_at=datetime.now())
                    elif collections == 'reassign':
                        Collection.objects.filter(vendor_id=pk, deleted=False).update(vendor_id=new_vendor)
                    else:
                        print('undefine collection attribute')

                if products is not None:
                    if products == 'delete':
                        Product.objects.filter(vendor_id=pk, deleted=False).update(deleted=True,
                                                                                   deleted_at=datetime.now())
                    elif products == 'reassign':
                        Product.objects.filter(vendor_id=pk).update(vendor_id=new_vendor)
                    else:
                        print('undefine product attribute')

        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)

        return Response({"detail": "Deleted Vendor Successfully!"}, status=200)


class VendorStatusChange(APIView):
    @swagger_auto_schema(responses={200: VendorStatusChangeSerializer}, request_body=VendorStatusChangeSerializer)
    def put(self, request):
        access = AccessApi(self.request.user, "vendor")
        if not access:
            raise exceptions.ParseError("This user does not have permission to access vendor")

        try:
            obj_id = request.data['id']
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=400)

        vendor = Vendor.objects.filter(id=obj_id, deleted=False).first()
        serializer = VendorStatusChangeSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            # Post Entry in Logs
            action_performed = request.user.username + " update vendor status"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response({"detail": True}, status=200)
        else:
            return Response(serializer.errors, status=422)


class VendorStoreFrontView(APIView):
    @swagger_auto_schema(responses={200: AddExternalVendorSerializer}, request_body=AddExternalVendorSerializer)
    def post(self, request):
        request_data = request.data

        vendor_data = json.loads(request_data['data'])

        if 'tradeLicense' in request_data:
            image = request_data['tradeLicense']
            vendor_data['trade_license'] = media_upload(image)

        if 'nationalId' in request_data:
            image = request_data['nationalId']
            vendor_data['national_id'] = media_upload(image)

        if 'cancelCheck' in request_data:
            image = request_data['cancelCheck']
            vendor_data['cancel_check'] = media_upload(image)

        vendor = AddExternalVendorSerializer(data=vendor_data)
        if vendor.is_valid(raise_exception=True):
            vendor.save()

            # Post Entry in Logs
            action_performed = f"Create vendor request from storefront with store name: {vendor_data['store_name']}"
            SystemLogs.post_logs(self, request, '', action_performed)

            return Response({'detail': 'vendor created'}, status=200)
        else:
            return Response(vendor.errors, status=422)


class VendorApprovalView(APIView):
    @swagger_auto_schema(responses={200: VendorApprovalSerializer}, request_body=VendorApprovalSerializer)
    def put(self, request):
        try:
            access = AccessApi(self.request.user, "vendor")
            if not access:
                raise exceptions.ParseError("This user does not have permission to access vendor")

            obj_id = request.data["id"]
            vendor = Vendor.objects.filter(id=obj_id).first()
            serializer = VendorApprovalSerializer(vendor, data=request.data)

            if serializer.is_valid():
                serializer.save()

                # Post Entry in Logs
                action_performed = request.user.username + "change vendor status"
                SystemLogs.post_logs(self, request, request.user, action_performed)

                return Response(serializer.data, status=200)
            else:
                return Response(serializer.errors, status=422)

        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=400)


class CommissionView(APIView):
    @swagger_auto_schema(responses={200: CommissionListSerializer}, request_body=CommissionListSerializer)
    def get(self, request):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "vendor")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

            obj_id = self.request.GET.get('vendor_id', None)
        else:
            obj_id = self.request.user.vendor_id

        if obj_id:

            all_commissions = Commission.objects.filter(vendor_id=obj_id, deleted=False)

            if not all_commissions:
                data = []
                return Response(data, status=200)

            commissions = CommissionListSerializer(all_commissions, many=True)
        else:
            raise Exception('provide valid vendor id')

        # Post Entry in Logs
        action_performed = request.user.username + " get all commissions"
        SystemLogs.post_logs(self, request, request.user, action_performed)

        return Response(commissions.data, status=200)

    def delete(self, request, pk):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "vendor")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to this Api")
            else:
                raise Exception('Vendor cannot delete commissions')

            new_id = self.request.GET.get('new_id', None)

            if pk is not None:
                Product.objects.filter(commission_id=pk).update(commission_id=new_id)
                Commission.objects.filter(id=pk).update(deleted=True, deleted_at=datetime.now())
                return Response({"detail": "Deleted Commission Successfully!"}, status=200)
            else:
                raise Exception('old and new commission id is mandatory')
        except Exception as e:
            return Response({"detail": str(e)}, status=400)
