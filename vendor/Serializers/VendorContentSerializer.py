
from rest_framework import serializers
from discount.BusinessLogic.DeleteDiscount import delete_discount
from discount.BusinessLogic.ApplyDiscount import apply_discount
from products.models import ProductGroup, Product, Collection
from shipping.models import Shipping
from discount.models import Discount
from vendor.models import DataApproval


class VendorContentListSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.name')
    content_type = serializers.CharField(source='content_type.model')

    class Meta:
        model = DataApproval
        exclude = ['deleted', 'deleted_at']


class UpdateApprovalDataStatusSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = DataApproval
        fields = ('id', 'status')

    def update(self, instance, validate_data):
        try:
            validated_data = self.initial_data
            DataApproval.objects.filter(id=instance.id).update(**validated_data)

            if instance.content_type.model == 'product':
                Product.objects.filter(id=instance.object_id).update(status=validated_data['status'])
            elif instance.content_type.model == 'productgroup':
                ProductGroup.objects.filter(id=instance.object_id).update(status=validated_data['status'])
            elif instance.content_type.model == 'collection':
                Collection.objects.filter(id=instance.object_id).update(status=validated_data['status'])
            elif instance.content_type.model == 'shipping':
                Shipping.objects.filter(id=instance.object_id).update(status=validated_data['status'])
            elif instance.content_type.model == 'discount':
                discount = Discount.objects.filter(id=instance.object_id, discount_type='simple_discount', is_active=True).first()
                if validated_data['status'] == 'Approved':
                    if discount:
                        apply_discount(discounts=[discount])
                elif validate_data['status'] == 'Disapproved':
                    if discount:
                        delete_discount(discount)
                Discount.objects.filter(id=instance.object_id).update(status=validated_data['status'])

            return instance

        except Exception as e:
            print(e)
            raise Exception(str(e))
