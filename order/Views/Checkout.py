from django.shortcuts import redirect
import json
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.BusinessLogic.ActivityStream import SystemLogs
from order.models import Checkout, LineItems, Order
from order.Serializers.CheckoutSerializers import CountryListSerializer, CityListSerializer
from setting.models import PaymentMethod, Country, City
from crm.models import Wallet
from shipping.models import Shipping, Zone
from storefront.BussinessLogic.CheckDomain import check_domain
from setting.Serializers.PaymentMethodSerializer import PaymentSerializer, GatewaySerializer
from order.Serializers.CheckoutSerializers import \
    CheckoutAddSerializer, \
    CheckoutUpdateSerializer, \
    CheckoutDetailSerializer, \
    ShippingCalculateSerializer, ThankYouSerializer, \
    VerifyProductShippingSerializer, CheckoutLineItemSerializer
from drf_yasg.utils import swagger_auto_schema
from order.BusinessLogic.CheckAvailableVariant import CheckVariantQuantity
from rest_framework import exceptions
from paymentgateway.models import GatewayCredentials
from ecomm_app.settings.local import STAGING_HOST


class CheckoutView(APIView):
    @swagger_auto_schema(responses={200: CheckoutAddSerializer}, request_body=CheckoutAddSerializer)
    def post(self, request):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            request_data = request.data
            check_qty = CheckVariantQuantity(request_data["line_items"])
            if check_qty:
                return Response(data=check_qty, status=404)
            serializer = CheckoutAddSerializer(data=request_data)
            if serializer.is_valid():
                serializer.save()

                return Response(serializer.data, status=200)
            else:
                return Response(serializer.errors, status=422)

        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)

    @swagger_auto_schema(responses={200: CheckoutUpdateSerializer}, request_body=CheckoutUpdateSerializer)
    def put(self, request):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            request_data = request.data
            checkout_id = request.data["checkout_id"]
            line_items = LineItems.objects.values().filter(checkout__checkout_id=checkout_id)
            check_qty = CheckVariantQuantity(line_items)
            if check_qty:
                return Response(data=check_qty, status=404)

            if checkout_id is None:
                serializer = CheckoutUpdateSerializer(data=request_data)
            else:
                checkout = Checkout.objects.filter(checkout_id=checkout_id).first()
                serializer = CheckoutUpdateSerializer(checkout, data=request_data)

            if serializer.is_valid():
                serializer.save()

                return Response(serializer.data, status=200)
            else:
                return Response(serializer.errors, status=422)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=400)


class CheckoutDetailView(APIView):
    @swagger_auto_schema(responses={200: CheckoutDetailSerializer}, request_body=CheckoutDetailSerializer)
    def get(self, request, pk):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            try:
                checkout = Checkout.objects.get(pk=pk)
            except Exception as e:
                return Response({"detail": str(e)}, status=404)

            serializer = CheckoutDetailSerializer(checkout)
            return Response(serializer.data, status=200)

        except Exception as e:
            return Response({"detail": str(e)}, status=400)


class DeleteLineItem(APIView):
    def delete(self, request):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        checkout_id = self.request.GET.get('checkout_id')
        line_item = self.request.GET.get('line_item')

        if checkout_id and line_item is not None:
            try:
                checkout = Checkout.objects.get(checkout_id=checkout_id)
                LineItems.objects.get(id=line_item, checkout=checkout).delete()
                return Response({"detail": "line item deleted successfully"}, status=200)
            except Exception as e:
                return Response({"detail": str(e)}, status=404)
        else:
            return Response({"detail": "Checkout ID OR Line Item id not found in request"}, status=404)


class CheckoutShippingPrice(APIView):

    @swagger_auto_schema(responses={200: ShippingCalculateSerializer}, request_body=ShippingCalculateSerializer)
    def post(self, request):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            request_data = request.data
            if 'checkout_id' in request_data:
                line_items = LineItems.objects.filter(checkout__checkout_id=request_data['checkout_id'])
            elif 'order_id' in request_data:
                line_items = LineItems.objects.filter(order__order_id=request_data['order_id'])
            else:
                return Response({'detail': 'checkout_id or order_id not exist'}, status=404)

            serializer = ShippingCalculateSerializer(line_items, context={'checkout_id': request_data['checkout_id']})
            return Response(serializer.data, status=200)

        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)


class PaymentMethodList(APIView):
    @swagger_auto_schema(responses={200: PaymentSerializer}, request_body=PaymentSerializer)
    def get(self, request):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            try:
                payment_method = PaymentMethod.objects.filter(deleted=False)
            except Exception as e:
                return Response({"detail": str(e)}, status=404)

            serializer = PaymentSerializer(payment_method, many=True)
            return Response(serializer.data, status=200)

        except Exception as e:
            return Response({"detail": str(e)}, status=400)


class PaymentGatewayList(APIView):
    @swagger_auto_schema(responses={200: PaymentSerializer}, request_body=PaymentSerializer)
    def get(self, request):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            try:
                payment_method = GatewayCredentials.objects.filter(deleted=False)
            except Exception as e:
                return Response({"detail": str(e)}, status=404)

            serializer = GatewaySerializer(payment_method, many=True)
            return Response(serializer.data, status=200)

        except Exception as e:
            return Response({"detail": str(e)}, status=400)


