
from order.BusinessLogic.OrderHistory import create_orderhistory
from order.models import LineItems, ShippingAddress, BillingAddress, ChildOrder, ChildOrderLineItems
from rest_framework import exceptions


def split_order(order, line_items):
    paid_amount = order.paid_amount
    vendors = list()
    for line_item in line_items:
        if line_item.vendor not in vendors:
            vendors.append(line_item.vendor)

    for count, vendor in enumerate(vendors, start=1):
        data = {
            'subtotal': 0,
            'shipping': 0,
            'total': 0,
            'actual_total': 0
        }

        parent_line_items = LineItems.objects.filter(vendor=vendor, order=order)
        for parent_line_item in parent_line_items:
            data['subtotal'] += int(parent_line_item.total_price)
            data['actual_total'] += ((int(parent_line_item.quantity) * int(parent_line_item.price)) + parent_line_item.shipping_amount)
            data['shipping'] += parent_line_item.shipping_amount

        data['total'] = data['subtotal'] + data['shipping']

        shipping_address = ShippingAddress.objects.filter(order=order).first()
        if not shipping_address:
            shipping_address = None

        billing_address = BillingAddress.objects.filter(order=order).first()
        if not billing_address:
            billing_address = None

        if float(data['total']) <= float(paid_amount):
            childorder_paid_amount = float(data['total'])
            paid_amount = float(paid_amount) - float(data['total'])
        else:
            childorder_paid_amount = float(paid_amount)
            paid_amount = 0

        child_order_data = {
            'name': str(order.name) + '-' + str(count),
            'payment_method': order.payment_method,
            'subtotal_price': data['subtotal'],
            'tax_applied': order.tax_applied,
            'total_shipping': data['shipping'],
            'total_price': data['total'],
            'paid_amount': childorder_paid_amount,
            'fulfillment_status': order.fulfillment_status,
            'order_status': order.order_status,
        }

        child_order = ChildOrder.objects.create(order=order, shipping_address=shipping_address,
                                                billing_address=billing_address,
                                                vendor=vendor, **child_order_data)

        # create childorder log
        create_orderhistory(childorder=child_order,
                            message=f"order of {child_order.total_price} amount placed through {order.payment_method} payment method")

        if float(childorder_paid_amount) != 0:
            create_orderhistory(childorder=child_order, message=f"Customer paid {childorder_paid_amount} amount from wallet")

        payment_status = 'Unpaid'
        if order.payment_method is not None:
            payment_method = order.payment_method.split(',')
            if len(payment_method) == 1:
                if payment_method[0] == 'wallet':
                    if float(child_order.total_price) == float(child_order.paid_amount):
                        payment_status = 'Paid'
                        create_orderhistory(childorder=child_order,
                                            message=f"Customer paid {childorder_paid_amount} amount from wallet")
                elif payment_method[0] == 'COD (Cash on Delivery)':
                    payment_status = 'Unpaid'
                else:
                    payment_status = 'Paid'
                    create_orderhistory(childorder=child_order,
                                        message=f"Customer paid {childorder_paid_amount} amount from credit/debit card")
            elif len(payment_method) == 2:
                if 'wallet' in payment_method and 'COD (Cash on Delivery)' not in payment_method:
                    payment_status = 'Paid'
                    create_orderhistory(childorder=child_order,
                                        message=f"Customer paid {childorder_paid_amount} amount from credit/debit card and wallet")
                elif 'wallet' in payment_method and 'COD (Cash on Delivery)' in payment_method:
                    if float(child_order.total_price) == float(child_order.paid_amount):
                        payment_status = 'Paid'
                    elif float(child_order.total_price) > float(child_order.paid_amount):
                        payment_status = 'Partially Paid'

                    create_orderhistory(childorder=child_order,
                                        message=f"Customer paid {childorder_paid_amount} amount from wallet")
            else:
                payment_status = 'Unpaid'

        child_order.payment_status = payment_status
        child_order.save()

        for parent_line_item in parent_line_items:
            child_lineItems = {
                'variant': parent_line_item.variant,
                'variant_title': parent_line_item.variant_title,
                'product_title': parent_line_item.product_title,
                'product_image': parent_line_item.product_image,
                'child_order': child_order,
                'quantity': parent_line_item.quantity,
                'price': parent_line_item.price,
                'compare_at_price': parent_line_item.compare_at_price,
                'total_price': parent_line_item.total_price,
                'shipping_name': parent_line_item.shipping_name,
                'shipping_amount': parent_line_item.shipping_amount,
                'shipping': parent_line_item.shipping,
                'vendor_commission': parent_line_item.vendor_commission
            }

            ChildOrderLineItems.objects.create(**child_lineItems)

        # discounted amount
        discounted_price = float(data['actual_total']) - float(data['total'])
        child_order.discounted_price = discounted_price
        child_order.save()

    return True
