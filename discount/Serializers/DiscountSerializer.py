
from rest_framework import serializers, exceptions
from crm.models import Customer
from discount.BusinessLogic.ApplyDiscount import apply_discount
from discount.models import Discount, DiscountHandle
from products.BusinessLogic.RemoveSpecialCharacters import remove_specialcharacters
from datetime import datetime
from products.models import Product, Variant, Media
from vendor.BussinessLogic.AddApproval import add_approval_entry
from vendor.models import DataApproval


class ProductSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.name', required=True)
    price = serializers.SerializerMethodField('get_price')
    image = serializers.SerializerMethodField('get_media')

    class Meta:
        model = Product
        fields = ('id', 'title', 'vendor_name', 'price', 'image')

    def get_price(self, obj):
        variant = Variant.objects.filter(product=obj, deleted=False).first()
        return variant.price

    def get_media(self, obj):
        media = Media.objects.filter(product=obj, deleted=False).first()
        if not media:
            return None
        return media.cdn_link


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('id', 'first_name', 'last_name', 'email')


class DiscountListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = ('id', 'title', 'status', 'value', 'value_type', 'is_active')


class DiscountDetailSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField('get_customers')
    product = serializers.SerializerMethodField('get_products')
    y_product = serializers.SerializerMethodField('get_y_products')
    reason = serializers.SerializerMethodField('get_reason')

    class Meta:
        model = Discount
        exclude = ('deleted', 'deleted_at', 'tags')

    def get_customers(self, obj):
        serializer_context = {'request': self.context.get('request')}
        customer_data = Customer.objects.filter(customer_discount=obj, deleted=False)
        serializer = CustomerSerializer(customer_data, many=True, context=serializer_context)
        return serializer.data

    def get_products(self, obj):
        serializer_context = {'request': self.context.get('request')}
        product_data = Product.objects.filter(product_discount=obj, deleted=False)
        serializer = ProductSerializer(product_data, many=True, context=serializer_context)
        return serializer.data

    def get_y_products(self, obj):
        serializer_context = {'request': self.context.get('request')}
        product_data = Product.objects.filter(y_product_discount=obj, deleted=False)
        serializer = ProductSerializer(product_data, many=True, context=serializer_context)
        return serializer.data

    def get_reason(self, obj):
        data = DataApproval.objects.filter(content_type__model='discount', status='Disapproved', object_id=obj.id, deleted=False).first()
        if data:
            reason = data.reason
        else:
            reason = None
        return reason


class AddDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = ('id', 'title',)
        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=Discount.objects.filter(deleted=False),
        #         fields=['title']
        #     )
        # ]

    def create(self, validate_data):
        try:
            validated_data = self.initial_data
            handle_name = remove_specialcharacters(validated_data['title'].replace(' ', '-').lower())
            handle = DiscountHandle.objects.filter(name=handle_name).first()

            if handle is not None:
                handle_name = handle_name + "-" + str(handle.count)
                handle.count = handle.count + 1
                handle.save()
            else:
                handle = DiscountHandle()
                handle.name = handle_name
                handle.count = 1
                handle.save()

            validated_data['handle'] = handle_name

            vendor_id = validated_data.pop('vendor')
            main_category = validated_data.pop('main_category', None)
            sub_category = validated_data.pop('sub_category', None)
            super_sub_category = validated_data.pop('super_sub_category', None)
            product = validated_data.pop('product', None)
            product_group = validated_data.pop('product_group', None)
            y_main_category = validated_data.pop('y_main_category', None)
            y_sub_category = validated_data.pop('y_sub_category', None)
            y_super_sub_category = validated_data.pop('y_super_sub_category', None)
            y_product = validated_data.pop('y_product', None)
            y_product_group = validated_data.pop('y_product_group', None)
            customer = validated_data.pop('customer', None)
            shipping = validated_data.pop('shipping', None)

            if not validated_data['start_date']:
                validated_data['start_date'] = None
            if not validated_data['end_date']:
                validated_data['end_date'] = None

            discount = Discount.objects.create(vendor_id=vendor_id, **validated_data)

            discount.main_category.set(main_category)
            discount.sub_category.set(sub_category)
            discount.super_sub_category.set(super_sub_category)

            if product is not None and len(product) > 0:
                discount.product.set(product)

            if product_group is not None and len(product_group) > 0:
                discount.product_group.set(product_group)

            if y_main_category is not None and len(y_main_category) > 0:
                discount.y_main_category.set(y_main_category)

            if y_sub_category is not None and len(y_sub_category) > 0:
                discount.y_sub_category.set(y_sub_category)

            if y_super_sub_category is not None and len(y_super_sub_category) > 0:
                discount.y_super_sub_category.set(y_super_sub_category)

            if y_product is not None and len(y_product) > 0:
                discount.y_product.set(y_product)

            if y_product_group is not None and len(y_product_group) > 0:
                discount.y_product_group.set(y_product_group)

            if customer is not None and len(customer) > 0:
                discount.customer.set(customer)

            if shipping is not None and len(shipping) > 0:
                discount.shipping.set(shipping)

            # approval entry
            try:
                add_approval_entry(title=discount.title,
                                   vendor=discount.vendor,
                                   instance=discount,
                                   )
            except Exception as e:
                print(e)

            return discount
        except Exception as e:
            print(e)
            raise Exception(str(e))

    def update(self, instance, validate_data):
        try:
            validated_data = self.initial_data

            vendor_id = validated_data.pop('vendor')
            main_category = validated_data.pop('main_category', None)
            sub_category = validated_data.pop('sub_category', None)
            super_sub_category = validated_data.pop('super_sub_category', None)
            product = validated_data.pop('product', None)
            product_group = validated_data.pop('product_group', None)
            y_main_category = validated_data.pop('y_main_category', None)
            y_sub_category = validated_data.pop('y_sub_category', None)
            y_super_sub_category = validated_data.pop('y_super_sub_category', None)
            y_product = validated_data.pop('y_product', None)
            y_product_group = validated_data.pop('y_product_group', None)
            customer = validated_data.pop('customer', None)
            shipping = validated_data.pop('shipping', None)

            if not validated_data['start_date']:
                validated_data['start_date'] = None
            if not validated_data['end_date']:
                validated_data['end_date'] = None

            Discount.objects.filter(id=instance.id).update(vendor_id=vendor_id, **validated_data)
            discount = Discount.objects.get(id=instance.id)

            discount.main_category.set(main_category)
            discount.sub_category.set(sub_category)
            discount.super_sub_category.set(super_sub_category)
            discount.product.set(product)
            discount.product_group.set(product_group)
            discount.y_main_category.set(y_main_category)
            discount.y_sub_category.set(y_sub_category)
            discount.y_super_sub_category.set(y_super_sub_category)
            discount.y_product.set(y_product)
            discount.y_product_group.set(y_product_group)
            discount.customer.set(customer)

            try:
                # approval entry
                add_approval_entry(title=discount.title,
                                   vendor=discount.vendor,
                                   instance=discount,
                                   )
            except Exception as e:
                print(e)

            if discount.discount_type == 'simple_discount':
                if discount.status == 'Approved':
                    apply_discount(discounts=[discount])

            return instance

        except Exception as e:
            print(e)
            raise Exception(str(e))


class DiscountStatusChangeSerializer(serializers.ModelSerializer):
    ids = serializers.ListField(required=True)
    status = serializers.CharField(max_length=50, allow_blank=False, allow_null=False)
    value = serializers.BooleanField(default=False)

    class Meta:
        model = Discount
        fields = ('ids', 'status', 'value',)

    def create(self, validated_data):
        validated_data = self.initial_data
        if validated_data["status"] == "active":
            try:
                Discount.objects.filter(id__in=validated_data['ids']).update(is_active=validated_data["value"])
            except Exception as e:
                raise exceptions.ParseError(str(e))

            return validated_data


class DiscountBulkDeleteSerializer(serializers.ModelSerializer):
    ids = serializers.ListField(required=True)

    class Meta:
        model = Discount
        fields = ('ids',)

    def create(self, validated_data):
        validated_data = self.initial_data
        try:
            Discount.objects.filter(id__in=validated_data['ids']).update(deleted=True, deleted_at=datetime.now())
        except Exception as e:
            raise exceptions.ParseError(str(e))

        return validated_data
