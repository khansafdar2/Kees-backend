
from order.models import LineItems, ShippingAddress, BillingAddress, DraftOrder
from products.models import Variant, Product, Media
from crm.models import Customer
from setting.models import StoreInformation
from rest_framework import serializers
from django.db import transaction
from order.BusinessLogic.OrderEmail import orderemail
from order.BusinessLogic.OrderConversion import ConvertOpenOrder
from order.Serializers.CheckoutSerializers import ShippingAddressSerializer, BillingAddressSerializer


class DraftOrderListSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField('get_customer')

    class Meta:
        model = DraftOrder
        exclude = ['customer', 'updated_at']

    def get_customer(self, obj):
        customer = Customer.objects.filter(draft_order_customer=obj, deleted=False).first()
        if not customer:
            return None
        name = f"{customer.first_name} {customer.last_name}"
        return name


class LineItemsSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='variant.product.title', read_only=True, allow_null=True, allow_blank=True)
    vendor_name = serializers.CharField(source='vendor.name', read_only=True, allow_null=True, allow_blank=True)
    variant_title = serializers.CharField(source='variant.title', read_only=True, allow_null=True, allow_blank=True)
    price = serializers.CharField(source='variant.price', read_only=True, allow_null=True, allow_blank=True)
    shipping = serializers.CharField(source='variant.product.product_group.shipping.amount', read_only=True, allow_null=True, allow_blank=True)
    subtotal = serializers.SerializerMethodField('get_price')
    image = serializers.SerializerMethodField('get_image')

    class Meta:
        model = LineItems
        fields = '__all__'

    def get_price(self, obj):
        variant = Variant.objects.get(id=obj.variant_id)
        price = int(variant.price) * int(obj.quantity)
        return price

    def get_image(selfself, obj):
        product = Product.objects.filter(product_variant=obj.variant_id).first()
        if product:
            image = Media.objects.filter(product_id=product.id).first()
            if image:
                return image.cdn_link


class DraftOrderDetailSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField('get_customer')
    lineitems = serializers.SerializerMethodField('get_lineitems')
    shipping_address = serializers.SerializerMethodField('get_shipping_address')
    billing_address = serializers.SerializerMethodField('get_billing_address')

    class Meta:
        model = DraftOrder
        exclude = ['created_at', 'updated_at']

    def get_lineitems(self, obj):
        serializer_context = {'request': self.context.get('request')}
        lineitem_data = LineItems.objects.filter(draft_order=obj, deleted=False)
        serializer = LineItemsSerializer(lineitem_data, many=True, context=serializer_context)
        return serializer.data

    def get_shipping_address(self, obj):
        serializer_context = {'request': self.context.get('request')}
        shipping_address_data = ShippingAddress.objects.filter(draft_order=obj, deleted=False).first()
        if shipping_address_data:
            serializer = ShippingAddressSerializer(shipping_address_data, context=serializer_context)
            return serializer.data
        data = {}
        return data

    def get_billing_address(self, obj):
        serializer_context = {'request': self.context.get('request')}
        billing_address_data = BillingAddress.objects.filter(draft_order=obj, deleted=False).first()
        if billing_address_data:
            serializer = BillingAddressSerializer(billing_address_data, context=serializer_context)
            return serializer.data
        data = {}
        return data

    def get_customer(self, obj):
        customer = Customer.objects.filter(draft_order_customer=obj, deleted=False).first()
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


class AdminOrderAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = DraftOrder
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        validated_data = self.initial_data
        customer = validated_data.pop('customer', None)
        shipping_address = validated_data.pop('shipping_address', None)
        billing_address = validated_data.pop('billing_address', None)
        line_items = validated_data.pop('line_items')
        open_order = validated_data.pop('open_order')

        if customer is not None:
            customer = Customer.objects.filter(id=customer).first()
            customer_email = customer.email
        else:
            customer_email = False

        store = StoreInformation.objects.filter(deleted=False).first()

        if not open_order:
            validated_data.pop('payment_method', None)
            validated_data.pop('payment_status', None)
            validated_data['name'] = '#D' + str(store.order_counter)
            draft_order = DraftOrder.objects.create(customer=customer, **validated_data)

            store.order_counter += 1
            store.save()

            for line_item in line_items:
                vendor = line_item.pop('vendor')
                variant_id = line_item.pop('variant_id')
                variant = Variant.objects.filter(id=variant_id).first()
                LineItems.objects.create(vendor_id=vendor, variant=variant, draft_order=draft_order, quantity=line_item['quantity'], shipping_amount=line_item['shipping_amount'])

            if shipping_address is not None:
                ShippingAddress.objects.create(draft_order=draft_order, **shipping_address)

            if billing_address is not None:
                BillingAddress.objects.create(draft_order=draft_order, **billing_address)

            return draft_order

        else:
            order = ConvertOpenOrder(validated_data=validated_data,
                                     customer=customer,
                                     shipping_address=shipping_address,
                                     billing_address=billing_address,
                                     line_items=line_items,
                                     store=store)
            if customer_email:
                orderemail(
                    order=order,
                    bcc_email=store.store_contact_email,
                    email_subject=f"Your order {order.order_id}",
                    email_heading="Thank you for purchase at KEES",
                    description="we're getting your order ready to be shipped. We will notify you when it has been sent."
                )
            return order

    @transaction.atomic
    def update(self, instance, validated_data):
        validated_data = self.initial_data
        customer = validated_data.pop('customer', None)
        shipping_address = validated_data.pop('shipping_address', None)
        billing_address = validated_data.pop('billing_address', None)
        line_items = validated_data.pop('line_items', None)
        open_order = validated_data.pop('open_order')

        if customer is not None:
            customer = Customer.objects.filter(id=customer).first()
            customer_email = customer.email
        else:
            customer_email = False

        store = StoreInformation.objects.filter(deleted=False).first()

        if not open_order:
            validated_data.pop('payment_method', None)
            validated_data.pop('payment_status', None)
            draft_order = DraftOrder.objects.filter(id=instance.id).update(customer=customer, **validated_data)

            if shipping_address is not None:
                ShippingAddress.objects.filter(draft_order_id=instance.id).update(**shipping_address)

            if billing_address is not None:
                BillingAddress.objects.filter(draft_order_id=instance.id).update(**billing_address)

            return draft_order

        else:
            order = ConvertOpenOrder(validated_data=validated_data,
                                     customer=customer,
                                     shipping_address=shipping_address,
                                     billing_address=billing_address,
                                     line_items=line_items,
                                     store=store)

            DraftOrder.objects.filter(id=instance.id).delete()

            if customer_email:
                orderemail(
                    order=order,
                    bcc_email=store.store_contact_email,
                    email_subject=f"Your order {order.order_id}",
                    email_heading="Thank you for purchase at KEES",
                    description="we're getting your order ready to be shipped. We will notify you when it has been sent."
                )

            return order
