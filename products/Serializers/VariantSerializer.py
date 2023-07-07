from rest_framework import serializers, exceptions
from products.models import Variant, InventoryHistory, Product, Option
from products.BusinessLogic.InventoryTrack import AddInventoryEvent
from products.BusinessLogic.HideOutOfStock import hide_stock
from rest_framework.validators import UniqueTogetherValidator
from django.db import transaction


class VariantDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        exclude = [
            'deleted',
            'deleted_at',
        ]


class VariantAddSerializer(serializers.ModelSerializer):

    class Meta:
        model = Variant
        exclude = [
            'deleted',
            'deleted_at',
            'created_at',
            'updated_at',
            'id',
            'old_inventory_quantity',
            'weight_unit'
        ]
        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=Variant.objects.filter(deleted=False),
        #         fields=['sku']
        #     )
        # ]

    @transaction.atomic
    def create(self, validated_data):
        try:
            validated_data = self.initial_data
            user = validated_data.pop('user')
            product = validated_data.pop('product')
            options = Option.objects.filter(product_id=product, deleted=False).order_by('id')
            counter = 1
            for option in options:
                found = False
                variant_option = validated_data['option' + str(counter)]
                if variant_option is None:
                    counter += 1
                    continue
                values = option.values.split(",")
                for value in values:
                    if value == variant_option:
                        found = True
                        break
                if not found:
                    option.values = option.values + "," + variant_option
                    option.save()
                counter += 1

            product = Product.objects.get(id=product)

            if validated_data['is_physical']:
                if validated_data['weight'] == 0:
                    raise exceptions.ParseError("physical product weight cannot be null")
            else:
                validated_data['weight'] = 0

            if validated_data['compare_at_price'] is None:
                validated_data['compare_at_price'] = validated_data['price']
            else:
                if float(validated_data['compare_at_price']) < float(validated_data['price']):
                    validated_data['compare_at_price'] = validated_data['price']

            variant = Variant.objects.create(product_id=product.id, **validated_data)

            # hide out of stock
            hide_stock(product)

            if product.track_inventory:
                AddInventoryEvent(
                    variant=variant,
                    user=user,
                    event="Initial Inventory",
                    quantity=variant.inventory_quantity,
                    new_inventory=variant.inventory_quantity,
                    old_inventory=0)
            return variant
        except Exception as e:
            print(e)
            raise Exception(str(e))


class UpdateVariantSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = Variant
        exclude = [
            'deleted',
            'deleted_at',
            'created_at',
            'updated_at',
            'weight_unit',
        ]
        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=Variant.objects.filter(deleted=False),
        #         fields=['sku']
        #     )
        # ]

    @transaction.atomic
    def update(self, instance, validate_data):
        try:
            validated_data = self.initial_data
            product = Product.objects.get(id=validated_data['product'])

            if validated_data['is_physical']:
                if validated_data['weight'] == 0:
                    raise exceptions.ParseError("physical product weight cannot be null")
            else:
                validated_data['weight'] = 0

            if 'weight_unit' in validated_data:
                raise exceptions.ParseError("Weight Unit cannot be updated through this api")

            if validated_data['compare_at_price'] is None:
                validated_data['compare_at_price'] = validated_data['price']
            else:
                if float(validated_data['compare_at_price']) < float(validated_data['price']):
                    validated_data['compare_at_price'] = validated_data['price']

            user = validated_data.pop('user')
            if int(validated_data["inventory_quantity"]) != instance.inventory_quantity:
                if int(validated_data['inventory_quantity']) > instance.inventory_quantity:
                    event = "Manually Added"
                elif int(validated_data['inventory_quantity']) < instance.inventory_quantity:
                    event = "Manually Removed"
                else:
                    event = "Not Found"
                validated_data["old_inventory_quantity"] = instance.inventory_quantity

                if product.track_inventory:
                    AddInventoryEvent(
                        variant=instance,
                        user=user,
                        event=event,
                        quantity=instance.inventory_quantity,
                        new_inventory=validated_data['inventory_quantity'],
                        old_inventory=instance.old_inventory_quantity)

            product_id = validated_data.pop('product')
            product = Product.objects.filter(id=product_id, deleted=False).first()
            options = Option.objects.filter(product=product, deleted=False).order_by('id')
            counter = 1
            for option in options:
                found = False
                variant_option = validated_data['option' + str(counter)]
                if variant_option is None:
                    counter += 1
                    continue
                values = option.values.split(",")
                for value in values:
                    if value == variant_option:
                        found = True
                        break
                if not found:
                    option.values = option.values + "," + variant_option
                    option.save()
                counter += 1
            Variant.objects.filter(id=instance.id).update(product=product, **validated_data)
            variant = Variant.objects.get(id=instance.id)

            # hide out of stock
            hide_stock(product)

            return variant
        except Exception as e:
            print(e)
            raise Exception(str(e))


class BulkDeleteVariantsSerializer(serializers.Serializer):
    ids = serializers.ListField(required=True)
    product = serializers.ListField(required=True)


class GetInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryHistory
        fields = '__all__'
