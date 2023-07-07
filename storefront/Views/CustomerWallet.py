from datetime import datetime
import json
from django.conf import settings
import requests
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import APIView
from crm.models import Wallet, WalletHistory, Coupon, Customer
from setting.models import StoreInformation, LoyaltySetting
from storefront.BussinessLogic.CheckDomain import check_domain
from storefront.BussinessLogic.CustomerAuthentication import token_authentication
from storefront.Serializers.CustomerWalletSerializer import WalletSerializer, WalletHistoryListSerializer, \
    CouponListSerializer


class GetWalletView(APIView):
    def get(self, request, pk):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        token = request.GET.get('token', None)
        customer = token_authentication(token)

        if customer:
            wallet = Wallet.objects.filter(customer_id=pk).first()
            customer = Customer.objects.get(id=pk, deleted=False)
            setting = LoyaltySetting.objects.filter(deleted=False).first()

            serializer = WalletSerializer(wallet)
            loyalty_points = {
                "points": customer.points,
                "amount_equal_point": setting.point_equal_amount
            }

            data = serializer.data
            data['loyalty_points'] = loyalty_points
            return Response(data, status=200)


class RedeemLoyaltyPointsView(APIView):
    def post(self, request):
        try:
            access = check_domain(self.request)
            if access:
                raise exceptions.ParseError("This user does not have permission to this Api")
            token = request.GET.get('token', None)
            customer = token_authentication(token)

            redeem_amount = 0.00
            if customer:
                requested_data = request.data
                customer_id = requested_data['customer_id']
                points = requested_data['points']

                customer = Customer.objects.get(id=customer_id, deleted=False)
                setting = LoyaltySetting.objects.filter(deleted=False).first()

                # checking minimum point required for redemption
                if float(points) < setting.minimum_point_redeem:
                    return Response("Minimum Points required for redemption are:" + str(setting.minimum_point_redeem),
                                    status=400)
                # Redeem Points
                if customer.points >= float(points):
                    customer.points = float(customer.points) - float(points)
                    customer.save()
                    redeem_amount = float(points) / float(setting.point_equal_amount)

                wallet = Wallet.objects.filter(customer_id=customer_id).first()
                wallet.value = float(wallet.value) + redeem_amount
                wallet.save()

                WalletHistory.objects.create(wallet=wallet,
                                             type='Loyalty Points', action='Credited',
                                             value=redeem_amount)

                return Response({"details": "Loyalty points redeemed  Successfully"}, status=200)

        except Exception as e:
            return Response({"detail": str(e)}, status=404)


class GetLoyaltyPointsView(APIView):
    def get(self, request, pk):
        try:
            access = check_domain(self.request)
            if access:
                raise exceptions.ParseError("This user does not have permission to this Api")
            token = request.GET.get('token', None)
            customer = token_authentication(token)

            if customer:
                customer = Customer.objects.get(id=pk, deleted=False)
                setting = LoyaltySetting.objects.filter(deleted=False).first()
                data = {
                    "points": customer.points,
                    "amount_equal_point": setting.point_equal_amount
                }
                return Response(data, status=200)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)


class DebitWalletAmountView(APIView):
    def post(self, request):
        try:
            access = check_domain(self.request)
            if access:
                raise exceptions.ParseError("This user does not have permission to this Api")
            token = request.GET.get('token', None)
            customer = token_authentication(token)

            if customer:
                customer_id = request['customer_id']
                amount = request['amount']
                wallet = Wallet.objects.filter(customer_id=customer_id).first()
                wallet.value -= amount
                wallet.save()

                WalletHistory.objects.create(wallet=wallet,
                                             type='Payment At Checkout', action='Debited', value=amount)
                return Response(wallet, status=200)
        except Exception as e:
            return Response({"detail": str(e)}, status=404)


class WalletHistoryListView(APIView):
    def get(self, request, pk):
        try:
            access = check_domain(self.request)
            if access:
                raise exceptions.ParseError("This user does not have permission to this Api")
            token = request.GET.get('token', None)
            customer = token_authentication(token)

            if customer:
                wallet_history = WalletHistory.objects.filter(wallet_id=pk).order_by('-id')
                response = WalletHistoryListSerializer(wallet_history, many=True)
                return Response(response.data, status=200)
        except Exception as e:
            return Response({"detail": str(e)}, status=404)


# this is not using right now
class GetCouponListView(APIView):
    def get(self, request, pk):
        try:
            access = check_domain(self.request)
            if access:
                raise exceptions.ParseError("This user does not have permission to this Api")
            token = request.GET.get('token', None)
            customer = token_authentication(token)

            if customer:
                all_coupon = Coupon.objects.filter(customer_id=pk, is_active=True)
                response = CouponListSerializer(all_coupon, many=True)
                return Response(response, status=200)
        except Exception as e:
            return Response({"detail": str(e)}, status=404)


class RedeemCouponView(APIView):
    def post(self, request):
        try:
            access = check_domain(self.request)
            if access:
                raise exceptions.ParseError("This user does not have permission to this Api")

            token = request.GET.get('token', None)
            customer = token_authentication(token)
            request = request.data
            if customer:
                coupon_id = request['coupon_id']
                customer_id = request['customer_id']
                coupon = Coupon.objects.filter(id=coupon_id, customer_id=customer_id, is_active=True, is_deleted=False).first()

                if not coupon:
                    return Response({'detail': 'No Coupon Found'}, status=404)

                if coupon.is_active and coupon.expiry_date > datetime.now():
                    coupon.is_active = False
                    coupon.save()
                    wallet = Wallet.objects.filter(customer_id=customer_id).first()
                    wallet.value += coupon.value
                    wallet.save()

                    WalletHistory.objects.create(wallet=wallet,
                                                 type='Coupon', action='Credited', value=coupon.value)

                    return Response({'detail': 'Coupon redeemed successfully'}, status=200)
                else:
                    return Response({'detail': 'Coupon is expired or already used'}, status=404)
        except Exception as e:
            return Response({"detail": str(e)}, status=404)
