
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from authentication.BusinessLogic.NeglectDefaultAuthentications import neglect_authentication
from discount.Views import Discount, CheckoutPromoCode

urlpatterns = [
    # Products Crud
    path('discount', Discount.DiscountView.as_view(), name="Discount"),
    path('discount/<int:pk>', Discount.DiscountDetailView.as_view(), name="Discount_detail"),
    path('discount_list', Discount.DiscountListView.as_view(), name="Discount_list"),
    path('discount_status_change', Discount.DiscountStatusChange.as_view(), name="Discount_status_change"),
    path('bulk_discount_delete', Discount.DiscountBulkDelete.as_view(), name="bulk_discount_delete"),

    # checkout promocode
    path('apply_promo', neglect_authentication(CheckoutPromoCode.PromoCodeView), name="PromoCodeView"),

]

schema_view = get_schema_view(
    openapi.Info(
        title="Discount APIs Documentation",
        default_version='v1',
        description="This Documentation contains all the CRUD operations API needed for the Discount application",
        terms_of_service="https://www.alchemative.com/privacy-policy",
        contact=openapi.Contact(email="app-support@alchemative.net"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[
        path('discount/', include(urlpatterns))
    ],
)


urlpatterns += [
   # API Documentation route. (We are using Django Rest Swagger to sync with our API)
   path('docs', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]