
from authentication.BusinessLogic.MessageService import MessageServiceProvider
from order.BusinessLogic.OrderHistory import create_orderhistory
from order.models import LineItems, ShippingAddress, BillingAddress, Order, ChildOrder, ChildOrderLineItems
from products.BusinessLogic.HideOutOfStock import hide_stock
from products.models import Variant, Product, Media
from crm.models import Customer, Wallet, WalletHistory
from rest_framework import serializers
from django.db import transaction
from order.Serializers.CheckoutSerializers import ShippingAddressSerializer, BillingAddressSerializer


class ChildOrderLineItemsSerializer(serializers.ModelSerializer):
    available_quantity = serializers.SerializerMethodField('get_quantity')
    subtotal = serializers.CharField(source='total_price')
    variant_id = serializers.CharField(source='variant.id')

    class Meta:
        model = ChildOrderLineItems
        fields = ('id', 'product_title', 'variant_title', 'variant_id', 'product_image', 'price', 'quantity', 'subtotal', 'shipping_name', 'shipping_amount', 'available_quantity', 'deleted')

    def get_quantity(self, obj):
        variant = Variant.objects.get(id=obj.variant_id)
        quantity = int(variant.inventory_quantity)
        return quantity


class ChildOrderDetailSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField('get_customer')
    line_items = serializers.SerializerMethodField('get_line_items')
    shipping_address = serializers.SerializerMethodField('get_shipping_address')
    billing_address = serializers.SerializerMethodField('get_billing_address')

    class Meta:
        model = ChildOrder
        exclude = ['created_at', 'updated_at']

    def get_shipping_address(self, obj):
        serializer_context = {'request': self.context.get('request')}
        shipping_address_data = ShippingAddress.objects.filter(childOrders_shippingAddress=obj, deleted=False).first()
        if shipping_address_data:
            serializer = ShippingAddressSerializer(shipping_address_data, context=serializer_context)
            return serializer.data
        data = {}
        return data

    def get_billing_address(self, obj):
        serializer_context = {'request': self.context.get('request')}
        billing_address_data = BillingAddress.objects.filter(childOrders_billingAddress=obj, deleted=False).first()
        if billing_address_data:
            serializer = BillingAddressSerializer(billing_address_data, context=serializer_context)
            return serializer.data
        data = {}
        return data

    def get_customer(self, obj):
        order = Order.objects.filter(childOrders_order=obj).first()
        customer = Customer.objects.filter(order_customer=order, deleted=False).first()
        if not customer:
            return None
        name = f"{customer.first_name} {customer.last_name}"
        data = {
            "id": customer.id,
            "name":  name,
            "email": customer.email,
            "phone": customer.phone,
        }
        return data

    def get_line_items(self, obj):
        serializer_context = {'request': self.context.get('request')}
        items_data = ChildOrderLineItems.objects.filter(child_order=obj)
        serializer = ChildOrderLineItemsSerializer(items_data, many=True, context=serializer_context)
        return serializer.data


class ChildOrderAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChildOrder
        exclude = ['id', 'order', 'vendor', 'shipping_address', 'billing_address']

    @transaction.atomic
    def create(self, validated_data):
        validated_data = self.initial_data
        order_id = validated_data.pop('order')
        vendor = validated_data.pop('vendor')
        line_items = validated_data.pop('line_items')
        payment_method = validated_data.pop('payment_method')
        payment_status = validated_data.pop('payment_status')

        order = Order.objects.get(id=order_id)
        child_orders = ChildOrder.objects.filter(order=order).count()

        shipping_address = ShippingAddress.objects.filter(order=order).first()
        if not shipping_address:
            shipping_address = None

        billing_address = BillingAddress.objects.filter(order=order).first()
        if not billing_address:
            billing_address = None

        child_order_data = {
            'name': str(order.name) + '-' + str(child_orders + 1),
            'payment_method': payment_method,
            'fulfillment_status': 'Unfulfilled',
            'payment_status': payment_status,
            'order_status': order.order_status,
            'total_shipping': 0,
            'subtotal_price': 0,
            'total_price': 0
        }

        child_order = ChildOrder.objects.create(order=order, shipping_address=shipping_address,
                                                billing_address=billing_address,
                                                vendor_id=vendor, **child_order_data)

        # shipping_amount = 0
        for line_item in line_items:
            variant = Variant.objects.filter(id=line_item['variant_id'], deleted=False).first()
            product = Product.objects.filter(product_variant=variant, deleted=False, is_active=True).first()
            media = Media.objects.filter(product=product).first()
            if media:
                cdn_link = media.cdn_link
            else:
                cdn_link = None

            total_price = float(variant.price) * int(line_item['quantity'])
            child_lineitems = {
                'variant': variant,
                'variant_title': variant.title,
                'product_title': product.title,
                'product_image': cdn_link,
                'child_order': child_order,
                'quantity': line_item['quantity'],
                'price': variant.price,
                'compare_at_price': variant.compare_at_price,
                'total_price': total_price,
                'shipping_amount': line_item['shipping_amount'],
            }

            child_line_item = ChildOrderLineItems.objects.create(**child_lineitems)

            child_lineitems.pop('child_order')
            LineItems.objects.create(vendor_id=vendor, order=order, **child_lineitems)

            child_order.subtotal_price += child_line_item.total_price
            child_order.total_shipping = child_order.total_shipping + child_line_item.shipping_amount
            child_order.total_price = child_order.subtotal_price + child_order.total_shipping
            child_order.save()

            order.subtotal_price = float(order.subtotal_price) + float(child_line_item.total_price)
            order.total_shipping = float(order.total_shipping) + float(child_line_item.shipping_amount)
            order.total_price = float(order.subtotal_price) + float(order.total_shipping)
            order.save()

        return validated_data


class ChildOrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChildOrder
        exclude = ['id', 'order', 'vendor', 'shipping_address', 'billing_address']

    def update(self, instance, validated_data):
        validated_data = self.initial_data
        line_items = validated_data.pop('line_items', None)
        fulfillment_status = validated_data.pop('fulfillment_status', None)
        payment_status = validated_data.pop('payment_status', None)

        child_order = ChildOrder.objects.get(id=validated_data['id'])
        order = Order.objects.filter(childOrders_order=instance).first()
        child_orders = ChildOrder.objects.filter(order=order)

        if fulfillment_status is not None:
            child_order.fulfillment_status = fulfillment_status
            child_order.save()
            create_orderhistory(childorder=child_order, message=f"order fulfilment status changed as {fulfillment_status}")

        if payment_status is not None:
            child_order.payment_status = payment_status
            child_order.save()
            create_orderhistory(childorder=child_order,
                                message=f"order payment status changed as {payment_status}")

            if payment_status == 'Paid':
                child_order.paid_amount = child_order.total_price
                child_order.save()

                order.paid_amount += child_order.total_price
                order.save()

        if line_items:
            for line_item in line_items:
                vendor = child_order.vendor.id
                variant = Variant.objects.filter(id=line_item['variant_id']).first()

                if 'id' in line_item:
                    item = LineItems.objects.filter(order=order, vendor_id=vendor, variant__id=line_item['variant_id']).first()

                    order.subtotal_price = float(order.subtotal_price) - float(item.total_price)
                    order.total_shipping = float(order.total_shipping) - float(item.shipping_amount)
                    order.total_price = float(order.total_price) - float(item.total_price) - float(item.shipping_amount)
                    order.save()

                    child_order.subtotal_price = float(child_order.subtotal_price) - float(item.total_price)
                    child_order.total_shipping = float(child_order.total_shipping) - float(item.shipping_amount)
                    child_order.total_price = float(child_order.total_price) - float(item.total_price) - float(item.shipping_amount)
                    child_order.save()

                    old_quantity = int(item.quantity)
                    new_quantity = int(line_item['quantity'])
                    item.total_price = float(item.price) * new_quantity
                    item.quantity = new_quantity
                    item.shipping_amount = line_item['shipping_amount']
                    item.save()

                    order.subtotal_price = float(order.subtotal_price) + float(item.total_price)
                    order.total_shipping = float(order.total_shipping) + float(item.shipping_amount)
                    order.total_price = float(order.total_price) + float(item.total_price) + float(item.shipping_amount)
                    order.save()

                    child_order_lineitem = ChildOrderLineItems.objects.filter(id=line_item['id']).first()

                    child_order_lineitem.total_price = item.total_price
                    child_order_lineitem.quantity = line_item['quantity']
                    child_order_lineitem.shipping_amount = line_item['shipping_amount']
                    child_order_lineitem.save()

                    child_order.subtotal_price = float(child_order.subtotal_price) + float(item.total_price)
                    child_order.total_shipping = float(child_order.total_shipping) + float(item.shipping_amount)
                    child_order.total_price = float(child_order.total_price) + float(item.total_price) + + float(item.shipping_amount)
                    child_order.save()

                    variant.old_inventory_quantity = variant.inventory_quantity
                    if new_quantity > old_quantity:
                        variant.inventory_quantity = int(variant.inventory_quantity) - (new_quantity - old_quantity)
                        variant.save()
                    elif new_quantity < old_quantity:
                        variant.inventory_quantity = int(variant.inventory_quantity) + (old_quantity - new_quantity)
                        variant.save()

                    # create_orderhistory(childorder=child_order, message=f"{child_order_lineitem.product_title} quantity set {child_order_lineitem.quantity}")
                else:
                    product = Product.objects.filter(product_variant=variant).first()
                    media = Media.objects.filter(product=product, position=1).first()
                    if media:
                        cdn_link = media.cdn_link
                    else:
                        cdn_link = ''

                    subtotal = float(variant.price) * int(line_item['quantity'])

                    line_item['order'] = order
                    line_item['price'] = variant.price
                    line_item['compare_at_price'] = variant.compare_at_price
                    line_item['total_price'] = subtotal
                    line_item['shipping_amount'] = ['shipping_amount']
                    line_item['product_title'] = product.title
                    line_item['variant_title'] = variant.title
                    line_item['product_image'] = cdn_link

                    item = LineItems.objects.create(vendor_id=vendor, **line_item)

                    variant.old_inventory_quantity = variant.inventory_quantity
                    variant.inventory_quantity = int(variant.inventory_quantity) - int(item.quantity)
                    variant.save()

                    order.subtotal_price = float(order.subtotal_price) + float(item.total_price)
                    order.total_shipping = float(order.total_shipping) + float(item.shipping_amount)
                    order.total_price = float(order.subtotal_price) + float(order.total_shipping)
                    order.save()

                    child_lineitems = {
                        'variant': item.variant,
                        'variant_title': item.variant_title,
                        'product_title': item.product_title,
                        'product_image': item.product_image,
                        'child_order_id': validated_data['id'],
                        'quantity': item.quantity,
                        'price': item.price,
                        'compare_at_price': item.compare_at_price,
                        'total_price': item.total_price,
                        'shipping_amount': item.shipping_amount
                    }

                    childlineitem = ChildOrderLineItems.objects.create(**child_lineitems)

                    child_order.subtotal_price = float(child_order.subtotal_price) + float(item.total_price)
                    child_order.total_shipping = float(child_order.total_shipping) + float(item.shipping_amount)
                    child_order.total_price = float(child_order.subtotal_price) + float(item.shipping_amount)
                    child_order.save()

                    # hide out of stock
                    hide_stock(product)

                    create_orderhistory(childorder=child_order, message=f"{childlineitem.product_title} added in order")

        check_fulfillment_status = [child_order.fulfillment_status for child_order in child_orders if child_orders]
        if len(check_fulfillment_status) == check_fulfillment_status.count('Unfulfilled'):
            order.fulfillment_status = 'Unfulfilled'
            order.save()
            create_orderhistory(order=order, message=f"order fulfilment status changed as Unfulfilled")
        elif 'Unfulfilled' in check_fulfillment_status:
            order.fulfillment_status = 'Partially Fulfilled'
            order.save()
            create_orderhistory(order=order, message=f"order fulfilment status changed as Partially Fulfilled")
        else:
            order.fulfillment_status = 'Fulfilled'
            order.save()
            create_orderhistory(order=order, message=f"order fulfilment status changed as Fulfilled")

        check_payment_status = [child_order.payment_status for child_order in child_orders if child_orders]
        if len(check_payment_status) == check_payment_status.count('Pending'):
            order.payment_status = 'Pending'
            order.save()
            create_orderhistory(order=order, message=f"order payment status changed as Pending")
        elif 'Pending' in check_payment_status:
            order.payment_status = 'Partially Paid'
            order.save()
            create_orderhistory(order=order, message=f"order payment status changed as Partially Paid")
        else:
            order.payment_status = 'Paid'
            order.save()
            create_orderhistory(order=order, message=f"order payment status changed as Paid")

        return instance


