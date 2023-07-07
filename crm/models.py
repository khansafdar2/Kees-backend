
import uuid
from django.db import models
from authentication.models import TimeStampedModel
from authentication.models import User
from setting.models import Rule


# Create your models here.
class Customer(TimeStampedModel):
    rule = models.ManyToManyField(Rule, related_name='customer_rule')
    points = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    first_name = models.CharField(blank=True, null=True, max_length=200)
    last_name = models.CharField(blank=True, null=True, max_length=200)
    token = models.CharField(blank=True, null=True, max_length=200)
    last_login = models.DateTimeField(blank=True, null=True)
    phone = models.CharField(blank=True, null=True, max_length=200)
    email = models.EmailField(blank=True, null=True)
    password = models.CharField(blank=True, null=True, max_length=200)
    notes = models.TextField(blank=True, null=True)
    tags = models.TextField(blank=True, null=True)
    has_account = models.BooleanField(default=False)
    one_time = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['deleted', ]),
        ]


class CustomerForgetPassword(TimeStampedModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="Customer_ForgetPassword")
    key = models.CharField(blank=True, null=True, max_length=200)
    accepted = models.BooleanField(default=False)
    sent = models.BooleanField(default=False)
    expired = models.BooleanField(default=False)


class Notes(TimeStampedModel):
    text = models.TextField()
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='customer_notes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crm_notes_user')


class Address(TimeStampedModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="customer_address", null=True)
    first_name = models.CharField(blank=True, null=True, max_length=200)
    last_name = models.CharField(blank=True, null=True, max_length=200)
    company = models.CharField(blank=True, null=True, max_length=200)
    phone = models.CharField(blank=True, null=True, max_length=200)
    address = models.TextField(blank=True, null=True)
    apartment = models.TextField(blank=True, null=True)
    city = models.CharField(blank=True, null=True, max_length=200)
    country = models.CharField(blank=True, null=True, max_length=200)
    postal_code = models.CharField(blank=True, null=True, max_length=50)
    primary_address = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['deleted', ]),
        ]


class Tags(TimeStampedModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="CustomerTags")
    name = models.CharField(blank=True, null=True, max_length=200)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['deleted', ]),
        ]


class Wallet(TimeStampedModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='wallet_customer')
    unique_id = models.CharField(blank=True, null=True, max_length=200)
    value = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=10, default=0.00)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)


class Coupon(TimeStampedModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='coupon_customer')
    value = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    name = models.CharField(blank=True, null=True, max_length=200)
    unique_id = models.CharField(blank=True, null=True, max_length=200)
    note = models.TextField(blank=True, null=True,)
    expiry_date = models.DateTimeField(default=None, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)


class WalletHistory(TimeStampedModel):
    wallet = models.ForeignKey(Wallet, on_delete=models.DO_NOTHING)
    type = models.CharField(blank=True, null=True, max_length=200)
    action = models.CharField(blank=True, null=True, max_length=200)
    value = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['wallet', ]),
        ]

