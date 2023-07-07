
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from storefront.Views import StorefrontCustomer as Customer
from authentication.BusinessLogic.NeglectDefaultAuthentications import neglect_authentication


urlpatterns = [
    path('signin', neglect_authentication(Customer.SignIn), name="SignIn"),
    path('signup', neglect_authentication(Customer.CustomerSignup), name="Signup"),

    path('account', neglect_authentication(Customer.CustomerAccount), name="account"),
    path('account_address_delete', neglect_authentication(Customer.AddressDelete), name="AddressDelete"),

    path('forget_password', neglect_authentication(Customer.CustomerForgetPasswordView), name="forget_password"),
    path('check_forgot_expiry', neglect_authentication(Customer.CheckForgotPasswordLinkExpiry), name="forget_password_expiry"),
    path('set_password', neglect_authentication(Customer.SetPassword), name="Set_password")

    # All Custom API methods
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
