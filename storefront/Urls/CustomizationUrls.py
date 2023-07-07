
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from storefront.Views import Customization, ContactUs, CheckoutCustomization
from authentication.BusinessLogic.NeglectDefaultAuthentications import neglect_authentication


urlpatterns = [
    path('homepage', neglect_authentication(Customization.HomePageView), name="HomePage"),
    path('header', neglect_authentication(Customization.HeaderView), name="Header"),
    path('footer', neglect_authentication(Customization.FooterView), name="Footer"),
    path('newsletter', neglect_authentication(Customization.NewsletterView), name="Newsletter"),
    path('contact-us', neglect_authentication(ContactUs.ContactUs), name="contactus"),
    path('checkout_setting', neglect_authentication(CheckoutCustomization.CheckoutCustomizationView), name="checkout_setting"),

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
