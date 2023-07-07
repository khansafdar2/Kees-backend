from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from crm.Views import Customer, Coupon

urlpatterns = [
    # All CMS CRUD APIs needed
    path('customer_list', Customer.CustomerListView.as_view(), name="CustomerListView"),
    path('customer', Customer.CustomerView.as_view(), name="CustomerView"),
    path('customer/<int:pk>', Customer.CustomerDetailView.as_view(), name="CustomerDetailView"),
    path('address/<int:pk>', Customer.AddressDelete.as_view(), name="AddressDelete"),
    path('customer_status_change', Customer.CustomerStatusChange.as_view(), name="CustomerStatusChange"),

    # Coupon Urls
    path('coupon_list', Coupon.CouponListView.as_view(), name="CouponListView"),
    path('coupon', Coupon.CouponView.as_view(), name="CouponView"),
    path('coupon/<int:pk>', Coupon.CouponDetailView.as_view(), name="CouponDetailView"),
    path('wallet_creation', Coupon.CustomScriptForWalletCreation.as_view(), name="CustomScriptForWalletCreation"),

    # All Custom API methods
]

schema_view = get_schema_view(
    openapi.Info(
        title="CRM (Customer Relationship Management) APIs Documentation",
        default_version='v1',
        description="This Documentation contains all the CRUD operations API needed for the CRM application",
        terms_of_service="https://www.alchemative.com/privacy-policy",
        contact=openapi.Contact(email="app-support@alchemative.net"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[
        path('crm/', include(urlpatterns))
    ],
)

urlpatterns += [
    # API Documentation route. (We are using Django Rest Swagger to sync with our API)
    path('docs', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
