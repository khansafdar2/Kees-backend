
import json
from datetime import datetime
import pytz
from django.db.models import Q
from crm.models import Customer, Wallet
from discount.BusinessLogic.BuyXGetY import get_x_lineitem, get_y_lineitem
from discount.models import Discount
from order.BusinessLogic.ShippingCalculation import calculate_shipping
from order.models import Checkout, LineItems, ShippingAddress, BillingAddress, Order
from products.models import Variant, Product, ProductGroup, Media, MainCategory, SubCategory, SuperSubCategory
from setting.models import Country, StoreInformation
from shipping.models import ConditionalRate, Shipping, Rule
from vendor.models import Vendor
from rest_framework import serializers, exceptions
import secrets
from django.db import transaction
from django.db.models import Sum
from drf_yasg.utils import swagger_serializer_method
from shipping.models import Zone, City


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        exclude = ['id', 'checkout', 'order', 'draft_order', 'deleted', 'deleted_at', 'created_at', 'updated_at']


class BillingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingAddress
        exclude = ['id', 'checkout', 'order', 'draft_order', 'deleted', 'deleted_at', 'created_at', 'updated_at']


class LineItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineItems
        exclude = ['checkout', 'order', 'vendor',  'deleted', 'deleted_at', 'created_at', 'updated_at']


class CheckoutDetailSerializer(serializers.ModelSerializer):
    shipping_address = serializers.SerializerMethodField('get_shipping_address')
    billing_address = serializers.SerializerMethodField('get_billing_address')
    lineItems = serializers.SerializerMethodField('get_line_items')

    class Meta:
        model = Checkout
        exclude = ['deleted', 'deleted_at', 'created_at', 'updated_at']

    @swagger_serializer_method(serializer_or_field=ShippingAddressSerializer)
    def get_shipping_address(self, obj):
        serializer_context = {'request': self.context.get('request')}
        shipping_address = ShippingAddress.objects.filter(checkout=obj, deleted=False).first()
        if not shipping_address:
            data = []
            return data
        serializer = ShippingAddressSerializer(shipping_address, context=serializer_context)
        return serializer.data

    @swagger_serializer_method(serializer_or_field=BillingAddressSerializer)
    def get_billing_address(self, obj):
        serializer_context = {'request': self.context.get('request')}
        billing_address = BillingAddress.objects.filter(checkout=obj, deleted=False).first()
        if not billing_address:
            data = []
            return data
        serializer = BillingAddressSerializer(billing_address, context=serializer_context)
        return serializer.data

    @swagger_serializer_method(serializer_or_field=LineItemsSerializer)
    def get_line_items(self, obj):
        serializer_context = {'request': self.context.get('request')}
        line_item_data = LineItems.objects.filter(checkout=obj, deleted=False)
        serializer = LineItemsSerializer(line_item_data, many=True, context=serializer_context)
        return serializer.data


