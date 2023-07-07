
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from shipping.Views import Shipping, Zone

urlpatterns = [
    # Shipping Region Crud
    path('shipping', Shipping.ShippingView.as_view(), name="ShippingView"),
    path('shipping/<int:pk>', Shipping.ShippingDetailView.as_view(), name="ShippingDetailView"),

    # Rule
    path('rule/<int:pk>', Shipping.RuleView.as_view(), name="RuleView"),

    # Conditional Rate
    path('conditional_rate/<int:pk>', Shipping.ConditionalRateView.as_view(), name="ConditionalRateView"),

    # Shipping Zones
    path('default_zone_list', Zone.DefaultZoneListView.as_view(), name="defaultZoneListView"),
    path('custom_zone_list', Zone.CustomZoneListView.as_view(), name="ZoneListView"),
    path('zone_list', Zone.ZoneListView.as_view(), name="ZoneListView"),
    path('zone', Zone.ZoneView.as_view(), name="ZoneView"),
    path('zone/<int:pk>', Zone.ZoneDetailView.as_view(), name="ZoneDetailView"),
    path('vendor_zone/<int:pk>', Zone.VendorZoneListView.as_view(), name="VendorZoneListView"),

    # shipping product group
    path('shipping_productgroup_list', Shipping.ShippingProductGroupListView.as_view(), name="productgroupListView"),

    # Count Apis
    path('zone_count', Shipping.ZoneCountView.as_view(), name="ZoneCountView"),
    path('region_count', Shipping.RegionCountView.as_view(), name="RegionCountView"),

]

schema_view = get_schema_view(
    openapi.Info(
        title="Shipping APIs Documentation",
        default_version='v1',
        description="This Documentation contains all the CRUD operations API needed for the Shipping application",
        terms_of_service="https://www.alchemative.com/privacy-policy",
        contact=openapi.Contact(email="app-support@alchemative.net"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[
        path('shipping/', include(urlpatterns))
    ],
)

urlpatterns += [
    # API Documentation route. (We are using Django Rest Swagger to sync with our API)
    path('docs', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
