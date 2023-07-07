
from django.db import models
import jsonfield
from authentication.models import TimeStampedModel


class GatewayCredentials(TimeStampedModel):
    gateway_name = models.CharField(max_length=200, blank=True, null=True)
    brand_name = models.CharField(max_length=200, blank=True, null=True)
    credentials = jsonfield.JSONField(blank=True, null=True)
    certificatePath = models.TextField(max_length=100, blank=True, null=True)
    # description = models.TextField(max_length=200, blank=True, null=True)
    test_mode = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['deleted', ]),
        ]


class PaymentTransactions(TimeStampedModel):
    checkout_id = models.CharField(max_length=100, blank=True, null=True)
    customer_first_name = models.TextField(max_length=100, blank=True, null=True)
    customer_last_name = models.TextField(max_length=100, blank=True, null=True)
    callback_url = models.TextField(max_length=200, blank=True, null=True)
    complete_url = models.TextField(max_length=200, blank=True, null=True)
    cancel_url = models.TextField(max_length=200, blank=True, null=True)
    currency = models.TextField(max_length=100, blank=True, null=True)
    signature = models.TextField(max_length=100, blank=True, null=True)
    order_amount = models.TextField(max_length=100, blank=True, null=True)
    order_status = models.TextField(max_length=100, blank=True, null=True)
    txn_ref_no = models.TextField(max_length=100, blank=True, null=True)
    expiry_time = models.DateTimeField(default=None, null=True, blank=True)
    test_mode = models.BooleanField(default=False)

    # Pay2m response values
    access_token = models.TextField(max_length=100, blank=True, null=True)
    response_code = models.TextField(max_length=100, blank=True, null=True)
    response_message = models.TextField(max_length=100, blank=True, null=True)
    response_status = models.TextField(max_length=20, blank=True, null=True)
    transaction_id = models.TextField(max_length=20, blank=True, null=True)

    card_band = models.TextField(max_length=100, blank=True, null=True)
    card_expiry_month = models.TextField(max_length=100, blank=True, null=True)
    card_expiry_year = models.TextField(max_length=100, blank=True, null=True)
    card_funding_method = models.TextField(max_length=100, blank=True, null=True)
    card_name_on_card = models.TextField(max_length=100, blank=True, null=True)
    card_number = models.TextField(max_length=100, blank=True, null=True)
    card_scheme = models.TextField(max_length=100, blank=True, null=True)
    fund_type = models.TextField(max_length=100, blank=True, null=True)
    payment_status = models.TextField(max_length=100, blank=True, null=True)
    total_authorized_amount = models.TextField(max_length=100, blank=True, null=True)
    total_captured_amount = models.TextField(max_length=100, blank=True, null=True)
    total_refunded_amount = models.TextField(max_length=100, blank=True, null=True)

    # for stripe
    stripe_publishable_key = models.TextField(max_length=250, blank=True, null=True)
    stripe_secret_key = models.TextField(max_length=250, blank=True, null=True)
    stripe_session_id = models.TextField(max_length=250, blank=True, null=True)
    stripe_payment_intent = models.TextField(max_length=250, blank=True, null=True)

    # Bykea
    invoice_no = models.TextField(max_length=200, blank=True, null=True)
    invoice_reference = models.TextField(max_length=200, blank=True, null=True)
    invoice_url = models.TextField(blank=True, null=True)

    # PayPro
    response_description = models.TextField(max_length=250, blank=True, null=True)
    request_status = models.TextField(max_length=250, blank=True, null=True)
    fetch_order_type = models.TextField(max_length=250, blank=True, null=True)
    click_2Pay = models.TextField(max_length=250, blank=True, null=True)
    description = models.TextField(max_length=250, blank=True, null=True)
    connect_pay_id = models.TextField(max_length=250, blank=True, null=True)
    order_number = models.TextField(max_length=250, blank=True, null=True)
    is_fee_applied = models.TextField(max_length=250, blank=True, null=True)
    connect_pay_fee = models.TextField(max_length=250, blank=True, null=True)

    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['deleted', ]),
        ]
