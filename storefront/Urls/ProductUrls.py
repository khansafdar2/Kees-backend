
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from storefront.Views import StorefrontProducts as Products
from authentication.BusinessLogic.NeglectDefaultAuthentications import neglect_authentication


urlpatterns = [
    path('product_list', neglect_authentication(Products.ProductView), name="product_list"),
    path('product/<slug:slug>', neglect_authentication(Products.ProductDetailView), name="product_detail_view"),

    path('search_products', neglect_authentication(Products.ProductSearchView), name="product_search_view"),

    path('productlistbanner', neglect_authentication(Products.BannerView), name="BannerView"),

    # All Custom API methods
    path('visited_products', neglect_authentication(Products.MostVisitedProducts), name="VisitedProducts"),
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
