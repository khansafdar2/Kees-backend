
from products.models import Variant, Product
from rest_framework import exceptions
from rest_framework.response import Response


def CheckVariantQuantity(lineitems):
    data = []
    for lineitem in lineitems:
        quantity = int(lineitem['quantity'])
        variant = Variant.objects.filter(id=lineitem['variant_id']).first()
        product = Product.objects.filter(product_variant=variant).first()

        if variant:
            if quantity > variant.inventory_quantity:
                data.append({'variant_id': variant.id, 'variant_title': variant.title, 'product': product.title, 'available_quantity': variant.inventory_quantity})
        else:
            data.append({'variant_id': lineitem['variant_id'], 'variant_title': None, 'product': None,
                         'available_quantity': None})

    if len(data) > 0:
        return data
    else:
        return False

