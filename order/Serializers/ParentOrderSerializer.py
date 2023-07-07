
import requests

from authentication.BusinessLogic.MessageService import MessageServiceProvider
from ecomm_app.settings.local import LOYALTY_MICROSERVICE_URL
from order.BusinessLogic.OrderHistory import create_orderhistory
from order.models import LineItems, ShippingAddress, BillingAddress, Order, ChildOrder, ChildOrderLineItems, OrderHistory
from products.models import Variant, Media, Product
from order.BusinessLogic.OrderEmail import orderemail
from crm.models import Customer, WalletHistory
from rest_framework import serializers
from rest_framework import exceptions
from django.db import transaction
from crm.models import Wallet
from products.BusinessLogic.HideOutOfStock import hide_stock
from order.Serializers.CheckoutSerializers import ShippingAddressSerializer, BillingAddressSerializer
from setting.BusinessLogic.LoyaltyCalculation import calculate_points
from setting.models import StoreInformation


class ParentOrderListSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField('get_customer')

    class Meta:
        model = Order
        fields = (
        'id', 'name', 'order_id', 'created_at', 'customer_name', 'total_price', 'payment_status', 'fulfillment_status',
        'order_status')

    def get_customer(self, obj):
        customer = Customer.objects.filter(order_customer=obj, deleted=False).first()
        if not customer:
            return None
        name = f"{customer.first_name} {customer.last_name}"
        return name


class LineItemsSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='variant.product.title', read_only=True, allow_null=True,
                                          allow_blank=True)
    vendor = serializers.CharField(source='vendor.name', read_only=True, allow_null=True, allow_blank=True)
    variant_title = serializers.CharField(source='variant.title', read_only=True, allow_null=True, allow_blank=True)
    subtotal = serializers.SerializerMethodField('get_price')

    class Meta:
        model = LineItems
        fields = (
        'id', 'product_title', 'vendor', 'variant_title', 'product_image', 'price', 'quantity', 'subtotal', 'shipping_name', 'shipping_amount',
        'total_price', 'deleted')

    def get_price(self, obj):
        # variant = Variant.objects.get(id=obj.variant_id)
        # price = int(variant.price) * int(obj.quantity)
        price = obj.price * obj.quantity
        return price


class ChildOrderSerializer(serializers.ModelSerializer):
    vendor = serializers.CharField(source='vendor.name', read_only=True, allow_null=True, allow_blank=True)

    class Meta:
        model = ChildOrder
        fields = ('id', 'name', 'vendor', 'total_price', 'payment_status', 'fulfillment_status', 'order_status')


class ParentOrderDetailSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField('get_customer')
    line_items = serializers.SerializerMethodField('get_line_items')
    child_orders = serializers.SerializerMethodField('get_childorder')
    shipping_address = serializers.SerializerMethodField('get_shipping_address')
    billing_address = serializers.SerializerMethodField('get_billing_address')

    class Meta:
        model = Order
        exclude = ['created_at', 'updated_at']

    def get_childorder(self, obj):
        serializer_context = {'request': self.context.get('request')}
        child_orders = ChildOrder.objects.filter(order=obj)
        if child_orders:
            serializer = ChildOrderSerializer(child_orders, many=True, context=serializer_context)
            return serializer.data
        data = []
        return data

    def get_shipping_address(self, obj):
        serializer_context = {'request': self.context.get('request')}
        shipping_address_data = ShippingAddress.objects.filter(order=obj, deleted=False).first()
        if shipping_address_data:
            serializer = ShippingAddressSerializer(shipping_address_data, context=serializer_context)
            return serializer.data
        data = {}
        return data

    def get_billing_address(self, obj):
        serializer_context = {'request': self.context.get('request')}
        billing_address_data = BillingAddress.objects.filter(order=obj, deleted=False).first()
        if billing_address_data:
            serializer = BillingAddressSerializer(billing_address_data, context=serializer_context)
            return serializer.data
        data = {}
        return data

    def get_line_items(self, obj):
        serializer_context = {'request': self.context.get('request')}
        items_data = LineItems.objects.filter(order=obj)
        serializer = LineItemsSerializer(items_data, many=True, context=serializer_context)
        return serializer.data

    def get_customer(self, obj):
        customer = Customer.objects.filter(order_customer=obj, deleted=False).first()
        if not customer:
            return None
        name = f"{customer.first_name} {customer.last_name}"
        data = {
            "id": customer.id,
            "name": name,
            "email": customer.email,
            "phone": customer.phone,
        }
        return data


class ParentOrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

    @transaction.atomic
    def update(self, instance, validated_data):
        validated_data = self.initial_data
        fulfilment_status = validated_data.pop('fulfillment_status', None)
        payment_status = validated_data.pop('payment_status', None)
        order_status = validated_data.pop('order_status', None)
        shipping_address = validated_data.pop('shipping_address', None)
        billing_address = validated_data.pop('billing_address', None)
        notes = validated_data.pop('notes', None)
        tags = validated_data.pop('tags', None)

        order = Order.objects.filter(id=instance.id).first()
        order.notes = notes
        order.tags = tags
        order.save()

        if payment_status is not None:
            order.payment_status = payment_status
            order.save()

        if fulfilment_status is not None:
            order.fulfillment_status = fulfilment_status
            order.save()

        shipping_address_object = None
        if shipping_address is not None:
            shipping_address_object = ShippingAddress.objects.filter(order_id=instance.id).first()
            if shipping_address_object:
                ShippingAddress.objects.filter(order_id=instance.id).update(**shipping_address)
            else:
                shipping_address['order_id'] = instance.id
                shipping_address_object = ShippingAddress.objects.create(**shipping_address)

        if billing_address is not None:
            billing_address_object = BillingAddress.objects.filter(order_id=instance.id).first()
            if billing_address_object:
                BillingAddress.objects.filter(order_id=instance.id).update(**billing_address)
            else:
                billing_address['order_id'] = instance.id
                BillingAddress.objects.create(**billing_address)

        child_orders = ChildOrder.objects.filter(order_id=instance.id)
        if fulfilment_status is not None:
            create_orderhistory(order=order, message=f"order fulfilment status changed as {fulfilment_status}")
            if fulfilment_status != 'Partially Fulfilled':
                for child_order in child_orders:
                    child_order.fulfillment_status = fulfilment_status
                    child_order.save()
                    create_orderhistory(childorder=child_order, message=f"order fulfilment status changed as {fulfilment_status}")

        if payment_status is not None:
            create_orderhistory(order=order, message=f"order payment status changed as {payment_status}")
            if payment_status != 'Partially Paid':
                for child_order in child_orders:
                    child_order.payment_status = payment_status
                    child_order.save()
                    create_orderhistory(childorder=child_order,
                                        message=f"order payment status changed as {payment_status}")

                    if payment_status == 'Paid':
                        child_order.paid_amount = child_order.total_price
                        child_order.save()

        if order_status is not None:
            order.order_status = order_status
            order.save()

            if order_status.lower() == 'delivered':
                create_orderhistory(order=order, message=f"order has been {order_status}")
                orderemail(
                    order=order,
                    email_heading="Your order has been delivered",
                    email_subject=f"A shipment from order {order.order_id} has been delivered",
                    description="Your order has been delivered. If you have not received your package yet please contact us."
                )

                # order sms
                if shipping_address_object:
                    if shipping_address_object.phone is not None:
                        try:
                            message = f"Your Order {order.order_id} of {order.total_price} has been delivered"
                            MessageServiceProvider.send_message(self, phone=shipping_address_object.phone, message=message)
                        except Exception as e:
                            print(e)

            if order_status.lower() == 'shipped':
                create_orderhistory(order=order, message=f"order has been {order_status}")
                orderemail(
                    order=order,
                    email_heading="Your order is on the way",
                    email_subject=f"A shipment from order {order.order_id} is on the way",
                    description="Your order is on the way and will take 1-2 working days."
                )

                # order sms
                if shipping_address_object:
                    if shipping_address_object.phone is not None:
                        try:
                            message = f"Your Order {order.order_id} of {order.total_price} has been shipped"
                            MessageServiceProvider.send_message(self, phone=shipping_address_object.phone, message=message)
                        except Exception as e:
                            print(e)

        if order.payment_status == 'Paid':
            order.paid_amount = order.total_price
            order.save()

            # loyalty payload for points calculation
            store = StoreInformation.objects.filter(deleted=False).first()
            customer_id = order.customer_id
            total_no_of_order = Order.objects.filter(customer_id=customer_id).count()
            orders = Order.objects.filter(customer_id=customer_id)
            total_orders_sum = 0
            for order_object in orders:
                total_orders_sum += order_object.total_price

            calculate_points(customer_id, total_no_of_order, total_orders_sum, order.total_price, order.payment_status)

        return instance


