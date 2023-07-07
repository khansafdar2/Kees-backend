
from rest_framework import serializers
from crm.models import Wallet, WalletHistory, Coupon


class WalletSerializer(serializers.ModelSerializer):
    coupons = serializers.SerializerMethodField('get_coupon')

    class Meta:
        model = Wallet
        fields = '__all__'

    def get_coupon(self, obj):
        serializer_context = {'request': self.context.get('request')}
        coupon = Coupon.objects.filter(customer_id=obj.customer_id, is_active=True, is_deleted=False)
        serializer = CouponListSerializer(coupon, many=True, context=serializer_context)
        return serializer.data


class WalletHistoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletHistory
        fields = '__all__'


class CouponListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'
