from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from order.Views import Checkout, CheckoutOrder, ProductList, OrderCustomer, DraftOrder, ParentOrder, ChildOrder \
    , OrdersExport, OrderInvoice
from authentication.BusinessLogic.NeglectDefaultAuthentications import neglect_authentication

urlpatterns = [
    path('checkout', neglect_authentication(Checkout.CheckoutView), name="CheckoutView"),
    path('checkout/<int:pk>', neglect_authentication(Checkout.CheckoutDetailView), name="CheckoutDetailView"),
    path('checkout_thankyou/<int:pk>', neglect_authentication(Checkout.ThankYouView), name="ThankYouView"),
    path('delete_line_item', neglect_authentication(Checkout.DeleteLineItem), name="DeleteLineItem"),
    path('verify_wallet_amount', neglect_authentication(Checkout.CheckWalletAmount), name="CheckWalletAmount"),

    path('shipping_price', neglect_authentication(Checkout.CheckoutShippingPrice), name="CheckoutShippingPrice"),
    path('payment_method', neglect_authentication(Checkout.PaymentMethodList), name="PaymentMethodList"),
    path('payment_gateway_method', neglect_authentication(Checkout.PaymentGatewayList), name="PaymentGatewayList"),
    path('payment_gateway_select', neglect_authentication(Checkout.GatewayPaymentMethod), name="GatewayPaymentMethod"),

    # Countries & Cities for Checkout
    path('countries', neglect_authentication(Checkout.GetCountriesAtCheckoutView), name="GetCountriesAtCheckoutView"),
    path('cities', neglect_authentication(Checkout.GetCitiesAtCheckoutView), name="GetCitiesAtCheckoutView"),

    # Storefront Orders Url
    path('place_order', neglect_authentication(CheckoutOrder.OrderView), name="Orders"),
    path('order_detail', neglect_authentication(CheckoutOrder.OrderDetailView), name="OrderDetail"),

    # Admin Panel Order
    path('parent_order_list', ParentOrder.ParenttOrderListView.as_view(), name="ParenttOrderListView"),
    path('parent_order', ParentOrder.ParentOrderView.as_view(), name="ParenttOrderView"),
    path('order_status_change', ParentOrder.ParentOrderStatusChange.as_view(), name="ParentOrderStatusChange"),
    path('parent_order/<int:pk>', ParentOrder.ParentOrderDetailView.as_view(), name="ParenttOrderDetailView"),
    path('refund_parent_order/<int:pk>', ParentOrder.RefundOrderView.as_view(), name="RefendOrderView"),

    path('childorder/<int:pk>', ChildOrder.ChildOrderDetailView.as_view(), name="ChildOrderDetailView"),
    path('childorder', ChildOrder.ChildOrderView.as_view(), name="ChildOrderView"),

    path('refund_child_order/<int:pk>', ChildOrder.RefundChildOrderView.as_view(), name="RefundChildOrderView"),

    path('childorder_lineitem/<int:pk>', ChildOrder.ChildOrderListItemView.as_view(), name="ChildOrderLineitemView"),

    path('childorder_status_change', ChildOrder.ChildOrderStatusChange.as_view(), name="ChildOrderStatusChange"),

    # Order Products
    path('orders_product_list', ProductList.ProductListView.as_view(), name="OrderProductListView"),

    # Order Customers
    path('orders_customer_list', OrderCustomer.OrderCustomerListView.as_view(), name="OrderCustomerListView"),

    # Admin Order
    path('draft_order_list', DraftOrder.DraftOrderListView.as_view(), name="DraftOrderListView"),
    path('draft_order', DraftOrder.DraftOrderView.as_view(), name="DraftOrderView"),
    path('draft_order/<int:pk>', DraftOrder.DraftOrderDetailView.as_view(), name="DraftOrderDetailView"),

    # Orders Export
    path('orders_export', OrdersExport.OrdersExport.as_view(), name="OrdersExport"),

    # order history
    path('order_history', ParentOrder.OrderHistoryView.as_view(), name="OrderHistory"),

    # order invoice
    path('orders_invoice', OrderInvoice.Invoice.as_view(), name="OrdersInvoice"),

    # verify product shipping
    path('verify_product_shipping', Checkout.VerifyProductShipping.as_view(), name="VerifyProduct"),

    # Loyalty Urls
    path('loyalty', neglect_authentication(ParentOrder.LoyaltyPointCalculation), name="Loyalty"),

    # Checkout Line Items
    path('checkout_line_items', neglect_authentication(Checkout.CheckoutLineItems), name="CheckoutLineItems")

]

schema_view = get_schema_view(
    openapi.Info(
        title="Orders (Orders Management System) APIs Documentation",
        default_version='v1',
        description="This Documentation contains all the CRUD operations API needed for the cms application",
        terms_of_service="https://www.alchemative.com/privacy-policy",
        contact=openapi.Contact(email="app-support@alchemative.net"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[
        path('order/', include(urlpatterns))
    ],
)

urlpatterns += [
    # API Documentation route. (We are using Django Rest Swagger to sync with our API)
    path('docs', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
