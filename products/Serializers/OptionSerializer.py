from rest_framework import serializers, exceptions
from products.models import Option


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        exclude = ['deleted', 'deleted_at']

    def create(self, validate_data):
        try:
            validated_data = self.initial_data
            product = validated_data.pop('product')
            if Option.objects.filter(product_id=product, position=validated_data['position']).exists():
                raise exceptions.ParseError("Position already exists")
            option = Option.objects.create(product_id=product, **validated_data)
            return option
        except Exception as e:
            print(e)
            raise Exception(str(e))


class OptionUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = Option
        exclude = ['deleted', 'deleted_at']

    def update(self, instance, validate_data):
        try:
            validated_data = self.initial_data
            product = validated_data.pop('product')
            Option.objects.filter(id=instance.id).update(product_id=product, **validated_data)
            return instance

        except Exception as e:
            print(e)
            raise Exception(str(e))
