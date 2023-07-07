import pytz
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.BusinessLogic.ActivityStream import SystemLogs
from crm.models import Customer
from discount.Serializers.CheckoutPromoCodeSerializer import PromoCodeSerializer, RemovePromoCodeSerializer
from discount.models import Discount
from datetime import datetime
from django.conf import settings

from order.models import Checkout
from setting.models import StoreInformation
from storefront.BussinessLogic.CheckDomain import check_domain
from rest_framework import exceptions


class PromoCodeView(APIView):
    def post(self, request):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        promo_code = request.data['promo_code']
        checkout_id = request.data['checkout_id']
        if 'customer_id' in request.data:
            customer = request.data['customer_id']
        else:
            customer = None

        try:
            try:
                checkout = Checkout.objects.filter(checkout_id=checkout_id).first()
                if checkout:
                    promo_list = checkout.promo_code
                    if promo_list is not None:
                        promo_list = promo_list.split(',')
                        if promo_code in promo_list:
                            return Response({"detail": 'Promo code already applied'}, status=404)

                store_information = StoreInformation.objects.filter(deleted=False).first()

                if not store_information:
                    raise exceptions.ParseError('Please save store information first')

                if not store_information.time_zone:
                    raise exceptions.ParseError('Please save time zone in store information first')

                today = datetime.now(pytz.timezone(store_information.time_zone))
                today = today.replace(tzinfo=None)
                # utc = pytz.UTC
                # today = utc.localize(today)

                discount = Discount.objects.filter(promo_code=promo_code, start_date__lt=today, end_date__gt=today,
                                                   is_active=True, deleted=False, status='Approved').first()
                if not discount:
                    raise exceptions.ParseError('No promo code found')

                if not discount.no_limit:
                    if discount.usage_count > discount.usage_limit:
                        raise exceptions.ParseError('Promo code usage limit exceed')
                if discount.customer_eligibility == 'specific_customers':
                    if customer:
                        customer = Customer.objects.filter(id=customer, customer_discount=discount).first()

                    if not customer:
                        raise exceptions.ParseError('Promo code not valid for this customer')
            except Exception as e:
                print(e)
                return Response({"detail": f'{e}'}, status=404)

            serializer = PromoCodeSerializer(discount, context={'checkout': checkout, 'promo_code': promo_code})

            if not discount.no_limit:
                discount.usage_count += 1
                discount.save()

            # return Response({'detail': 'Promocode applied'}, status=200)
            return Response(serializer.data, status=200)

        except Exception as e:
            return Response({"detail": str(e)}, status=400)

    def delete(self, request):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        promo_code = request.data['promo_code']
        checkout_id = request.data['checkout_id']
        if 'customer_id' in request.data:
            customer = request.data['customer_id']
        else:
            customer = None

        try:
            try:
                checkout = Checkout.objects.filter(checkout_id=checkout_id).first()
                if checkout:
                    promo_list = checkout.promo_code
                    if promo_list is not None:
                        promo_list = promo_list.split(',')
                        if promo_code not in promo_list:
                            return Response({"detail": 'Promo code already removed'}, status=404)

                discount = Discount.objects.get(promo_code=promo_code, is_active=True, deleted=False, status='Approved')
                # if discount.usage_count > discount.usage_limit:
                #     raise exceptions.ParseError('Promo code usage limit exceed')
                # if discount.customer_eligibility == 'specific_customers':
                #     if customer:
                #         customer = Customer.objects.filter(id=customer, customer_discount=discount).first()
                #
                #     if not customer:
                #         raise exceptions.ParseError('Promo code not valid for this customer')
            except Exception as e:
                print(e)
                return Response({"detail": 'Invalid promo code'}, status=404)

            serializer = RemovePromoCodeSerializer(discount,
                                                   context={'checkout': checkout, 'promo_code': promo_code})

            if not discount.no_limit:
                discount.usage_count -= 1
                discount.save()

            # return Response({'detail': 'Promo code applied'}, status=200)
            return Response(serializer.data, status=200)

        except Exception as e:
            return Response({"detail": str(e)}, status=400)
