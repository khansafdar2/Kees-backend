from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from storefront.Views import CustomerWallet
from authentication.BusinessLogic.NeglectDefaultAuthentications import neglect_authentication


urlpatterns = [
    path('get_wallet/<int:pk>', neglect_authentication(CustomerWallet.GetWalletView), name="GetWalletView"),
    path('redeem_loyalty_points', neglect_authentication(CustomerWallet.RedeemLoyaltyPointsView),
         name="RedeemLoyaltyPointsView"),
    path('get_loyalty_points/<int:pk>', neglect_authentication(CustomerWallet.GetLoyaltyPointsView),
         name="GetLoyaltyPointsView"),
    path('debit_wallet_amount', neglect_authentication(CustomerWallet.DebitWalletAmountView),
         name="DebitWalletAmountView"),
    path('get_wallet_history/<int:pk>', neglect_authentication(CustomerWallet.WalletHistoryListView),
         name="WalletHistoryListView"),
    path('get_coupon_list/<int:pk>', neglect_authentication(CustomerWallet.GetCouponListView), name="GetCouponListView"),
    path('redeem_coupon', neglect_authentication(CustomerWallet.RedeemCouponView), name="RedeemCouponView"),
]

schema_view = get_schema_view(
    openapi.Info(
        title="Storefront (StoreFront Management System) APIs Documentation",
        default_version='v1',
        description="This Documentation contains all the CRUD operations API needed for the cms application",
        terms_of_service="https://www.alchemative.com/privacy-policy",
        contact=openapi.Contact(email="app-support@alchemative.net"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[
        path('storefront/', include(urlpatterns))
    ],
)

urlpatterns += [
    # API Documentation route. (We are using Django Rest Swagger to sync with our API)
    path('docs', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
