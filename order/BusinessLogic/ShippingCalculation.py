
from shipping.models import Rule, ConditionalRate


def calculate_shipping(shipping, order_weight, order_price):
    shipping_rule = []
    rules = Rule.objects.filter(shipping=shipping, is_active=True, deleted=False)
    for rule in rules:
        rates = ConditionalRate.objects.filter(rule=rule, is_active=True, deleted=False)
        for rate in rates:
            min_value = rate.min_value
            max_value = rate.max_value
            amount = rate.amount

            if shipping.condition_type == 'weight':
                product_value = order_weight
            elif shipping.condition_type == 'price':
                product_value = order_price
            else:
                product_value = None

            if product_value is not None:
                if min_value == '' or min_value == 0:
                    if product_value <= max_value:
                        shipping_amount = amount
                    else:
                        shipping_amount = None

                elif max_value == 0:
                    if product_value >= min_value:
                        shipping_amount = amount
                    else:
                        shipping_amount = None

                elif min_value <= product_value <= max_value:
                    shipping_amount = amount

                else:
                    shipping_amount = None

                if shipping_amount is not None:
                    shipping_rule.append({'name': rule.title, 'shipping_amount': shipping_amount})
    return shipping_rule
