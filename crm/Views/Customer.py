
from datetime import datetime
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from ecomm_app.pagination import StandardResultSetPagination
from crm.models import Customer, Address
from crm.Serializers.CustomerSerializer import CustomerListSerializer, CustomerDetailSerializer, \
    CustomerStatusChangeSerializer, CustomerDeleteSerializer, CustomerAddSerializer
from drf_yasg.utils import swagger_auto_schema
from authentication.BusinessLogic.ActivityStream import SystemLogs
from authentication.BusinessLogic.ApiPermissions import AccessApi


class CustomerListView(ListCreateAPIView):
    serializer_class = CustomerListSerializer
    pagination_class = StandardResultSetPagination

    @swagger_auto_schema(responses={200: CustomerListSerializer}, request_body=CustomerListSerializer)
    def get_queryset(self):
        access = AccessApi(self.request.user, "customer")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        queryset = Customer.objects.filter(deleted=False)

        # Post Entry in Logs
        action_performed = self.request.user.username + " get list of Customers"
        SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

        return queryset


class CustomerView(APIView):

    @swagger_auto_schema(responses={200: CustomerAddSerializer}, request_body=CustomerAddSerializer)
    def post(self, request):
        access = AccessApi(self.request.user, "customer")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        request_data = request.data
        customer = CustomerAddSerializer(data=request_data)
        if customer.is_valid(raise_exception=True):
            customer.save()

            # Post Entry in Logs
            action_performed = request.user.username + "created customer"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(customer.data, status=200)
        else:
            return Response(customer.errors, status=422)

    @swagger_auto_schema(responses={200: CustomerAddSerializer}, request_body=CustomerAddSerializer)
    def put(self, request):
        access = AccessApi(self.request.user, "customer")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            obj_id = request.data["id"]
        except Exception as e:
            print(e)
            return Response({"detail": "ID not found in data!"}, status=400)

        request_data = request.data

        if obj_id is None:
            serializer = CustomerAddSerializer(data=request_data)
        else:
            customer = Customer.objects.filter(id=obj_id).first()
            serializer = CustomerAddSerializer(customer, data=request_data)

        if serializer.is_valid():
            serializer.save()

            # Post Entry in Logs
            action_performed = request.user.username + " update customer"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=422)


class CustomerDetailView(APIView):
    @swagger_auto_schema(responses={200: CustomerDetailSerializer})
    def get(self, request, pk):
        if not self.request.user.is_vendor:
            access = AccessApi(self.request.user, "customer")
            if not access:
                raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            instance = Customer.objects.get(id=pk, deleted=False)
        except Exception as e:
            return Response({"detail": str(e)}, status=404)

        serializer = CustomerDetailSerializer(instance)

        # Post Entry in Logs
        action_performed = request.user.username + " fetched single Customer"
        SystemLogs.post_logs(self, request, request.user, action_performed)

        return Response(serializer.data, status=200)

    @swagger_auto_schema(responses={200: CustomerDeleteSerializer}, request_body=CustomerDeleteSerializer)
    def delete(self, request, pk):
        access = AccessApi(self.request.user, "customer")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        if pk is not None:
            try:
                Address.objects.filter(customer_id=pk).update(deleted=True, deleted_at=datetime.now())
                Customer.objects.filter(id=pk).update(deleted=True, deleted_at=datetime.now())
            except Exception as e:
                return Response({"detail": str(e)}, status=404)
        else:
            return Response({"detail": "Customer ID not found in request"}, status=404)

        # Post Entry in Logs
        action_performed = request.user.username + " deleted customer"
        SystemLogs.post_logs(self, request, request.user, action_performed)

        return Response({"detail": "Deleted Customer Successfully!"}, status=200)


class AddressDelete(APIView):
    def delete(self, request, pk):
        access = AccessApi(self.request.user, "customer")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        if pk is not None:
            try:
                Address.objects.filter(id=pk).update(deleted=True, deleted_at=datetime.now())
            except Exception as e:
                return Response({"detail": str(e)}, status=404)
        else:
            return Response({"detail": "Address ID not found in request"}, status=404)

        # Post Entry in Logs
        action_performed = request.user.username + " deleted customer"
        SystemLogs.post_logs(self, request, request.user, action_performed)

        return Response({"detail": "Deleted Address Successfully!"}, status=200)


class CustomerStatusChange(APIView):
    @swagger_auto_schema(responses={200: CustomerStatusChangeSerializer}, request_body=CustomerStatusChangeSerializer)
    def put(self, request):
        access = AccessApi(self.request.user, "customer")
        if not access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            request_data = request.data
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=400)

        serializer = CustomerStatusChangeSerializer(data=request_data)

        if serializer.is_valid():
            serializer.save()

            # Post Entry in Logs
            action_performed = request.user.username + " update Customer status"
            SystemLogs.post_logs(self, request, request.user, action_performed)

            return Response({"detail": True}, status=200)
        else:
            return Response(serializer.errors, status=422)