# Create Checkout
class CheckoutAddSerializer(serializers.ModelSerializer):
    lineItems = serializers.SerializerMethodField('get_line_items')

    class Meta:
        model = Checkout
        fields = ('checkout_id', 'lineItems')

    @swagger_serializer_method(serializer_or_field=LineItemsSerializer)
    def get_line_items(self, obj):
        serializer_context = {'request': self.context.get('request')}
        line_item_data = LineItems.objects.filter(checkout=obj, deleted=False)
        serializer = LineItemsSerializer(line_item_data, many=True, context=serializer_context)
        return serializer.data

    @transaction.atomic
    def create(self, validated_data):
        try:
            validated_data = self.initial_data
            customer = validated_data.pop('customer', None)
            line_items = validated_data.pop('line_items')

            checkout = Checkout.objects.create(customer_id=customer, **validated_data)
            checkout.checkout_id = str(checkout.id) + str(secrets.token_hex(8))
            checkout.save()

            for line_item in line_items:
                vendor = line_item.pop('vendor')
                variant_id = line_item.pop('variant_id')
                variant = Variant.objects.filter(id=variant_id, deleted=False).first()
                product = Product.objects.filter(product_variant=variant, is_active=True, deleted=False).first()
                media = Media.objects.filter(product=product, position=1).first()

                if not variant or not product:
                    continue

                if media:
                    cdn_link = media.cdn_link
                else:
                    cdn_link = None

                line_item['price'] = variant.price
                line_item['compare_at_price'] = variant.compare_at_price
                line_item['total_price'] = int(variant.price) * int(line_item['quantity'])
                line_item['product_title'] = product.title
                line_item['variant_title'] = variant.title
                line_item['product_image'] = cdn_link

                lineitem = LineItems.objects.create(vendor_id=vendor, variant_id=variant_id, checkout=checkout, **line_item)

                checkout.subtotal_price += lineitem.total_price
                checkout.save()

            line_item_count = LineItems.objects.filter(checkout=checkout).count()
            if line_item_count == 0:
                raise exceptions.ParseError('lineitems length zero')

            # Buy x Get y
            discounts = Discount.objects.filter(discount_type='buy_x_get_y', is_active=True, deleted=False)
            line_items = LineItems.objects.filter(checkout=checkout)
            for discount in discounts:
                x_lineitems = []
                y_lineitems = []
                for line_item in line_items:
                    x_variant = get_x_lineitem(discount, line_item)
                    if x_variant:
                        x_lineitems.append(line_item)

                    y_variant = get_y_lineitem(discount, line_item)
                    if y_variant:
                        y_lineitems.append(line_item.id)

                y_lineitems = LineItems.objects.filter(id__in=y_lineitems).order_by('total_price')
                while True:
                    if discount.x_minimum_no_products <= len(x_lineitems):
                        x_lineitems = x_lineitems[discount.x_minimum_no_products:]
                        free_product = y_lineitems[:discount.y_minimum_no_products]
                        y_lineitems = y_lineitems[discount.y_minimum_no_products:]

                        for item in free_product:
                            try:
                                if discount.value_type == 'fixed_amount':
                                    discount_value = discount.value
                                    if discount_value < item.price:
                                        discount_price = item.price - discount_value
                                    else:
                                        discount_price = item.price

                                elif discount.value_type == 'percentage':
                                    discount_value = discount.value / item.quantity
                                    discount_price = item.price * (discount_value / 100)
                                    discount_price = item.price - discount_price
                                else:
                                    raise exceptions.ParseError('Invalid discount value type')

                                item.price = discount_price
                                item.total_price = discount_price * item.quantity
                                item.save()
                            except Exception as e:
                                print(e)
                    else:
                        break

                total_sum = LineItems.objects.filter(checkout=checkout).aggregate(Sum('total_price'))
                checkout.subtotal_price = total_sum['total_price__sum']
                checkout.save()
            return checkout

        except Exception as e:
            print(e)
            raise Exception(str(e))


def apply_shipping_discount(discount, checkout):
    if checkout.total_shipping != 0:
        line_items = LineItems.objects.filter(checkout=checkout)
        data = [{'id': line_item.id, 'shipping_percentage': (float(line_item.shipping_amount) / float(checkout.total_shipping)) * 100} for line_item in line_items]

        if discount.value_type == 'fixed_amount':
            discount_value = discount.value
            if discount_value < checkout.total_shipping:
                discount_price = checkout.total_shipping - discount_value
            else:
                discount_price = 0

        elif discount.value_type == 'percentage':
            discount_value = discount.value
            discount_price = checkout.total_shipping * (discount_value / 100)
            discount_price = checkout.total_shipping - discount_price
        else:
            raise exceptions.ParseError('Invalid discount value type')

        for item in data:
            shipping = (float(item['shipping_percentage']) / 100) * float(discount_price)
            lineitem = LineItems.objects.filter(id=item['id']).first()
            lineitem.shipping_amount = shipping
            lineitem.save()

        checkout.total_shipping = discount_price
        checkout.save()


