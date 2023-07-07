
from products.models import Product, CategoryHandle, Variant, Media
from django.conf import settings


def productslider(handle):
    products_list = []
    category_handle = CategoryHandle.objects.filter(name=handle).first()
    category_type = category_handle.category_type

    if category_type == 'main_category':
        if handle == 'deals-of-the-month':
            products = Product.objects.filter(collection__main_category__handle=handle, is_active=True, deleted=False)
        else:
            products = Product.objects.filter(collection__main_category__handle=handle,
                                              collection__main_category__is_active=True,
                                              collection__main_category__deleted=False,
                                              is_active=True,
                                              deleted=False
                                              ).order_by('-id').distinct()[0:10]
    elif category_type == 'sub_category':
        products = Product.objects.filter(collection__sub_category__handle=handle,
                                          collection__sub_category__is_active=True,
                                          collection__sub_category__deleted=False,
                                          is_active=True,
                                          deleted=False).order_by('-id').distinct()[0:10]
    elif category_type == 'super_sub_category':
        products = Product.objects.filter(collection__super_sub_category__handle=handle,
                                          collection__super_sub_category__is_active=True,
                                          collection__super_sub_category__deleted=False,
                                          is_active=True,
                                          deleted=False).order_by('-id').distinct()[0:10]
    else:
        products = None

    if products is not None:
        for product in products:
            variant = Variant.objects.filter(product=product, deleted=False).first()
            image = Media.objects.filter(product=product, position=1).first()
            if image is not None:
                optimize_image = image.cdn_link
                # optimize_image = optimize_image.replace(settings.AWS_BASE_URL, settings.IMAGEKIT_URL)
                optimize_image = optimize_image.replace('+', ' ')
                # optimize_image = optimize_image.replace('%26', '&')
                # optimize_image = optimize_image.replace('%20', ' ')
                # optimize_image = optimize_image+'?tr=w-400'
            else:
                optimize_image = None

            product_data = {
                "image": optimize_image,
                "title": product.title,
                "handle": product.handle,
                "price": {
                    "original_price": variant.price,
                    "compare_price": variant.compare_at_price
                }
            }
            products_list.append(product_data)

    return products_list
