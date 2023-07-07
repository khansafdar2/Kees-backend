
from rest_framework import serializers, exceptions
from products.models import ProductGroup, Product, ProductGroupHandle
from products.BusinessLogic.RemoveSpecialCharacters import remove_specialcharacters
from vendor.BussinessLogic.AddApproval import add_approval_entry
from vendor.models import DataApproval


class ProductGroupListSerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()
    vendor_name = serializers.CharField(source='vendor.name')

    class Meta:
        model = ProductGroup
        exclude = ['deleted', 'deleted_at']

    def get_product_count(self, obj):
        return Product.objects.filter(product_group=obj, deleted=False).count()


class ProductGroupDetailSerializer(serializers.ModelSerializer):
    reason = serializers.SerializerMethodField('get_reason')

    class Meta:
        model = ProductGroup
        exclude = ['deleted', 'deleted_at', 'created_at', 'updated_at', 'handle']

    def get_reason(self, obj):
        data = DataApproval.objects.filter(content_type__model='productgroup', status='Disapproved', object_id=obj.id,
                                           deleted=False).first()
        if data:
            reason = data.reason
        else:
            reason = None
        return reason


class ProductGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductGroup
        exclude = ['deleted', 'deleted_at', 'created_at', 'updated_at', 'handle']

    def create(self, validate_data):
        try:
            validated_data = self.initial_data
            vendor = validated_data.pop('vendor')

            if 'tat' in validated_data:
                tat = validated_data['tat']
                if tat is not None and len(tat) > 0:
                    if '-' not in validated_data['tat']:
                        raise exceptions.ParseError("Please enter '-' separated TAT")

            handle_name = remove_specialcharacters(validated_data['title'].replace(' ', '-').lower())
            handle = ProductGroupHandle.objects.filter(name=handle_name).first()
            if handle is not None:
                handle_name = handle_name + "-" + str(handle.count)
                handle.count = handle.count + 1
                handle.save()
            else:
                handle = ProductGroupHandle()
                handle.name = handle_name
                handle.count = 1
                handle.save()
            validated_data['handle'] = handle_name
            product_group = ProductGroup.objects.create(vendor_id=vendor, **validated_data)

            add_approval_entry(title=product_group.title,
                               vendor=product_group.vendor,
                               instance=product_group,
                               )

            return product_group
        except Exception as e:
            print(e)
            raise Exception(str(e))

    def update(self, instance, validate_data):
        try:
            validated_data = self.initial_data
            vendor = validated_data.pop('vendor')

            if 'tat' in validated_data:
                tat = validated_data['tat']
                if tat is not None or tat != '':
                    if '-' not in validated_data['tat']:
                        raise exceptions.ParseError("Please enter '-' separated TAT")

            ProductGroup.objects.filter(id=instance.id).update(vendor_id=vendor, **validated_data)
            product_group = ProductGroup.objects.get(id=instance.id)

            # approval entry
            add_approval_entry(title=product_group.title,
                               vendor=product_group.vendor,
                               instance=product_group,
                               )

            return validate_data

        except Exception as e:
            print(e)
            raise Exception(str(e))

    def validate(self, data):
        return data


class ProductGroupStatusChangeSerializer(serializers.ModelSerializer):
    ids = serializers.ListField(required=True)
    status = serializers.CharField(max_length=50, allow_blank=False, allow_null=False)
    value = serializers.BooleanField(default=False)

    class Meta:
        model = ProductGroup
        fields = ('ids', 'status', 'value')

    def create(self, validated_data):
        validated_data = self.initial_data
        user = validated_data['user']

        if validated_data["status"] == "approved":
            try:
                ProductGroup.objects.filter(id__in=validated_data['ids']).update(status=validated_data["value"])
            except Exception as e:
                raise exceptions.ParseError(str(e))
            return validated_data
        elif validated_data["status"] == "active":
            try:
                if user.is_vendor:
                    ProductGroup.objects.filter(id__in=validated_data['ids'], vendor_id=user.vendor_id).update(is_active=validated_data["value"])
                else:
                    ProductGroup.objects.filter(id__in=validated_data['ids']).update(is_active=validated_data["value"])
            except Exception as e:
                raise exceptions.ParseError(str(e))
            return validated_data
        raise exceptions.ParseError("Status can be approved or active")


