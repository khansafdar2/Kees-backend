

from order.models import LineItems, ShippingAddress, BillingAddress, Order
from products.models import Variant, Product, Media
from products.BusinessLogic.HideOutOfStock import hide_stock
from setting.models import Tax
import random
from order.BusinessLogic.SplitOrders import split_order


def ConvertOpenOrder(validated_data, customer, shipping_address, billing_address, line_items, store):
    payment_status = validated_data.pop('payment_status', None)
    if payment_status is None:
        payment_status = 'Unpaid'

    tax = Tax.objects.filter(deleted=False).first()
    if tax is not None:
        tax_percentage = tax.tax_percentage
    else:
        tax_percentage = 0

    prefix = store.main_order_prefix

    order_data = {
        'name': '#' + prefix + str(store.order_counter),
        'payment_method': validated_data['payment_method'],
        'payment_status': payment_status,
        'order_status': "Open",
        'fulfillment_status': 'Unfulfilled',
        'notes': validated_data['notes'],
        'tags': validated_data['tags']
    }

    # Order Create
    order = Order.objects.create(customer=customer, **order_data)

    # create order_id for track
    order_id = str(order.id) + str(random.randint(10000000, 99999999))
    order.order_id = order_id
    order.save()

    # Order Counter Increase
    store.order_counter = store.order_counter + 1
    store.save()

    # Create Shipping Address
    if shipping_address is not None:
        ShippingAddress.objects.create(order=order, **shipping_address)

    if billing_address is not None:
        BillingAddress.objects.create(order=order, **billing_address)

    # Create Line Items
    order_amount = {'shipping_amount': 0, 'subtotal': 0, 'total': 0}
    for line_item in line_items:
        vendor = line_item.pop('vendor')
        variant = Variant.objects.filter(id=line_item['variant_id']).first()
        product = Product.objects.filter(product_variant=variant).first()
        media = Media.objects.filter(product=product, position=1).first()
        if media:
            media_link = media.cdn_link
        else:
            media_link = None

        # if shipping is None:
        #     shipping_amount = 0
        # else:
        #     shipping_amount = int(shipping.amount)

        subtotal = int(variant.price) * int(line_item['quantity'])
        line_item['order'] = order
        line_item['price'] = variant.price
        line_item['compare_at_price'] = variant.compare_at_price
        line_item['total_price'] = subtotal
        line_item['shipping_amount'] = line_item['shipping_amount']
        line_item['product_title'] = product.title
        line_item['variant_title'] = variant.title
        line_item['product_image'] = media_link

        item = LineItems.objects.create(vendor_id=vendor, **line_item)

        variant.old_inventory_quantity = variant.inventory_quantity
        variant.inventory_quantity = int(variant.inventory_quantity) - int(item.quantity)
        variant.save()

        # hide out of stock
        product = Product.objects.filter(product_variant=variant).first()
        hide_stock(product)

        # order_amount['shipping_amount'] += shipping_amount
        order_amount['subtotal'] += subtotal
    order_amount['total'] = order_amount['shipping_amount'] + order_amount['subtotal']

    order.subtotal_price = order_amount['subtotal']
    order.total_shipping = order_amount['shipping_amount']
    order.total_price = order_amount['total']
    order.tax_applied = ((order_amount['subtotal'] + order_amount['shipping_amount']) / 100) * tax_percentage

    order.save()

    line_items = LineItems.objects.filter(order=order)
    split_order(order, line_items)

    return order
