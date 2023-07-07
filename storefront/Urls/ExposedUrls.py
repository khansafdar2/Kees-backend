
from django.urls import path
from storefront.Views import ExposedApis
from authentication.BusinessLogic.NeglectDefaultAuthentications import neglect_authentication


urlpatterns = [
    path('products', neglect_authentication(ExposedApis.ProductListView), name="ProductListView"),
    path('orders', neglect_authentication(ExposedApis.ParenttOrderListView), name="ParenttOrderListView"),
    path('customers', neglect_authentication(ExposedApis.CustomerListView), name="CustomerListView"),
]
