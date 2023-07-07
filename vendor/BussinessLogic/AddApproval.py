
import inspect
from vendor.models import DataApproval
from products.models import Product, ProductGroup, Collection
from shipping.models import Shipping
from discount.models import Discount


def check_approval(vendor, instance):
    if instance.__class__.__name__ == 'Product':
        if vendor.product_approval:
            return True
    elif instance.__class__.__name__ is 'ProductGroup':
        if vendor.product_group_approval:
            return True
    elif instance.__class__.__name__ is 'Collection':
        if vendor.collection_approval:
            return True
    elif instance.__class__.__name__ is 'Shipping':
        if vendor.shipping_approval:
            return True
    elif instance.__class__.__name__ is 'Discount':
        if vendor.discount_approval:
            return True
    return False


def add_approval_entry(title, vendor, instance):
    # get user
    user = None
    for frame_record in inspect.stack():
        if frame_record[3] == 'get_response':
            request = frame_record[0].f_locals['request']
            user = request.user
            break

    if user:
        if user.is_vendor:
            if vendor.is_approval:
                if check_approval(vendor, instance):
                    content_data = {
                        'title': title,
                        'content_object': instance,
                        'status': 'Pending',
                        'vendor': vendor
                    }

                    DataApproval.objects.create(**content_data)

                    instance.status = 'Pending'
                    instance.save()
                else:
                    instance.status = 'Approved'
                    instance.save()
            else:
                instance.status = 'Approved'
                instance.save()
        else:
            instance.status = 'Approved'
            instance.save()
