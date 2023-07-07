
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from datetime import datetime
from discount.BusinessLogic.ApplyDiscount import apply_discount
from discount.BusinessLogic.DeleteDiscount import delete_discount
from discount.models import Discount
from rest_framework.generics import ListCreateAPIView
from authentication.BusinessLogic.ActivityStream import SystemLogs
from ecomm_app.pagination import StandardResultSetPagination
from discount.Serializers.DiscountSerializer import \
    AddDiscountSerializer, \
    DiscountDetailSerializer, \
    DiscountListSerializer, \
    DiscountStatusChangeSerializer, \
    DiscountBulkDeleteSerializer
from authentication.BusinessLogic.ApiPermissions import AccessApi
from rest_framework import exceptions


class DiscountListView(ListCreateAPIView):
    serializer_class = DiscountListSerializer
    pagination_class = StandardResultSetPagination

    @swagger_auto_schema(responses={200: DiscountListSerializer(many=True)})
    def get_queryset(self):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "discounts")
            if not access:
                raise exceptions.ParseError("This user does not have permission to access this api")

        try:
            if self.request.user.is_vendor:
                vendor = self.request.user.vendor
                queryset = Discount.objects.filter(deleted=False, vendor=vendor)
            else:
                queryset = Discount.objects.filter(deleted=False)

            # Post Entry in Logs
            action_performed = self.request.user.username + " get list of discount"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            return queryset

        except Exception as e:
            print(e)
            raise exceptions.ParseError(str(e))


class DiscountView(APIView):

    @swagger_auto_schema(responses={200: AddDiscountSerializer}, request_body=AddDiscountSerializer)
    def post(self, request):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "discounts")
            if not access:
                raise exceptions.ParseError("This user does not have permission to access this Api")

        request_data = request.data
        if self.request.user.is_vendor:
            request_data['vendor'] = self.request.user.vendor.id

        discount = AddDiscountSerializer(data=request_data)
        if discount.is_valid(raise_exception=True):
            discount.save()
            new_discount = Discount.objects.filter(id=discount.data['id']).first()
            try:
                if new_discount.discount_type == 'simple_discount':
                    if new_discount.status == 'Approved':
                        apply_discount(discounts=[new_discount])
            except Exception as e:
                return Response({'detail': f"{e}"}, status=200)

            # Post Entry in Logs
            action_performed = request.user.username + " created discount"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(discount.data, status=200)
        else:
            return Response(discount.errors, status=422)

    @swagger_auto_schema(responses={200: AddDiscountSerializer}, request_body=AddDiscountSerializer)
    def put(self, request):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "discounts")
            if not access:
                raise exceptions.ParseError("This user does not have permission to access this api")

        try:
            request_data = request.data
            if self.request.user.is_vendor:
                request_data['vendor'] = self.request.user.vendor.id

            obj_id = request_data["id"]
            discount = Discount.objects.filter(id=obj_id).first()
            serializer = AddDiscountSerializer(discount, data=request_data)

            if serializer.is_valid():
                serializer.save()

                # Post Entry in Logs
                action_performed = request.user.username + " update discount"
                SystemLogs.post_logs(self, request, request.user, action_performed)

                return Response(serializer.data, status=200)
            else:
                return Response(serializer.errors, status=422)

        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=400)


class DiscountDetailView(APIView):
    @swagger_auto_schema(responses={200: DiscountDetailSerializer})
    def get(self, request, pk):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "discounts")
            if not access:
                raise exceptions.ParseError("This user does not have permission to access this api")

        try:
            if self.request.user.is_vendor:
                vendor = self.request.user.vendor
                instance = Discount.objects.get(pk=pk, deleted=False, vendor=vendor)
            else:
                instance = Discount.objects.get(pk=pk, deleted=False)
        except Exception as e:
            return Response({"detail": str(e)}, status=404)

        serializer = DiscountDetailSerializer(instance)

        # Post Entry in Logs
        action_performed = request.user.username + " fetched single discount"
        SystemLogs.post_logs(self, request, request.user, action_performed)

        return Response(serializer.data, status=200)

    @swagger_auto_schema(responses={200: DiscountDetailSerializer}, request_body=DiscountDetailSerializer)
    def delete(self, request, pk):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "discounts")
            if not access:
                raise exceptions.ParseError("This user does not have permission to access this api")

        try:
            if self.request.user.is_vendor:
                vendor = self.request.user.vendor
                discount = Discount.objects.filter(id=pk, vendor=vendor).first()
            else:
                discount = Discount.objects.filter(id=pk).first()

            if discount:
                if discount.discount_type == 'simple_discount':
                    if discount.status == 'Approved':
                        delete_discount(discount)

                discount.deleted = True
                discount.deleted_at = datetime.now()
                discount.save()
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)

        # Post Entry in Logs
        action_performed = request.user.username + " delete discount"
        SystemLogs.post_logs(self, request, request.user, action_performed)

        return Response({"detail": "Deleted Discount Successfully!"}, status=200)


class DiscountStatusChange(APIView):
    @swagger_auto_schema(responses={200: DiscountStatusChangeSerializer}, request_body=DiscountStatusChangeSerializer)
    def put(self, request):
        access = AccessApi(self.request.user, "discounts")
        if not access:
            raise exceptions.ParseError("This user does not have permission to access this api")

        try:
            request_data = request.data
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=400)

        serializer = DiscountStatusChangeSerializer(data=request_data)

        if serializer.is_valid():
            serializer.save()

            # Post Entry in Logs
            action_performed = request.user.username + " update discount status"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response({"detail": "Status Changed"}, status=200)
        else:
            return Response(serializer.errors, status=422)


class DiscountBulkDelete(APIView):
    @swagger_auto_schema(responses={200: DiscountBulkDeleteSerializer}, request_body=DiscountBulkDeleteSerializer)
    def post(self, request):
        access = AccessApi(self.request.user, "discounts")
        if not access:
            raise exceptions.ParseError("This user does not have permission to access this api")

        try:
            request_data = request.data
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=400)

        serializer = DiscountBulkDeleteSerializer(data=request_data)

        if serializer.is_valid():
            serializer.save()

            # Post Entry in Logs
            action_performed = request.user.username + " bulk discount delete"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response({"detail": "Successfully deleted discounts"}, status=200)
        else:
            return Response(serializer.errors, status=422)
