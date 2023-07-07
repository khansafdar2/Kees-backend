
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import exceptions
from crm.BussinessLogic.CheckForgotLinkExpiry import CheckExpiry
from storefront.Serializers.StorefrontCustomerSerializer import SignInSerializer, \
    CustomerSignupSerializer, \
    CustomerAccountDetailSerializer, \
    CustomerAccountUpdateSerializer, \
    CustomerForgetPasswordSerializer, \
    SetPasswordSerializer
from order.Serializers.CheckoutOrderSerializer import CustomerAccountOrderDetailSerializer
from order.models import Order
from drf_yasg.utils import swagger_auto_schema
from crm.models import Customer, CustomerForgetPassword, Address
from storefront.BussinessLogic.CustomerAuthentication import token_authentication
from django.utils import timezone
from datetime import datetime, timedelta
from storefront.BussinessLogic.CheckDomain import check_domain
from rest_framework import exceptions


class CustomerSignup(APIView):

    @swagger_auto_schema(responses={200: CustomerSignupSerializer}, request_body=CustomerSignupSerializer)
    def post(self, request):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        request_data = request.data
        customer = CustomerSignupSerializer(data=request_data)
        if customer.is_valid(raise_exception=True):
            customer.save()

            return Response(customer.data, status=200)
        else:
            return Response(customer.errors, status=422)

    @swagger_auto_schema(responses={200: CustomerSignupSerializer}, request_body=CustomerSignupSerializer)
    def put(self, request):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            obj_id = request.data["id"]
        except Exception as e:
            print(e)
            return Response({"detail": "ID not found in data!"}, status=400)

        request_data = request.data

        if obj_id is None:
            serializer = CustomerSignupSerializer(data=request_data)
        else:
            customer = Customer.objects.filter(id=obj_id).first()
            serializer = CustomerSignupSerializer(customer, data=request_data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=422)


class SignIn(APIView):
    @swagger_auto_schema(responses={200: SignInSerializer}, request_body=SignInSerializer)
    def post(self, request):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        serializer = SignInSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            obj = serializer.validated_data
            response = {
                "id": obj.id,
                "email": obj.email,
                "token": obj.token
            }
            return Response(response, status=200)
        else:
            return Response({"response": "email or password incorrect"}, status=422)


class CustomerAccount(APIView):
    @swagger_auto_schema(responses={200: CustomerAccountDetailSerializer}, request_body=CustomerAccountDetailSerializer)
    def get(self, request):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        token = request.GET.get('token', None)
        customer = token_authentication(token)
        if customer:
            serializer = CustomerAccountDetailSerializer(customer)
            return Response(serializer.data, status=200)

    @swagger_auto_schema(responses={200: CustomerAccountUpdateSerializer}, request_body=CustomerAccountUpdateSerializer)
    def put(self, request):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        token = request.GET.get('token', None)
        customer = token_authentication(token)
        if customer:
            serializer = CustomerAccountUpdateSerializer(customer, request.data)
            if serializer.is_valid():
                serializer.save()
            return Response(serializer.data, status=200)


class AddressDelete(APIView):
    def delete(self, request):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        token = request.GET.get('token', None)
        address_id = request.GET.get('id', None)
        customer = token_authentication(token)
        if address_id is not None:
            try:
                Address.objects.filter(id=address_id, customer=customer).update(deleted=True, deleted_at=datetime.now())
                return Response({"detail": "Deleted Address Successfully!"}, status=200)
            except Exception as e:
                return Response({"detail": str(e)}, status=404)
        else:
            return Response({"detail": "Address ID not found in request"}, status=404)


class CustomerForgetPasswordView(APIView):
    @swagger_auto_schema(responses={200: CustomerForgetPasswordSerializer}, request_body=CustomerForgetPasswordSerializer)
    def post(self, request):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            serializer = CustomerForgetPasswordSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            return Response({'response': 'forgot password email send successfully'}, status=200)
        except Exception as e:
            print(e)
            return Response({'response': 'email not send, something went wrong'}, status=404)


# User Check if invite has expired or not with key signature
class CheckForgotPasswordLinkExpiry(APIView):
    def post(self, request):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            key = request.data['key']
            invitation = CustomerForgetPassword.objects.get(key=key)
            if invitation.expired:
                return Response({"expired": True}, status=200)
            key_expiry = CheckExpiry(key, invitation)
            if key_expiry["status"]:
                return Response({"expired": True}, status=200)
            else:
                return Response({"expired": False}, status=200)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=400)


class SetPassword(APIView):
    def post(self, request):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            data = request.data
            serializer = SetPasswordSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            return Response({'response': 'Password changed successfully'}, status=200)
        except Exception as e:
            print(e)
            return Response({'response': 'Password not changed, Something went wrong'}, status=400)
