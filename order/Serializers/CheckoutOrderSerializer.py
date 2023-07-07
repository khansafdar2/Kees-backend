
import requests

from authentication.BusinessLogic.MessageService import MessageServiceProvider
from ecomm_app.settings.local import LOYALTY_MICROSERVICE_URL
from order.BusinessLogic.OrderHistory import create_orderhistory
from order.models import Checkout, LineItems, ShippingAddress, BillingAddress, Order
from products.models import Variant
from order.BusinessLogic.OrderEmail import orderemail
from crm.models import Customer, Address, Wallet, WalletHistory
from setting.BusinessLogic.LoyaltyCalculation import calculate_points
from setting.models import StoreInformation, Tax
from rest_framework import serializers
from django.db import transaction
from rest_framework import exceptions
import random
from products.models import Product
from products.BusinessLogic.HideOutOfStock import hide_stock
from order.BusinessLogic.SplitOrders import split_order
from order.Serializers.CheckoutSerializers import ShippingAddressSerializer, BillingAddressSerializer
from vendor.models import Vendor


class OrdersListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        exclude = ('customer',)


class LineItemsSerializer(serializers.ModelSerializer):
    product_handle = serializers.CharField(source='variant.product.handle', read_only=True, allow_null=True, allow_blank=True)
    sku = serializers.CharField(source='variant.sku', read_only=True, allow_null=True,allow_blank=True)

    class Meta:
        model = LineItems
        exclude = ['checkout', 'order', 'vendor', 'draft_order', 'deleted_at', 'created_at', 'updated_at', 'variant']