class ChildOrderStatusChangeSerializer(serializers.ModelSerializer):
    id = serializers.CharField()

    class Meta:
        model = ChildOrder
        fields = ('id', 'order_status')

    def update(self, instance, validated_data):
        validated_data = self.initial_data
        order_status = validated_data.pop('order_status', None)
        refund_status = validated_data.pop('refund_status', None)
        refund_message = ""

        if order_status is not None:
            if str(order_status).lower() == 'cancelled':
                ChildOrder.objects.filter(id=instance.id).update(order_status='Cancelled')
                child_order = ChildOrder.objects.filter(id=instance.id).first()
                create_orderhistory(childorder=child_order, message=f"order has been {order_status}")

                # check parent order
                order = Order.objects.filter(childOrders_order=child_order).first()
                child_orders = ChildOrder.objects.filter(order=order)
                check_order_status = [child_order.order_status for child_order in child_orders if child_orders]
                if len(check_order_status) == check_order_status.count('Cancelled'):
                    order.payment_status = 'Cancelled'
                    order.save()
                    create_orderhistory(order=order, message=f"order status changed as Cancelled due to Cancelled all child orders")

                line_items = ChildOrderLineItems.objects.filter(child_order=child_order)
                for line_item in line_items:
                    variant = Variant.objects.filter(id=line_item.variant.id).first()
                    variant.inventory_quantity += int(line_item.quantity)
                    variant.save()

                    product = Product.objects.filter(product_variant=variant).first()
                    hide_stock(product, order_cancel=True)

                # Refund
                if child_order.payment_status == 'Paid' or child_order.payment_status == 'Partially Paid':
                    if refund_status == 'wallet':
                        wallet = Wallet.objects.filter(customer=child_order.order.customer, is_active=True).first()
                        wallet.value += child_order.paid_amount
                        wallet.save()

                        child_order.refund_type = 'Wallet'
                        child_order.save()

                        refund_message = "& your amount is refunded in your store wallet"
                        # entry in wallet history
                        WalletHistory.objects.create(wallet=wallet,
                                                     type=f'Refund on order {child_order.name}', action='Credited',
                                                     value=child_order.paid_amount)

                        create_orderhistory(childorder=child_order, message=f"{child_order.paid_amount} has been refunded to customer in wallet")

                    elif refund_status == 'bank':
                        child_order.refund_type = 'Bank'
                        child_order.save()
                        create_orderhistory(childorder=child_order,
                                            message=f"{child_order.paid_amount} has been refunded to customer in bank")
                        refund_message = "& your amount is refunded in your bank"

                # order sms
                shipping_address = ShippingAddress.objects.filter(order=order).first()
                if shipping_address.phone is not None:
                    try:
                        message = f"Your Order of {child_order.total_price} amount has been cancelled {refund_message}"
                        MessageServiceProvider.send_message(self, phone=shipping_address.phone, message=message)
                    except Exception as e:
                        print(e)

        return instance
