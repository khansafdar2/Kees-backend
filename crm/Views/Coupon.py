from datetime import datetime
import random

from drf_yasg.utils import swagger_auto_schema
from rest_framework import exceptions
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.BusinessLogic.ActivityStream import SystemLogs
from authentication.BusinessLogic.ApiPermissions import AccessApi
from crm.Serializers.CouponSerializer import CouponListSerializer, CouponAddSerializer, CouponDetailSerializer
from crm.models import Coupon, Customer, Wallet
from ecomm_app.pagination import StandardResultSetPagination


class CustomScriptForWalletCreation(APIView):
    def get(self, request):
        try:
            all_customers = Customer.objects.filter(deleted=False)
            for customer in all_customers:
                customer_id = customer.id
                wallet = Wallet.objects.filter(customer_id=customer_id).first()
                if not wallet:
                    current_date = datetime.now()
                    unique_id = (str(random.randint(1000, 1000000)) + '-' + current_date.strftime("%Y-%m-%dT%H-%M-%S")). \
                        replace('-', '')
                    Wallet.objects.create(customer_id=customer_id, unique_id=unique_id, is_active=True)
                # current_date = datetime.now()
                # unique_id = (str(random.randint(1000, 1000000)) + '-' + current_date.strftime("%Y-%m-%dT%H-%M-%S")). \
                #     replace('-', '')
                # Wallet.objects.filter(customer_id=customer_id).update(unique_id=unique_id)
            return Response('success', status=200)
        except Exception as e:
            return Response({"detail": str(e)}, status=404)


class CouponListView(ListCreateAPIView):
    serializer_class = CouponListSerializer
    pagination_class = StandardResultSetPagination

    @swagger_auto_schema(responses={200: CouponListSerializer}, request_body=CouponListSerializer)
    def get_queryset(self):
        access = AccessApi(self.request.user, "customer")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        queryset = Coupon.objects.filter(is_deleted=False)

        # Post Entry in Logs
        action_performed = self.request.user.username + " get list of all Coupon"
        SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

        return queryset


class CouponView(APIView):

    @swagger_auto_schema(responses={200: CouponAddSerializer}, request_body=CouponAddSerializer)
    def post(self, request):
        access = AccessApi(self.request.user, "customer")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        request_data = request.data
        coupon = CouponAddSerializer(data=request_data)

        if coupon.is_valid(raise_exception=True):
            coupon.save()

            # Post Entry in Logs
            action_performed = request.user.username + f"created coupon with name: {request_data['name']}"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(coupon.data, status=200)
        else:
            return Response(coupon.errors, status=422)

    @swagger_auto_schema(responses={200: CouponAddSerializer}, request_body=CouponAddSerializer)
    def put(self, request):
        access = AccessApi(self.request.user, "customer")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            obj_id = request.data["id"]
        except Exception as e:
            print(e)
            return Response({"detail": "Id not found in data!"}, status=400)

        request_data = request.data

        coupon = Coupon.objects.filter(id=obj_id).first()
        serializer = CouponAddSerializer(coupon, data=request_data)

        if serializer.is_valid():
            serializer.save()

            # Post Entry in Logs
            action_performed = request.user.username + f"update coupon with name: {coupon.name}"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=422)


class CouponDetailView(APIView):
    @swagger_auto_schema(responses={200: CouponDetailSerializer})
    def get(self, request, pk):
        access = AccessApi(self.request.user, "customer")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            instance = Coupon.objects.get(pk=pk)
        except Exception as e:
            return Response({"detail": str(e)}, status=404)

        serializer = CouponDetailSerializer(instance)

        # Post Entry in Logs
        action_performed = request.user.username + " fetched single Coupon"
        SystemLogs.post_logs(self, request, request.user, action_performed)

        return Response(serializer.data, status=200)

    def delete(self, request, pk):
        access = AccessApi(self.request.user, "customer")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        if pk is not None:
            try:
                coupon = Coupon.objects.filter(id=pk).first()
                coupon.is_deleted = True
                coupon.deleted_at = datetime.now()
                coupon.save()
            except Exception as e:
                return Response({"detail": str(e)}, status=404)
        else:
            return Response({"detail": "Coupon ID not found in request"}, status=404)

        # Post Entry in Logs
        action_performed = request.user.username + f"Deleted coupon with name {coupon.name}"
        SystemLogs.post_logs(self, request, request.user, action_performed)

        return Response({"detail": "Deleted Coupon Successfully!"}, status=200)
