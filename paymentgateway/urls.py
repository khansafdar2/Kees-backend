
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from paymentgateway.Views import Pay2m, GatewayCredentials, BAF, MCB, Stripe, Bykea, PayPro, UBL, QisstPay
from setting.BusinessLogic import SecureApi
from paymentgateway.Views import Pay2m, GatewayCredentials, BAF, MCB, Stripe, Bykea, PayPro, Jazzcash, Nift, HBL

urlpatterns = [
   # All Payment Gateway CRUD APIs needed
   path('gateway_credentials', GatewayCredentials.GatewayCredentialsView.as_view(), name='GatewayCredentials'),
   path('gateway_credentials/<int:pk>', GatewayCredentials.GatewayCredentialsDetailView.as_view(), name='GatewayCredentials'),

   # Pay2m
   path('pay2m_request', Pay2m.pay2m_view, name='pay2m'),
   path('process_request', Pay2m.process_request, name='process_request'),

   # Jazzcash
   path('jazzcash_request', Jazzcash.jazzcash_view, name='jazzcash'),
   path('jazzcash_process_request', Jazzcash.jazzcash_process_request, name='jazzcash_process_request'),

   # Nift
   path('nift_request', Nift.nift_view, name='nift'),
   path('nift_process_request', Nift.nift_process_request, name='nift_process_request'),

   # Bank Alfalah
   path('baf_request', BAF.baf_view, name='baf'),
   path('baf_process_request', BAF.baf_response, name='baf_process_request'),

   # MCB
   path('mcb_request', MCB.index, name='mcb'),
   path('mcb_process_request', MCB.mcb_response, name='mcb_process_request'),

   # Stripe
   path('stripe_request', Stripe.index, name='stripe'),
   path('stripe_success_request', Stripe.success_response, name='stripe_success_request'),
   path('stripe_failed_request', Stripe.failed_response, name='stripe_failed_request'),

   # Bykea
   path('bykea_request', Bykea.index, name='bykea'),
   path('bykea_success_request', Bykea.success_response, name='bykea_success'),
   path('bykea_failure_request', Bykea.failed_response, name='bykea_success'),

   # PayPro
   path('paypro_request', PayPro.index, name='paypro'),
   path('paypro_response', PayPro.response),
   path('paypro_listener_response', PayPro.listener_response),

   # UBL
   path('ubl_request', UBL.index, name='ubl'),
   path('ubl_response', UBL.response, name='ubl_response'),

   # Qisst Pay
   path('qisstpay_request', QisstPay.index, name='qisst_pay'),
   path('qisstpay_response', QisstPay.response, name='qissat_pay_response'),

   # HBL
   path('hbl_request', HBL.index, name='hbl'),
   # path('hbl_response', HBL.response, name='hbl_response'),

]


schema_view = get_schema_view(
   openapi.Info(
      title="Payment Gateway APIs Documentation",
      default_version='v1',
      description="This Documentation contains all the CRUD operations API needed for the payment gateway application",
      terms_of_service="https://www.alchemative.com/privacy-policy",
      contact=openapi.Contact(email="app-support@alchemative.net"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
   patterns=[
      path('paymentgateway/', include(urlpatterns))
   ],
)


urlpatterns += [
   # API Documentation route. (We are using Django Rest Swagger to sync with our API)
   path('docs', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]