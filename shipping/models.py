
from django.db import models
from authentication.models import TimeStampedModel
from setting.models import Region, Country, City
from products.models import ProductGroup
from vendor.models import Vendor


class Zone(TimeStampedModel):
    region = models.ManyToManyField(Region, related_name='zone_region')
    country = models.ManyToManyField(Country, related_name='zone_country')
    city = models.ManyToManyField(City, related_name='zone_city')
    title = models.CharField(max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True)

    class Meta:
        ordering = ('created_at',)
        indexes = [
            models.Index(fields=['title', ]),
        ]


class Shipping(TimeStampedModel):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, null=True, related_name='shipping_zone')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True, blank=True, related_name='shipping_vendor')
    product_group = models.ManyToManyField(ProductGroup, related_name='shipping_productgroup')

    title = models.CharField(max_length=200, blank=True, null=True)
    condition_type = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=250, blank=True, null=True)
    default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True)

    class Meta:
        ordering = ('created_at',)
        indexes = [
            models.Index(fields=['deleted', ]),
        ]


class Rule(TimeStampedModel):
    shipping = models.ForeignKey(Shipping, on_delete=models.CASCADE, related_name='rule_shipping')
    title = models.CharField(max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True)

    class Meta:
        ordering = ('created_at',)
        indexes = [
            models.Index(fields=['shipping', ]),
        ]


class ConditionalRate(TimeStampedModel):
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE, null=True, related_name='conditional_rate_rule')
    min_value = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    max_value = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(default=None, null=True)

    class Meta:
        ordering = ('created_at',)
        indexes = [
            models.Index(fields=['rule', ]),
        ]