class OrderStatusChangeSerializer(serializers.ModelSerializer):
    id = serializers.CharField()

    class Meta:
        model = Order
        fields = ('id', 'order_status')

    def update(self, instance, validated_data):
        validated_data = self.initial_data
        order_status = validated_data.pop('order_status', None)
        refund_status = validated_data.pop('refund_status', None)
        email_heading = "Your order has been cancelled"
        refund_message = ""

        if order_status is not None:
            if str(order_status).lower() == 'cancelled':
                Order.objects.filter(id=instance.id).update(order_status='Cancelled')
                child_orders = ChildOrder.objects.filter(order_id=instance.id, order_status='Open')
                if child_orders:
                    for child_order in child_orders:
                        child_order.order_status = 'Cancelled'
                        child_order.save()
                        create_orderhistory(childorder=child_order, message=f"order has been {order_status}")

                        line_items = ChildOrderLineItems.objects.filter(child_order=child_order)
                        for line_item in line_items:
                            variant = Variant.objects.filter(id=line_item.variant.id).first()
                            variant.inventory_quantity += int(line_item.quantity)
                            variant.save()

                            product = Product.objects.filter(product_variant=variant).first()
                            hide_stock(product, order_cancel=True)

                order = Order.objects.filter(id=instance.id).first()
                create_orderhistory(order=order, message=f"order has been {order_status}")

                # Refund
                if refund_status == 'wallet':
                    wallet = Wallet.objects.filter(customer=order.customer, is_active=True).first()
                    wallet.value += order.paid_amount
                    wallet.save()

                    order.refund_type = 'Wallet'
                    order.save()

                    email_heading = "Your order has been cancelled & Your amount is refunded in your wallet, if you didn't signup then please do signup on our store with same email and find your amount in your wallet",
                    refund_message = "& your amount is refunded in your wallet"
                    # entry in wallet history
                    WalletHistory.objects.create(wallet=wallet,
                                                 type=f'Refund on order {order.name}', action='Credited',
                                                 value=order.paid_amount)

                    create_orderhistory(order=order, message=f"{order.paid_amount} has been refunded to customer in wallet")
                    for child_order in child_orders:
                        if child_order.paid_amount > 0:
                            child_order.refund_type = 'Wallet'
                            child_order.save()
                            create_orderhistory(childorder=child_order,
                                                message=f"{child_order.paid_amount} has been refunded to customer in wallet")

                elif refund_status == 'bank':
                    order.refund_type = 'Bank'
                    order.save()
                    create_orderhistory(order=order, message=f"{order.paid_amount} has been refunded to customer in bank")

                    email_heading = "Your order has been cancelled & Your amount is refunded in your bank account."
                    refund_message = "& your amount is refunded in your bank"

                    for child_order in child_orders:
                        if child_order.paid_amount > 0:
                            child_order.refund_type = 'Bank'
                            child_order.save()
                            create_orderhistory(childorder=child_order,
                                                message=f"{child_order.paid_amount} has been refunded to customer in bank")

                orderemail(
                    order=order,
                    email_heading=email_heading,
                    email_subject=f"Your order {order.order_id} cancelled",
                    description="Your order has been cancelled. The items listed below were part of the cancelled order."
                )

                # order sms
                shipping_address = ShippingAddress.objects.filter(order=order).first()
                if shipping_address.phone is not None:
                    try:
                        message = f"Your Order {order.order_id} of {order.total_price} has been cancelled {refund_message}"
                        MessageServiceProvider.send_message(self, phone=shipping_address.phone, message=message)
                    except Exception as e:
                        print(e)

        return instance


class OrderHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderHistory
        fields = '__all__'

    def create(self, validated_data):
        validated_data = self.initial_data
        order_id = validated_data.pop('order_id', None)
        childorder_id = validated_data.pop('childorder_id', None)

        order_history = OrderHistory.objects.create(order_id=order_id, child_order_id=childorder_id, **validated_data)

        return order_history