# Update Checkout
class CheckoutUpdateSerializer(serializers.ModelSerializer):
    shipping_address = serializers.SerializerMethodField('get_shipping_address')
    billing_address = serializers.SerializerMethodField('get_billing_address')
    lineItems = serializers.SerializerMethodField('get_line_items')

    class Meta:
        model = Checkout
        exclude = ['id', 'deleted', 'deleted_at', 'created_at', 'updated_at', 'paid_by_wallet']

    @swagger_serializer_method(serializer_or_field=ShippingAddressSerializer)
    def get_shipping_address(self, obj):
        serializer_context = {'request': self.context.get('request')}
        shipping_address = ShippingAddress.objects.filter(checkout=obj, deleted=False).first()
        if not shipping_address:
            data = []
            return data
        serializer = ShippingAddressSerializer(shipping_address, context=serializer_context)
        return serializer.data

    @swagger_serializer_method(serializer_or_field=BillingAddressSerializer)
    def get_billing_address(self, obj):
        serializer_context = {'request': self.context.get('request')}
        billing_address = BillingAddress.objects.filter(checkout=obj, deleted=False).first()
        if not billing_address:
            data = []
            return data
        serializer = BillingAddressSerializer(billing_address, context=serializer_context)
        return serializer.data

    @swagger_serializer_method(serializer_or_field=LineItemsSerializer)
    def get_line_items(self, obj):
        serializer_context = {'request': self.context.get('request')}
        line_item_data = LineItems.objects.filter(checkout=obj, deleted=False)
        serializer = LineItemsSerializer(line_item_data, many=True, context=serializer_context)
        return serializer.data

    @transaction.atomic
    def update(self, instance, validated_data):
        try:
            validated_data = self.initial_data
            shipping_address = validated_data.pop('shipping_address', None)
            billing_address = validated_data.pop('billing_address', None)
            customer = validated_data.pop('customer', None)
            line_items = validated_data.pop('line_items', None)
            shipping_methods = validated_data.pop('shipping_methods', None)
            paid_by_wallet = validated_data.pop('paid_by_wallet', None)

            if customer is not None:
                validated_data['customer_id'] = customer

            Checkout.objects.filter(checkout_id=instance.checkout_id).update(**validated_data)
            checkout = Checkout.objects.filter(checkout_id=instance.checkout_id).first()

            if shipping_address is not None:
                address = ShippingAddress.objects.filter(checkout=checkout)
                if address:
                    address.update(checkout=checkout, **shipping_address)
                else:
                    ShippingAddress.objects.create(checkout=checkout, **shipping_address)

            if billing_address is not None:
                address = BillingAddress.objects.filter(checkout=checkout)
                if address:
                    address.update(checkout=checkout, **billing_address)
                else:
                    BillingAddress.objects.create(checkout=checkout, **billing_address)

            if line_items is not None:
                checkout.subtotal_price = 0
                checkout.save()

                if len(line_items) == 0:
                    raise exceptions.ParseError('lineitems length zero')

                for line_item in line_items:
                    vendor = line_item.pop('vendor')
                    variant_id = line_item.pop('variant_id')
                    variant = Variant.objects.filter(id=variant_id, deleted=False).first()
                    product = Product.objects.filter(product_variant=variant, is_active=True, deleted=False).first()
                    media = Media.objects.filter(product=product, position=1).first()

                    if not variant or not product:
                        if "id" in line_item:
                            LineItems.objects.filter(id=line_item['id']).delete()
                        continue

                    if media:
                        cdn_link = media.cdn_link
                    else:
                        cdn_link = None

                    line_item['product_title'] = product.title
                    line_item['variant_title'] = variant.title
                    line_item['product_image'] = cdn_link

                    if "id" in line_item:
                        LineItems.objects.filter(id=line_item['id']).update(vendor_id=vendor, variant=variant, checkout_id=checkout.id, **line_item)
                        line_item_obj = LineItems.objects.filter(id=line_item['id']).first()

                        if line_item_obj.promo_code:
                            checkout.subtotal_price += int(line_item_obj.total_price)
                        else:
                            line_item_obj.price = variant.price
                            line_item_obj.compare_at_price = variant.compare_at_price
                            line_item_obj.total_price = int(variant.price) * int(line_item['quantity'])
                            checkout.subtotal_price += int(variant.price) * int(line_item['quantity'])
                    else:
                        line_item_obj = LineItems.objects.create(vendor_id=vendor, variant=variant, checkout=checkout, **line_item)
                        line_item_obj.price = variant.price
                        line_item_obj.compare_at_price = variant.compare_at_price
                        line_item_obj.total_price = int(variant.price) * int(line_item['quantity'])
                        checkout.subtotal_price += int(variant.price) * int(line_item['quantity'])

                    line_item_obj.save()
                    checkout.save()

            line_items_list = LineItems.objects.filter(checkout=checkout)
            for line_item in line_items_list:
                product = Product.objects.filter(product_variant=line_item.variant, product_variant__deleted=False, is_active=True, deleted=False).first()
                if not product:
                    line_item.delete()

            line_items_count = LineItems.objects.filter(checkout=checkout).count()
            if line_items_count == 0:
                raise exceptions.ParseError('lineitems length zero')

            if shipping_methods is not None:
                total_shipping = 0
                for shipping_method in shipping_methods:
                    if shipping_method['selected_rule'] == 'Free Shipping':
                        shipping_method['shipping_id'] = None
                    else:
                        shipping = Shipping.objects.filter(id=shipping_method['shipping_id'], deleted=False).first()
                        rates = ConditionalRate.objects.filter(rule__shipping=shipping, rule__title__iexact=shipping_method['selected_rule'], deleted=False)
                        line_items = shipping_method['line_items']
                        count = len(line_items)

                        product_price = 0
                        product_weight = 0
                        for line_item_id in line_items:
                            line_item = LineItems.objects.filter(id=line_item_id).first()
                            variant = Variant.objects.filter(id=line_item.variant_id).first()
                            product_price += variant.price
                            product_price += variant.weight

                        shipping_amount = 0
                        for rate in rates:
                            if shipping.condition_type == 'weight':
                                product_value = product_weight
                            elif shipping.condition_type == 'price':
                                product_value = product_price
                            else:
                                product_value = None

                            min_value = rate.min_value
                            max_value = rate.max_value
                            amount = rate.amount

                            if product_value is not None:
                                if min_value == '' or min_value == 0:
                                    if product_value <= max_value:
                                        shipping_amount += amount
                                    else:
                                        shipping_amount += 0

                                elif max_value == 0:
                                    if product_value >= min_value:
                                        shipping_amount += amount
                                    else:
                                        shipping_amount += 0

                                elif min_value <= product_value <= max_value:
                                    shipping_amount += amount
                                else:
                                    shipping_amount += 0

                    if shipping_method['selected_rule'] == 'Free Shipping':
                        per_lineitem_shipping = 0
                        shipping_amount = 0
                    else:
                        per_lineitem_shipping = shipping_amount//count

                    remaining_shipping = 0
                    verify_shipping_amount = 0
                    for i in range(count):
                        verify_shipping_amount += per_lineitem_shipping

                    remaining_shipping = shipping_amount-verify_shipping_amount

                    total_shipping += shipping_amount

                    for i, item in enumerate(shipping_method['line_items'], 1):
                        line_item = LineItems.objects.filter(id=item).first()
                        line_item.shipping_name = shipping_method['selected_rule']
                        line_item.shipping_id = shipping_method['shipping_id']
                        line_item.shipping_amount = per_lineitem_shipping
                        if i == count:
                            if remaining_shipping > 0:
                                line_item.shipping_amount = per_lineitem_shipping+remaining_shipping
                        line_item.save()

                checkout.total_shipping = total_shipping
                checkout.save()

                # shipping discount
                today = datetime.now()
                discounts = Discount.objects.filter(discount_type='shipping_discount', deleted=False)
                if discounts:
                    for discount in discounts:
                        if discount.customer_eligibility == 'specific_customers':
                            if customer is not None:
                                customer_object = Customer.objects.filter(id=customer, customer_discount=discount).first()
                                if not customer_object:
                                    continue

                        if discount.start_date <= today <= discount.end_date:
                            if discount.minimum_purchase_amount:
                                if checkout.subtotal_price >= discount.minimum_purchase_amount:
                                    apply_shipping_discount(discount, checkout)
                                    break
                            else:
                                apply_shipping_discount(discount, checkout)
                                break

            # wallet payment
            if paid_by_wallet:
                wallet = Wallet.objects.filter(customer=checkout.customer).first()
                if wallet:
                    total_amount = float(checkout.subtotal_price) + float(checkout.total_shipping)
                    if total_amount <= wallet.value:
                        checkout.payment_method = 'wallet'
                        checkout.paid_by_wallet = total_amount
                        checkout.save()
                    elif total_amount > wallet.value:
                        checkout.payment_method = checkout.payment_method + ',wallet'
                        checkout.paid_by_wallet = wallet.value
                        checkout.save()
                    else:
                        pass

            discounts = Discount.objects.filter(discount_type='buy_x_get_y', is_active=True, deleted=False, status='Approved')
            line_items = LineItems.objects.filter(checkout=checkout)

            # remove discount
            if discounts:
                subtotal = 0
                for line_item in line_items:
                    line_item.price = line_item.variant.price
                    line_item.total_price = line_item.variant.price * line_item.quantity
                    subtotal += line_item.total_price
                    line_item.save()

                checkout.subtotal_price = subtotal
                checkout.save()

                # apply discount
                for discount in discounts:
                    x_lineitems = []
                    y_lineitems = []
                    for line_item in line_items:
                        x_variant = get_x_lineitem(discount, line_item)
                        if x_variant:
                            x_lineitems.append(line_item)

                        y_variant = get_y_lineitem(discount, line_item)
                        if y_variant:
                            y_lineitems.append(line_item.id)

                    y_lineitems = LineItems.objects.filter(id__in=y_lineitems).order_by('total_price')
                    while True:
                        if discount.x_minimum_no_products <= len(x_lineitems):
                            x_lineitems = x_lineitems[discount.x_minimum_no_products:]
                            free_product = y_lineitems[:discount.y_minimum_no_products]
                            y_lineitems = y_lineitems[discount.y_minimum_no_products:]

                            for item in free_product:
                                try:
                                    if discount.value_type == 'fixed_amount':
                                        discount_value = discount.value
                                        if discount_value < item.price:
                                            discount_price = item.price - discount_value
                                        else:
                                            discount_price = item.price

                                    elif discount.value_type == 'percentage':
                                        discount_value = discount.value / item.quantity
                                        discount_price = item.price * (discount_value / 100)
                                        discount_price = item.price - discount_price
                                    else:
                                        raise exceptions.ParseError('Invalid discount value type')

                                    item.price = discount_price
                                    item.total_price = discount_price * item.quantity
                                    item.save()
                                except Exception as e:
                                    print(e)
                        else:
                            break

                    total_sum = LineItems.objects.filter(checkout=checkout).aggregate(Sum('total_price'))
                    checkout.subtotal_price = total_sum['total_price__sum']
                    checkout.save()

            return checkout

        except Exception as e:
            print(e)
            raise Exception(str(e))


