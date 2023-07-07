
from django.db import models
from authentication.models import TimeStampedModel
from discount.models import Discount
from shipping.models import Shipping
from products.models import Variant
from vendor.models import Vendor
from crm.models import Customer


class Order(TimeStampedModel):
    # fulfillment = (
    #     ('FULFILLED', 'Fulfilled'),
    #     ('UNFULFILLED', 'Unfulfilled'),
    #     ('PARTIALLY', 'Partially Fulfilled')
    # )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True, related_name="order_customer")
    name = models.CharField(max_length=200, blank=True, null=True)
    order_id = models.TextField(blank=True, null=True)
    payment_method = models.CharField(max_length=200, blank=True, null=True)
    paid_amount = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    subtotal_price = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    tax_applied = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    total_shipping = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    total_price = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    discounted_price = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    fulfillment_status = models.CharField(max_length=200, default='Unfulfilled')
    payment_status = models.CharField(max_length=200, blank=True, null=True)
    order_status = models.CharField(max_length=200, blank=True, null=True)
    refund_type = models.CharField(max_length=200, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    tags = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ('-id',)
        indexes = [
            models.Index(fields=['customer', ]),
        ]


class DraftOrder(TimeStampedModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True, related_name="draft_order_customer")
    name = models.CharField(max_length=200, blank=True, null=True)
    payment_status = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=200, default='draft')
    notes = models.TextField(blank=True, null=True)
    tags = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['id', ]),
        ]


class Checkout(TimeStampedModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True, related_name="checkout_customer")
    checkout_id = models.CharField(max_length=200, blank=True, null=True, unique=True)
    email = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=200, blank=True, null=True)
    promo_code = models.CharField(max_length=200, blank=True, null=True)
    payment_method = models.CharField(max_length=200, blank=True, null=True)
    subtotal_price = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    total_shipping = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    discounted_price = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    paid_by_wallet = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    is_processing = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['deleted', ]),
        ]


class BillingAddress(TimeStampedModel):
    checkout = models.ForeignKey(Checkout, on_delete=models.CASCADE,  null=True, blank=True, related_name="billingaddress_checkout")
    order = models.ForeignKey(Order, on_delete=models.CASCADE,  null=True, blank=True, related_name="billingaddress_order")
    draft_order = models.ForeignKey(DraftOrder, on_delete=models.CASCADE, null=True, blank=True, related_name="billingaddress_draft_order")
    first_name = models.CharField(blank=True, null=True, max_length=200)
    last_name = models.CharField(blank=True, null=True, max_length=200)
    company = models.CharField(blank=True, null=True, max_length=200)
    phone = models.CharField(blank=True, null=True, max_length=200)
    address = models.TextField(blank=True, null=True)
    apartment = models.TextField(blank=True, null=True)
    city = models.CharField(blank=True, null=True, max_length=200)
    country = models.CharField(blank=True, null=True, max_length=200)
    postal_code = models.CharField(blank=True, null=True, max_length=50)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['deleted', ]),
        ]


class ShippingAddress(TimeStampedModel):
    checkout = models.ForeignKey(Checkout, on_delete=models.CASCADE,  null=True, blank=True, related_name="shippingaddress_checkout")
    order = models.ForeignKey(Order, on_delete=models.CASCADE,  null=True, blank=True, related_name="shippingaddress_order")
    draft_order = models.ForeignKey(DraftOrder, on_delete=models.CASCADE, null=True, blank=True, related_name="shippingaddress_draft_order")
    first_name = models.CharField(blank=True, null=True, max_length=200)
    last_name = models.CharField(blank=True, null=True, max_length=200)
    company = models.CharField(blank=True, null=True, max_length=200)
    phone = models.CharField(blank=True, null=True, max_length=200)
    address = models.TextField(blank=True, null=True)
    apartment = models.TextField(blank=True, null=True)
    city = models.CharField(blank=True, null=True, max_length=200)
    country = models.CharField(blank=True, null=True, max_length=200)
    postal_code = models.CharField(blank=True, null=True, max_length=50)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['deleted', ]),
        ]


class LineItems(TimeStampedModel):
    checkout = models.ForeignKey(Checkout, on_delete=models.CASCADE,  null=True, blank=True, related_name="lineitem_checkout")
    order = models.ForeignKey(Order, on_delete=models.CASCADE,  null=True, blank=True, related_name="lineitem_order")
    draft_order = models.ForeignKey(DraftOrder, on_delete=models.CASCADE, null=True, blank=True, related_name="lineitem_draft_order")
    shipping = models.ForeignKey(Shipping, on_delete=models.SET_NULL, null=True, blank=True, related_name="lineitem_shipping")
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="lineitem_vendor")
    variant = models.ForeignKey(Variant, on_delete=models.DO_NOTHING, null=True, blank=True, related_name="lineitem_variant")
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE, null=True, blank=True, related_name="lineitem_discount")
    promo_code = models.CharField(max_length=200, blank=True, null=True)
    product_title = models.CharField(max_length=200, blank=True, null=True)
    variant_title = models.CharField(max_length=200, blank=True, null=True)
    product_image = models.TextField(blank=True, null=True)
    quantity = models.IntegerField(default=0)
    vendor_commission = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    price = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    compare_at_price = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    total_price = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    shipping_name = models.CharField(max_length=200, blank=True, null=True)
    shipping_amount = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['deleted', ]),
        ]


class ChildOrder(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="childOrders_order")
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.CASCADE, blank=True, null=True, related_name="childOrders_shippingAddress")
    billing_address = models.ForeignKey(BillingAddress, on_delete=models.CASCADE, blank=True, null=True, related_name="childOrders_billingAddress")
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="child_vendor")
    name = models.CharField(max_length=200, blank=True, null=True)
    payment_method = models.CharField(max_length=200, blank=True, null=True)
    paid_amount = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    subtotal_price = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    tax_applied = models.CharField(max_length=200, blank=True, null=True)
    total_shipping = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    total_price = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    discounted_price = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    fulfillment_status = models.CharField(max_length=200, default='Unfulfilled')
    payment_status = models.CharField(max_length=200, blank=True, null=True)
    order_status = models.CharField(max_length=200, blank=True, null=True)
    refund_type = models.CharField(max_length=200, blank=True, null=True)
    tags = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['id', ]),
        ]


class ChildOrderLineItems(TimeStampedModel):
    variant = models.ForeignKey(Variant, on_delete=models.DO_NOTHING, null=True, blank=True, related_name="child_lineitem_variant")
    child_order = models.ForeignKey(ChildOrder, on_delete=models.CASCADE,  null=True, blank=True, related_name="child_order_lineitem_order")
    shipping = models.ForeignKey(Shipping, on_delete=models.SET_NULL, null=True, blank=True, related_name="childlineitem_shipping")
    product_title = models.CharField(max_length=200, blank=True, null=True)
    variant_title = models.CharField(max_length=200, blank=True, null=True)
    product_image = models.TextField(blank=True, null=True)
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    compare_at_price = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    total_price = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    shipping_name = models.CharField(max_length=200, blank=True, null=True)
    shipping_amount = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    vendor_commission = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['id', ]),
        ]


class OrderHistory(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING, null=True, blank=True)
    child_order = models.ForeignKey(ChildOrder, on_delete=models.DO_NOTHING, null=True, blank=True)
    message = models.CharField(blank=True, null=True, max_length=200)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['order', 'child_order']),
        ]
