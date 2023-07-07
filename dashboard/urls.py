
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from dashboard.Views import \
    DashboardCount, \
    OrdersReport

urlpatterns = [
    # Products Crud
    path('revenue', DashboardCount.Revenue.as_view(), name="Revenue"),
    path('order_analysis', DashboardCount.OrderAnalysis.as_view(), name="OrderAnalysis"),
    path('product_analysis', DashboardCount.ProductAnalysis.as_view(), name="ProductAnalysis"),
    path('top_sold_items', DashboardCount.TopSoldItems.as_view(), name="TopSoldItems"),
    path('sale_by_city', DashboardCount.SaleByCity.as_view(), name="SaleByCity"),
    path('sale_by_category', DashboardCount.SaleByCategory.as_view(), name="SaleByCategory"),
    path('sale_by_month', DashboardCount.SaleByMonth.as_view(), name="SaleByMonth"),
    path('sale_by_vendor', DashboardCount.SaleByVendor.as_view(), name="SaleByVendor"),
    path('orders_report', OrdersReport.OrdersReport.as_view(), name="OrdersReport"),
]

schema_view = get_schema_view(
    openapi.Info(
        title="Dashboard APIs Documentation",
        default_version='v1',
        description="This Documentation contains all the CRUD operations API needed for the Products application",
        terms_of_service="https://www.alchemative.com/privacy-policy",
        contact=openapi.Contact(email="app-support@alchemative.net"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[
        path('dashboard/', include(urlpatterns))
    ],
)


urlpatterns += [
   # API Documentation route. (We are using Django Rest Swagger to sync with our API)
   path('docs', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