class ShippingCalculateSerializer(serializers.ModelSerializer):
    list_items = serializers.SerializerMethodField('get_items')
    total_price = serializers.SerializerMethodField('get_price')
    is_promocode = serializers.SerializerMethodField('get_ispromoapplied')
    applied_promocodes = serializers.SerializerMethodField('get_appliedpromocodes')

    class Meta:
        model = LineItems
        fields = ('list_items', 'total_price', 'is_promocode', 'applied_promocodes')

    def get_items(self, obj):
        list_items = list()
        for item in obj:
            vendor = (Vendor.objects.get(id=item.vendor.id)).name
            product = Product.objects.get(product_variant=item.variant)
            product_group = ProductGroup.objects.get(product_group=product)
            variant = Variant.objects.get(id=item.variant.id)

            # try:
            #     image = (Media.objects.filter(product=product, deleted=False).first()).cdn_link
            # except Exception as e:
            #     print(e)
            #     image = None

            items = {
                'id': item.id,
                'product': product.title,
                'product_group': product_group.id,
                'variant_name': variant.title,
                'quantity': item.quantity,
                'price': int(variant.price),
                'total_price': item.total_price,
                'image': item.product_image
            }

            check_vendor = [i for i in list_items if vendor in i['vendor']]
            if not check_vendor or len(list_items) == 0:
                list_items_objects = {
                    'vendor': vendor,
                    'items': list()
                }
                list_items_objects['items'].append(items)
                list_items.append(list_items_objects)

            if check_vendor:
                check_vendor[0]['items'].append(items)

        return list_items

    def get_ispromoapplied(self, obj):
        if 'checkout_id' in self.context:
            checkout_id = self.context['checkout_id']
            checkout = Checkout.objects.filter(checkout_id=checkout_id).first()
            if checkout.promo_code is not None:
                return True
            return False

    def get_appliedpromocodes(self, obj):
        if 'checkout_id' in self.context:
            checkout_id = self.context['checkout_id']
            checkout = Checkout.objects.filter(checkout_id=checkout_id).first()
            if checkout.promo_code is not None:
                promo_codes = checkout.promo_code.split(',')
                return promo_codes
            return []

    def get_price(self, obj):
        line_items = obj
        checkout = Checkout.objects.get(id=line_items[0].checkout_id)
        shipping_data = []

        shipping_address = ShippingAddress.objects.filter(checkout=checkout, deleted=False).first()
        city = shipping_address.city

        productgroup_lineitems = []
        for line_item in line_items:
            variant = Variant.objects.filter(id=line_item.variant_id).first()
            product_group = ProductGroup.objects.filter(product_group__product_variant=variant).first()

            check_group = [sub['product_group'] for sub in productgroup_lineitems]
            if product_group.id in check_group:
                for productgroup_lineitem in productgroup_lineitems:
                    if product_group.id == productgroup_lineitem['product_group']:
                        productgroup_lineitem['price'] += variant.price
                        productgroup_lineitem['weight'] += variant.weight
            else:
                price = variant.price
                weight = variant.weight
                productgroup_lineitems.append(
                    {'vendor': product_group.vendor.name, 'product_group': product_group.id, 'shipping_rule': [], 'price': price, 'weight': weight})

        default_shipping = {'shipping_id': None, 'product_group': [], 'price': 0, 'weight': 0}
        system_shipping_product_groups = []
        for line_item in productgroup_lineitems:
            order_price = line_item.pop('price')
            order_weight = line_item.pop('weight')

            product_group = ProductGroup.objects.filter(id=line_item['product_group']).first()
            shipping = Shipping.objects.filter(product_group=product_group, zone__city__name__iexact=city, is_active=True, deleted=False).first()
            if not shipping:
                shipping = Shipping.objects.filter(zone__city__name__iexact=city, default=True, is_active=True, deleted=False).first()
                if shipping:
                    default_shipping['shipping_id'] = shipping.id
                    default_shipping['price'] += order_price
                    default_shipping['weight'] += order_weight
                    default_shipping['product_group'].append(line_item['product_group'])
                    continue
                else:
                    system_shipping_product_groups.append(line_item['product_group'])

            if shipping:
                line_item['shipping_id'] = shipping.id
                line_item['shipping_rule'] = calculate_shipping(shipping, order_weight, order_price)
                shipping_data.append(line_item)

        if len(system_shipping_product_groups) > 0:
            shipping_data.append({'shipping_id': 0, 'product_group': system_shipping_product_groups,
                                  'shipping_rule': [{'name': 'Free Shipping', 'shipping_amount': 0}]})

        if default_shipping['shipping_id'] is not None:
            shipping_object = Shipping.objects.filter(id=default_shipping['shipping_id']).first()
            total_price = default_shipping['price']
            total_weight = default_shipping['weight']
            shipping_rule = calculate_shipping(shipping_object, total_weight, total_price)
            shipping_data.append({'shipping_id': shipping_object.id, 'product_group': default_shipping['product_group'], 'shipping_rule': shipping_rule})

        return shipping_data