class CheckoutOrderAddSerializer(serializers.ModelSerializer):
    customer_email = serializers.CharField(source='customer.email', read_only=True, allow_null=True, allow_blank=True)
    customer_phone = serializers.CharField(source='customer.phone', read_only=True, allow_null=True, allow_blank=True)
    shipping_address = serializers.SerializerMethodField('get_shipping_address')
    billing_address = serializers.SerializerMethodField('get_billing_address')

    class Meta:
        model = Order
        exclude = ['id']

    def get_shipping_address(self, obj):
        serializer_context = {'request': self.context.get('request')}
        shipping_address_data = ShippingAddress.objects.filter(order=obj, deleted=False).first()
        serializer = ShippingAddressSerializer(shipping_address_data, context=serializer_context)
        return serializer.data

    def get_billing_address(self, obj):
        serializer_context = {'request': self.context.get('request')}
        billing_address_data = BillingAddress.objects.filter(order=obj, deleted=False).first()
        serializer = BillingAddressSerializer(billing_address_data, context=serializer_context)
        return serializer.data

    @transaction.atomic
    def create(self, validated_data):
        validated_data = self.initial_data
        checkout_id = validated_data['checkout_id']
        checkout = Checkout.objects.filter(checkout_id=checkout_id).first()

        try:
            if checkout:
                if not checkout.is_processing:
                    checkout.is_processing = True
                    checkout.save()

                    store = StoreInformation.objects.filter(deleted=False).first()
                    shipping_address = ShippingAddress.objects.filter(checkout=checkout, deleted=False).first()

                    customer_address = {
                        "first_name": shipping_address.first_name,
                        "last_name": shipping_address.last_name,
                        "phone": shipping_address.phone,
                        "address": shipping_address.address,
                        "apartment": shipping_address.apartment,
                        "city": shipping_address.city,
                        "country": shipping_address.country,
                        "postal_code": shipping_address.postal_code,
                        "primary_address": True
                    }

                    customer_data = dict()
                    customer_data['first_name'] = shipping_address.first_name
                    customer_data['last_name'] = shipping_address.last_name

                    if checkout.email:
                        customer = Customer.objects.filter(email=checkout.email).first()
                        if not customer:
                            customer_data['email'] = checkout.email
                    elif checkout.phone:
                        customer = Customer.objects.filter(phone=checkout.phone).first()
                        if not customer:
                            customer_data['phone'] = checkout.phone
                    else:
                        raise exceptions.ParseError("email or phone is required")

                    if not customer:
                        customer = Customer.objects.create(**customer_data)
                        Address.objects.create(customer=customer, **customer_address)

                    customer_data['customer_id'] = customer.id
                    customer_data['email'] = customer.email
                    customer_data['platform'] = store.store_name
                    # customer_response = requests.post(LOYALTY_MICROSERVICE_URL + '/loyalty/customer', customer_data)

                    tax = Tax.objects.filter(deleted=False).first()
                    if tax is not None:
                        tax_percentage = tax.tax_percentage
                    else:
                        tax_percentage = 0

                    prefix = store.main_order_prefix

                    subtotal = int(checkout.subtotal_price)
                    total_shipping = int(checkout.total_shipping)
                    tax_applied = ((subtotal + total_shipping)/100) * tax_percentage
                    total = subtotal + total_shipping + tax_applied

                    if checkout.payment_method is not None:
                        payment_method = checkout.payment_method.split(',')
                        if len(payment_method) == 1 and (payment_method[0] == 'wallet' or payment_method[0] != 'COD (Cash on Delivery)'):
                            payment_status = 'Paid'
                        elif len(payment_method) == 2:
                            if 'wallet' in payment_method and 'COD (Cash on Delivery)' in payment_method:
                                payment_status = 'Partially Paid'
                            else:
                                payment_status = 'Paid'
                        else:
                            payment_status = 'Unpaid'
                    else:
                        payment_status = 'Unpaid'

                    order_data = {
                        'name': '#' + prefix + str(store.order_counter),
                        'payment_method': checkout.payment_method,
                        'payment_status': payment_status,
                        'subtotal_price': subtotal,
                        'tax_applied': tax_applied,
                        'total_shipping': total_shipping,
                        'total_price': total,
                        'paid_amount': checkout.paid_by_wallet,
                        'order_status': "Open"
                    }

                    # Order Create
                    order = Order.objects.create(customer=customer, **order_data)

                    # place order log
                    create_orderhistory(order=order, message=f"order of {order.total_price} amount placed through {order.payment_method} payment method")

                    # create order_id for track
                    order_id = str(order.id) + str(random.randint(10000000, 99999999))
                    order.order_id = order_id
                    order.save()

                    # wallet deduction
                    if order.payment_method:
                        payment_method = order.payment_method.split(',')
                        if 'wallet' in payment_method:
                            wallet = Wallet.objects.filter(customer=customer, is_active=True, is_deleted=False).first()
                            if wallet:
                                total_amount = float(order.total_price)
                                if total_amount <= wallet.value:
                                    debited_amount = total_amount
                                    wallet.value = float(wallet.value) - total_amount
                                    wallet.save()
                                elif total_amount > wallet.value:
                                    debited_amount = wallet.value
                                    wallet.value = 0
                                    wallet.save()
                                else:
                                    debited_amount = 0

                                WalletHistory.objects.create(wallet=wallet,
                                                             type=f'order {order.order_id}', action='Debited',
                                                             value=debited_amount)

                        if len(payment_method) == 1:
                            if payment_method[0] == 'wallet':
                                create_orderhistory(order=order, message=f"Customer paid {order.paid_amount} amount from wallet")
                            elif payment_method[0] != 'COD (Cash on Delivery)':
                                create_orderhistory(order=order,
                                                    message=f"Customer paid {order.paid_amount} amount from credit/debit card")
                        elif len(payment_method) == 2:
                            if 'wallet' in payment_method and 'COD (Cash on Delivery)' not in payment_method:
                                create_orderhistory(order=order,
                                                    message=f"Customer paid {order.paid_amount} amount")
                            elif 'wallet' in payment_method and 'COD (Cash on Delivery)' in payment_method:
                                create_orderhistory(order=order,
                                                    message=f"Customer paid {order.paid_amount} amount from wallet")
                    # Order Counter Increase
                    store.order_counter = store.order_counter + 1
                    store.save()

                    # Update Shipping Address
                    shipping_address.checkout = None
                    shipping_address.order = order
                    shipping_address.save()

                    # Update Billing Address
                    BillingAddress.objects.filter(checkout=checkout).update(checkout=None, order=order)

                    # Update Line Items
                    actual_total = 0.0
                    line_items = LineItems.objects.filter(checkout=checkout)
                    for line_item in line_items:
                        # calculate actual total amount without discount
                        actual_total += float(line_item.price * line_item.quantity) + float(line_item.shipping_amount)

                        # inventory decrement
                        variant = Variant.objects.filter(id=line_item.variant.id).first()

                        variant.old_inventory_quantity = variant.inventory_quantity
                        variant.inventory_quantity = int(variant.inventory_quantity) - int(line_item.quantity)
                        variant.save()

                        line_item.checkout = None
                        line_item.order = order
                        line_item.save()

                        # commission calculate
                        try:
                            commission = line_item.variant.product.commission
                            if commission:
                                commission_value = commission.value
                                commission_type = commission.type

                                vendor = Vendor.objects.filter(id=line_item.variant.product.vendor.id).first()
                                if commission_type == 'fixed':
                                    vendor.commission_value += commission_value
                                    line_item.vendor_commission = commission_value
                                elif commission_type == 'percentage':
                                    value = line_item.total_price * (commission_value / 100)
                                    vendor.commission_value += value
                                    line_item.vendor_commission = value

                                vendor.save()
                                line_item.save()
                        except Exception as e:
                            print(e)

                        # hide out of stock
                        product = Product.objects.filter(product_variant=variant).first()
                        hide_stock(product)

                    # discounted amount
                    discounted_price = actual_total - total
                    order.discounted_price = discounted_price
                    order.save()

                    # Delete Checkout
                    checkout.delete()
                    split_order(order, line_items)
                    # loyalty payload for points calculation
                    total_no_of_order = Order.objects.filter(customer_id=customer.id).count()
                    orders = Order.objects.filter(customer_id=customer.id)
                    total_orders_sum = 0
                    for order_obejct in orders:
                        total_orders_sum += order_obejct.total_price

                    try:
                        calculate_points(customer.id, total_no_of_order, total_orders_sum, total, order.payment_status)
                    except Exception as e:
                        print(e)

                    # order email
                    if customer.email is not None:
                        orderemail(
                            order=order,
                            bcc_email=store.store_contact_email,
                            email_subject=f"Your order {order.order_id}",
                            email_heading= "Thank you for purchase at KEES",
                            description= "we're getting your order ready to be shipped. We will notify you when it has been sent."
                        )

                    # order sms
                    if shipping_address.phone is not None:
                        try:
                            message = f"Your Order {order.order_id} of {order.total_price} has been received"
                            MessageServiceProvider.send_message(self, phone=shipping_address.phone, message=message)
                        except Exception as e:
                            print(e)

                    return order
            else:
                raise exceptions.ParseError("please create checkout before order")
        except Exception as e:
            print(e)
            raise Exception(str(e))


class CustomerAccountOrderDetailSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='customer.first_name', read_only=True, allow_null=True, allow_blank=True)
    last_name = serializers.CharField(source='customer.last_name', read_only=True, allow_null=True, allow_blank=True)
    line_items = serializers.SerializerMethodField('get_line_items')
    shipping_address = serializers.SerializerMethodField('get_shipping_address')
    billing_address = serializers.SerializerMethodField('get_billing_address')

    class Meta:
        model = Order
        exclude = ['id', 'customer']

    def get_line_items(self, obj):
        serializer_context = {'request': self.context.get('request')}
        line_item_data = LineItems.objects.filter(order=obj)
        serializer = LineItemsSerializer(line_item_data, many=True, context=serializer_context)
        return serializer.data

    def get_shipping_address(self, obj):
        serializer_context = {'request': self.context.get('request')}
        shipping_address_data = ShippingAddress.objects.filter(order=obj, deleted=False).first()
        serializer = ShippingAddressSerializer(shipping_address_data, context=serializer_context)
        return serializer.data

    def get_billing_address(self, obj):
        serializer_context = {'request': self.context.get('request')}
        billing_address_data = BillingAddress.objects.filter(order=obj, deleted=False).first()
        serializer = BillingAddressSerializer(billing_address_data, context=serializer_context)
        return serializer.data
