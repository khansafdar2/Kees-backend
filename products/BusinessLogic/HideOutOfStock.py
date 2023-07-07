
from products.models import Variant


def hide_stock(product, order_cancel=False):
    if product.hide_out_of_stock:
        variants = Variant.objects.filter(product=product, deleted=False)
        check_quantity = [True if variant.inventory_quantity == 0 else False for variant in variants]
        if all(check_quantity):
            product.is_hidden = True
            product.save()
        else:
            product.is_hidden = False
            product.save()
    else:
        product.is_hidden = False
        product.save()
