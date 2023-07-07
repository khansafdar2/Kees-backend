
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from vendor.Views import Vendor, VendorOrder, VendorContentApproval
from authentication.BusinessLogic.NeglectDefaultAuthentications import neglect_authentication

urlpatterns = [
    # Vendors CRUD API
    path('vendor_list', Vendor.VendorListView.as_view(), name="VendorListView"),
    path('vendor', Vendor.VendorView.as_view(), name="VendorView"),
    path('external_signup', neglect_authentication(Vendor.VendorStoreFrontView), name="VendorStoreFrontView"),
    path('vendor/<int:pk>', Vendor.VendorDetailView.as_view(), name="VendorDetailView"),
    path('vendor_approval', Vendor.VendorApprovalView.as_view(), name="VendorApprovalView"),
    path('vendor_status_change', Vendor.VendorStatusChange.as_view(), name="VendorStatusChange"),
    path('vendor_order_list', VendorOrder.VendorOrderListView.as_view(), name="VendorOrderListView"),
    path('commission_list', Vendor.CommissionView.as_view(), name="CommissionView"),
    path('commission/<int:pk>', Vendor.CommissionView.as_view(), name="CommissionView"),

    path('approval_content', VendorContentApproval.VendorContentListView.as_view(), name="VendorContentListView"),
    path('change_approval_status', VendorContentApproval.VendorContentStatusChangeView.as_view(), name="VendorContentStatusChangeView"),

]


schema_view = get_schema_view(
    openapi.Info(
        title="Vendor Management APIs Documentation",
        default_version='v1',
        description="This Documentation contains all the CRUD operations API needed for the Vendor Management "
                    "application",
        terms_of_service="https://www.alchemative.com/privacy-policy",
        contact=openapi.Contact(email="app-support@alchemative.net"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[
        path('vendors/', include(urlpatterns))
    ],
)

urlpatterns += [
    # API Documentation route. (We are using Django Rest Swagger to sync with our API)
    path('docs', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]