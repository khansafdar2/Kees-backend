
from order.models import Checkout, LineItems, ShippingAddress
from products.models import ProductGroup, Variant
from shipping.models import Shipping, ConditionalRate


def shipping_calculate(checkout_id):
    line_items = LineItems.objects.filter(checkout__checkout_id=checkout_id, deleted=False)

    product_groups = []

    shipping = ShippingAddress.objects.filter(checkout__checkout_id=checkout_id, deleted=False).first()
    city = shipping.city

    shipping_amount = 0
    for line_item in line_items:
        variant = Variant.objects.filter(id=line_item.variant_id).first()
        product_group = ProductGroup.objects.filter(product_group__product_variant=variant).first()

        if product_group not in product_groups:
            product_groups.append(product_group)
            if variant:
                shipping = Shipping.objects.filter(product_group=product_group, zone__city__name=city).first()

                if shipping:
                    rates = ConditionalRate.objects.filter(shipping=shipping)
                    for rate in rates:
                        min_value = rate.min_value
                        max_value = rate.max_value
                        amount = rate.amount

                        if shipping.condition_type == 'weight':
                            product_value = variant.weight
                        elif shipping.condition_type == 'fixed':
                            product_value = variant.price
                        else:
                            product_value = None

                        if product_value is not None:
                            if min_value == 0:
                                if product_value <= max_value:
                                    shipping_amount += amount
                            elif max_value == 0:
                                if product_value >= min_value:
                                    shipping_amount += amount
                            elif min_value <= product_value <= max_value:
                                shipping_amount += amount
                            else:
                                pass

    checkout = Checkout.objects.filter(checkout_id=checkout_id)
    checkout.total_shipping = shipping_amount
    checkout.save()

    return shipping_amount

