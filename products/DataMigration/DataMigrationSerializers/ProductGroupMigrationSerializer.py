
from rest_framework import serializers, exceptions
from products.models import ProductGroup, Product, ProductGroupHandle
from products.BusinessLogic.RemoveSpecialCharacters import remove_specialcharacters


class ProductGroupMigrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductGroup
        fields = '__all__'

    def create(self, validate_data):
        try:
            validated_data = self.initial_data
            vendor = validated_data.pop('vendor')
            discount = validated_data.pop('discount', None)
            shipping = validated_data.pop('shipping', None)

            if 'tat' in validated_data:
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

            if discount is not None:
                if len(discount) == 0 or discount[0] == '':
                    discount = None

            if shipping is not None:
                if len(shipping) == 0 or shipping[0] == '':
                    shipping = None

            product_group_data = {
                "title": validated_data['title'],
                "handle": handle_name,
                "tat": validated_data['tat'],
                "vendor_id": vendor,
                "discount_id": discount,
                "shipping_id": shipping
            }

            product_group = ProductGroup.objects.create(**product_group_data)

            return product_group
        except Exception as e:
            print(e)
            raise Exception(str(e))
