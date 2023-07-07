
from django.db import models
from authentication.models import TimeStampedModel
from paymentgateway.models import GatewayCredentials


class StoreInformation(TimeStampedModel):
    store_name = models.TextField(blank=True, null=True)
    store_contact_email = models.TextField(blank=True, null=True)
    sender_email = models.TextField(blank=True, null=True)
    store_industry = models.TextField(blank=True, null=True)
    company_name = models.TextField(blank=True, null=True)
    phone_number = models.TextField(blank=True, null=True)
    address1 = models.TextField(blank=True, null=True)
    address2 = models.TextField(blank=True, null=True)
    country = models.TextField(blank=True, null=True)
    postal_code = models.TextField(blank=True, null=True)
    time_zone = models.TextField(blank=True, null=True)
    unit_system = models.TextField(blank=True, null=True)
    weight_units = models.TextField(blank=True, null=True)
    main_order_prefix = models.TextField(blank=True, null=True)
    order_counter = models.IntegerField(default=1000, blank=True, null=True)
    split_order_prefix = models.TextField(blank=True, null=True)
    store_currency = models.TextField(blank=True, null=True)
    # loyalty_enable = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['deleted', ]),
        ]


class StoreSetting(TimeStampedModel):
    domains = models.TextField(blank=True, null=True)
    development = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['deleted', ]),
        ]


class Tax(TimeStampedModel):
    tax_name = models.CharField(max_length=200, blank=True)
    tax_percentage = models.DecimalField(default=0, blank=True, null=True, decimal_places=2, max_digits=4)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['deleted', ]),
        ]


class PaymentMethod(TimeStampedModel):
    payment_gateway = models.ForeignKey(GatewayCredentials, on_delete=models.CASCADE, null=True, blank=True, related_name='paymentmethod_gateway')
    title = models.CharField(max_length=200, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    logo = models.CharField(max_length=200, null=True, blank=True)
    redirect_url = models.TextField(null=True, blank=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['deleted', ]),
        ]


# class ShippingMethod(TimeStampedModel):
#     name = models.CharField(max_length=200, blank=True, null=True)
#     amount = models.CharField(max_length=200, blank=True, null=True)
#     is_active = models.BooleanField(default=True)
#     deleted = models.BooleanField(default=False)
#     deleted_at = models.DateTimeField(default=None, null=True)


class Region(TimeStampedModel):
    name = models.CharField(max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True)

    class Meta:
        ordering = ('name',)
        indexes = [
            models.Index(fields=['deleted', ]),
        ]


class Country(TimeStampedModel):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True, related_name='country_region')
    name = models.CharField(max_length=200, blank=True, null=True)
    short_code = models.CharField(max_length=200, blank=True, null=True)
    country_code = models.CharField(max_length=200, blank=True, null=True)
    flags = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True)

    class Meta:
        ordering = ('name',)
        indexes = [
            models.Index(fields=['deleted', ]),
        ]


class City(TimeStampedModel):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True, related_name='city_country')
    name = models.CharField(max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True)

    class Meta:
        ordering = ('name',)
        indexes = [
            models.Index(fields=['deleted', ]),
        ]


class CheckoutSetting(TimeStampedModel):
    customer_accounts = models.CharField(max_length=200, blank=True, null=True)
    customer_contacts = models.CharField(max_length=200, blank=True, null=True)
    full_name = models.CharField(max_length=200, blank=True, null=True)
    address_second_line = models.CharField(max_length=200, blank=True, null=True)
    postal_code = models.CharField(max_length=200, blank=True, null=True)
    promo_code = models.CharField(max_length=200, blank=True, null=True)
    is_wallet = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True)

    class Meta:
        ordering = ('id',)


class LoyaltySetting(TimeStampedModel):
    amount_equal_point = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    point_equal_amount = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    start_loyalty_amount = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    minimum_orders_loyalty_start = models.IntegerField(default=0)
    minimum_point_redeem = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    is_active = models.BooleanField(default=True)
    is_paid = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['deleted', ]),
        ]


class Rule(TimeStampedModel):
    spending_amount = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    no_of_point = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    no_of_order = models.PositiveIntegerField(blank=True, null=True)
    type = models.CharField(max_length=200, null=True, blank=True)
    paid_order = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    start_date = models.DateTimeField(default=None, null=True, blank=True)
    end_date = models.DateTimeField(default=None, null=True, blank=True)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['deleted', ]),
        ]