class ThankYouSerializer(serializers.ModelSerializer):
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


class VerifyProductShippingSerializer(serializers.ModelSerializer):
    matched_ids = serializers.SerializerMethodField('get_city')

    class Meta:
        model = Checkout
        fields = ['matched_ids']

    def get_city(self, obj):
        matched_ids = []
        checkout_obj = json.loads(obj)
        line_items = LineItems.objects.filter(checkout__checkout_id=checkout_obj["checkout_id"], deleted=False)
        for line_item in line_items:
            cities = City.objects.filter(
                zone_city__shipping_zone__product_group__product_group__product_variant=line_item.variant)
            city_list = [city.name for city in cities]
            shipping_address = ShippingAddress.objects.filter(checkout__checkout_id=checkout_obj["checkout_id"], deleted=False).first()

            if shipping_address.city not in city_list:
                matched_ids.append(line_item.id)

        return matched_ids


class CheckoutLineItemSerializer(serializers.ModelSerializer):
    list_items = serializers.SerializerMethodField('get_items')
    is_promocode = serializers.SerializerMethodField('get_promoapplied')
    applied_promocodes = serializers.SerializerMethodField('get_appliedpromocodes')

    class Meta:
        model = LineItems
        fields = ('list_items', 'is_promocode', 'applied_promocodes')

    def get_items(self, obj):
        list_items = list()
        for item in obj:
            vendor = (Vendor.objects.get(id=item.vendor.id)).name
            product = Product.objects.get(product_variant=item.variant)
            product_group = ProductGroup.objects.get(product_group=product)
            variant = Variant.objects.get(id=item.variant.id)

            # try:
            #     image = (Media.objects.filter(product=product, deleted=False).first()).cdn_link
            # except Exception as e:
            #     print(e)
            #     image = None

            items = {
                'id': item.id,
                'product': product.title,
                'product_group': product_group.id,
                'variant_name': variant.title,
                'quantity': item.quantity,
                # 'price': int(variant.price),
                'price': int(item.price),
                'total_price': item.total_price,
                'image': item.product_image
            }

            check_vendor = [i for i in list_items if vendor in i['vendor']]
            if not check_vendor or len(list_items) == 0:
                list_items_objects = {
                    'vendor': vendor,
                    'items': list()
                }
                list_items_objects['items'].append(items)
                list_items.append(list_items_objects)

            if check_vendor:
                check_vendor[0]['items'].append(items)

        return list_items

    def get_appliedpromocodes(self, obj):
        if 'checkout_id' in self.context:
            checkout_id = self.context['checkout_id']
            checkout = Checkout.objects.filter(checkout_id=checkout_id).first()
            if checkout.promo_code is not None:
                promo_codes = checkout.promo_code.split(',')
                return promo_codes
            return []

    def get_promoapplied(self, obj):
        if 'checkout_id' in self.context:
            checkout_id = self.context['checkout_id']
            checkout = Checkout.objects.filter(checkout_id=checkout_id).first()
            if checkout.promo_code is not None:
                return True
            return False


class CountryListSerializer(serializers.ModelSerializer):
    text = serializers.CharField(source='name')
    key = serializers.CharField(source='id')
    flag = serializers.CharField(source='short_code')
    value = serializers.CharField(source='short_code')

    class Meta:
        model = Country
        fields = ('key', 'value', 'flag', 'text')


class CityListSerializer(serializers.ModelSerializer):
    text = serializers.CharField(source='name')
    key = serializers.CharField(source='id')
    value = serializers.CharField(source='name')

    class Meta:
        model = City
        fields = ('key', 'value', 'text')