class GatewayPaymentMethod(APIView):
    @swagger_auto_schema(responses={200: GatewaySerializer}, request_body=GatewaySerializer)
    def get(self, request):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            try:
                name = self.request.GET.get('gateway_name')
                payment_method = GatewayCredentials.objects.get(deleted=False, gateway_name__iexact=name)
            except Exception as e:
                return Response({"detail": str(e)}, status=404)
            if payment_method.gateway_name == 'BAF':
                return redirect(STAGING_HOST + '/paymentgateway/baf_request')
            if payment_method.gateway_name == 'MCB':
                return redirect(STAGING_HOST + '/paymentgateway/mcb_request')
            if payment_method.gateway_name == 'STRIPE':
                return redirect(STAGING_HOST + '/paymentgateway/stripe_request')
            if payment_method.gateway_name == 'BYKEA':
                return redirect(STAGING_HOST + '/paymentgateway/bykea_request')
            if payment_method.gateway_name == 'PAY PRO':
                return redirect(STAGING_HOST + '/paymentgateway/paypro_request')
            if payment_method.gateway_name == 'UBL':
                return redirect(STAGING_HOST + '/paymentgateway/ubl_request')
            if payment_method.gateway_name == 'QISSATPAY':
                return redirect(STAGING_HOST + '/paymentgateway/qisstpay_request')
        except Exception as e:
            return Response({"detail": str(e)}, status=400)


class ThankYouView(APIView):
    @swagger_auto_schema(responses={200: ThankYouSerializer}, request_body=ThankYouSerializer)
    def get(self, request, pk):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            try:
                order = Order.objects.filter(order_id=pk).first()
            except Exception as e:
                return Response({"detail": str(e)}, status=404)

            serializer = ThankYouSerializer(order)
            return Response(serializer.data, status=200)

        except Exception as e:
            return Response({"detail": str(e)}, status=400)


class VerifyProductShipping(APIView):
    # @swagger_auto_schema(responses={200: ThankYouSerializer}, request_body=ThankYouSerializer)
    def get(self, request):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")
        try:
            checkout_id = self.request.GET.get('checkout_id')
            checkout_obj = {"checkout_id": checkout_id}
            json_object = json.dumps(checkout_obj)

            serializer = VerifyProductShippingSerializer(json_object)
            return Response(serializer.data)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)


class CheckoutLineItems(APIView):

    @swagger_auto_schema(responses={200: CheckoutLineItemSerializer}, request_body=CheckoutLineItemSerializer)
    def post(self, request):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        try:
            request_data = request.data
            if 'checkout_id' in request_data:
                line_items = LineItems.objects.filter(checkout__checkout_id=request_data['checkout_id'])
            elif 'order_id' in request_data:
                line_items = LineItems.objects.filter(order__order_id=request_data['order_id'])
            else:
                return Response({'detail': 'checkout_id or order_id not exist'}, status=404)

            serializer = CheckoutLineItemSerializer(line_items, context={'checkout_id': request_data['checkout_id']})
            return Response(serializer.data, status=200)

        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)


class GetCountriesAtCheckoutView(APIView):
    def get(self, request):
        # shipping = Shipping.objects.filter(is_active=True, deleted=False)
        query_set = Country.objects.filter(zone_country__shipping_zone__isnull=False, zone_country__shipping_zone__is_active=True, zone_country__shipping_zone__deleted=False, deleted=False, is_active=True).distinct()
        if not query_set:
            data = []
            return Response(data, status=200)

        serializer = CountryListSerializer(query_set, many=True)

        # system logs
        action_performed = request.user.username + "fetch all countries at checkout "
        SystemLogs.post_logs(self, request, None, action_performed)

        return Response(serializer.data, status=200)


class GetCitiesAtCheckoutView(APIView):
    def get(self, request):

        country_id = self.request.GET.get('country_id')
        query_set = City.objects.filter(country_id=country_id,
                                        zone_city__shipping_zone__isnull=False,
                                        zone_city__shipping_zone__is_active=True,
                                        zone_city__shipping_zone__deleted=False,
                                        deleted=False,
                                        is_active=True).distinct()
        if not query_set:
            data = []
            return Response(data, status=200)

        serializer = CityListSerializer(query_set, many=True)

        # system logs
        action_performed = request.user.username + " fetch all cities at checkout"
        SystemLogs.post_logs(self, request, None, action_performed)

        return Response(serializer.data, status=200)


class CheckWalletAmount(APIView):
    def post(self, request):
        checkout_id = request.GET.get('checkout_id')
        customer_id = request.GET.get('customer_id')

        checkout = Checkout.objects.filter(checkout_id=checkout_id).first()
        wallet = Wallet.objects.filter(customer_id=customer_id).first()

        if not checkout:
            raise exceptions.ParseError('Invalid checkout id', code=404)

        total_amount = float(checkout.subtotal_price) + float(checkout.total_shipping)
        if wallet:
            if total_amount <= wallet.value:
                status = 'Fully Paid'
            elif total_amount > wallet.value:
                status = 'Partially Paid'
            else:
                status = 'Unpaid'
        else:
            status = 'Unpaid'

        return status
