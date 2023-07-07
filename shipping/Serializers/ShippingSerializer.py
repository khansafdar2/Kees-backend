
from products.models import ProductGroup
from shipping.models import Shipping, ConditionalRate, Rule
from rest_framework import serializers
from vendor.BussinessLogic.AddApproval import add_approval_entry
from vendor.models import DataApproval


class ShippingProductGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductGroup
        fields = ('id', 'title')


class ShippingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipping
        fields = '__all__'


class ShippingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipping
        exclude = ['product_group']

    def create(self, validated_data):
        validated_data = self.initial_data
        zone_id = validated_data.pop('zone')
        vendor_id = validated_data.pop('vendor', None)
        product_group = validated_data.pop('product_group', None)
        rules = validated_data.pop('rules')

        # create shipping
        shipping = Shipping.objects.create(zone_id=zone_id, vendor_id=vendor_id, **validated_data)

        if product_group is not None and len(product_group) > 0:
            shipping.product_group.set(product_group)

        # create Rules
        for rule in rules:
            conditional_rates = rule.pop('conditional_rates')
            rule['shipping'] = shipping
            rule = Rule.objects.create(**rule)

            # create conditional rates
            for conditional_rate in conditional_rates:
                conditional_rate['rule'] = rule
                ConditionalRate.objects.create(**conditional_rate)

        # approval entry
        if not shipping.default:
            add_approval_entry(title=shipping.title,
                               vendor=shipping.vendor,
                               instance=shipping,
                               )

        return shipping

    def update(self, instance, validated_data):
        validated_data = self.initial_data
        zone_id = validated_data.pop('zone')
        vendor_id = validated_data.pop('vendor', None)
        product_group = validated_data.pop('product_group', None)
        rules = validated_data.pop('rules')

        # update shipping
        Shipping.objects.filter(id=instance.id).update(zone_id=zone_id, vendor_id=vendor_id, **validated_data)
        shipping = Shipping.objects.get(id=instance.id)

        if product_group is not None and len(product_group) > 0:
            shipping.product_group.set(product_group)

        Rule.objects.filter(shipping=shipping).delete()
        # Update Rules
        for rule in rules:
            conditional_rates = rule.pop('conditional_rates')
            rule['shipping'] = shipping

            rule = Rule.objects.create(**rule)

            for conditional_rate in conditional_rates:
                conditional_rate['rule'] = rule

                ConditionalRate.objects.create(**conditional_rate)

        # approval entry
        if not shipping.default:
            add_approval_entry(title=shipping.title,
                               vendor=shipping.vendor,
                               instance=shipping,
                               )

        return instance


class ConditionalRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConditionalRate
        fields = '__all__'


class RuleSerializer(serializers.ModelSerializer):
    conditional_rates = serializers.SerializerMethodField('get_conditional_rates')

    class Meta:
        model = Rule
        fields = '__all__'

    def get_conditional_rates(self, obj):
        serializer_context = {'request': self.context.get('request')}
        rate_data = ConditionalRate.objects.filter(rule=obj, is_active=True, deleted=False)
        serializer = ConditionalRateSerializer(rate_data, many=True, context=serializer_context)
        return serializer.data


class ShippingDetailSerializer(serializers.ModelSerializer):
    zone_name = serializers.CharField(source='zone.title', allow_null=True, allow_blank=True, required=False)
    rules = serializers.SerializerMethodField('get_rules')
    reason = serializers.SerializerMethodField('get_reason')

    class Meta:
        model = Shipping
        fields = '__all__'

    def get_rules(self, obj):
        serializer_context = {'request': self.context.get('request')}
        rule_data = Rule.objects.filter(shipping=obj, deleted=False, is_active=True)
        serializer = RuleSerializer(rule_data, many=True, context=serializer_context)
        return serializer.data

    def get_reason(self, obj):
        data = DataApproval.objects.filter(content_type__model='shipping', status='Disapproved', object_id=obj.id, deleted=False).first()
        if data:
            reason = data.reason
        else:
            reason = None
        return reason
