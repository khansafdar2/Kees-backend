
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Vendor(models.Model):
    # Basic Details
    name = models.CharField(max_length=200, blank=True, null=True)
    unique_id = models.CharField(max_length=200, blank=True, null=True)
    email = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=200, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    notes = models.TextField(null=True, blank=True)

    commission_value = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)

    license_number = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(default='Pending', max_length=200)

    # Document
    trade_license = models.CharField(max_length=200, blank=True, null=True)
    national_id = models.CharField(max_length=200, blank=True, null=True)

    # Store Details
    store_name = models.CharField(max_length=200, blank=True, null=True)
    company_phone = models.CharField(max_length=200, blank=True, null=True)
    products_you_sell = models.CharField(max_length=200, blank=True, null=True)

    # Financial Details
    beneficiary_name = models.CharField(max_length=200, blank=True, null=True)
    bank_name = models.CharField(max_length=200, blank=True, null=True)
    branch_name = models.CharField(max_length=200, blank=True, null=True)
    account_number = models.CharField(max_length=200, blank=True, null=True)
    iban = models.CharField(max_length=200, blank=True, null=True)
    swift_code = models.CharField(max_length=200, blank=True, null=True)
    cancel_check = models.CharField(max_length=200, blank=True, null=True)

    # Others
    notify_less_inventory = models.BooleanField(default=False)
    sku_prefix = models.BooleanField(default=False)

    # Approval
    is_approval = models.BooleanField(default=False)
    product_approval = models.BooleanField(default=False)
    collection_approval = models.BooleanField(default=False)
    product_group_approval = models.BooleanField(default=False)
    discount_approval = models.BooleanField(default=False)
    shipping_approval = models.BooleanField(default=False)

    is_active = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['deleted', 'id']),
        ]


class Commission(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='commission_vendor')
    title = models.CharField(max_length=200, blank=True, null=True)
    type = models.CharField(max_length=200, blank=True, null=True)
    value = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['deleted', 'id']),
        ]


class DataApproval(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True, blank=True, related_name='data_approval_vendor')
    title = models.CharField(max_length=200, blank=True, null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    action_perform_by = models.CharField(max_length=200, blank=True, null=True)
    action_perform_at = models.DateTimeField(blank=True, null=True)
    requested_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    status = models.CharField(max_length=250, blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['object_id', ]),
        ]
