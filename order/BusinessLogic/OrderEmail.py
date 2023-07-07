
from order.models import LineItems, ShippingAddress, BillingAddress
from products.models import Product, Variant, Media
from crm.models import Customer
from authentication.BusinessLogic.EmailSender import send_email, email_templates


def orderemail(order, email_heading, description, email_subject, bcc_email=None):
    customer = Customer.objects.filter(order_customer=order, deleted=False).first()
    shipping_address = ShippingAddress.objects.filter(order=order, deleted=False).first()
    billing_address = BillingAddress.objects.filter(order=order, deleted=False).first()
    line_items = LineItems.objects.filter(order=order, deleted=False)

    product_list = ''''''
    for line_item in line_items:
        variant = Variant.objects.filter(id=line_item.variant.id).first()
        product = Product.objects.filter(product_variant=variant.id, deleted=False).first()
        image = Media.objects.filter(product=product, deleted=False).first()

        # email products
        if variant.title == 'Default Title':
            variant_title = ''
        else:
            variant_title = variant.title

        if image:
            image = image.cdn_link
        else:
            image = None

        data = f'''<div style="width: 100%;display: flex;justify-content: space-between;" class=" product-summary ">
              <div style="width: 60%; float: left;">
              <table>
                <tr>
                  <td><img class=" order-summary-img " alt="product_img" src="{image}" style="width: 85px;margin-right: 20px;"></td>
                  <td>
                    <p style="color: #555; font-weight: bold; margin: 5px 0;">{product.title} × {line_item.quantity}</p>
                    <p style="color: grey;">{variant_title}</p>
                  </td>
                </tr>
              </table>
            </div>
              <div class=" price " style="width: 40%; float: left; color: #555;font-weight: bold;font-size: 18px;"><p style="text-align: center;">QAR. {line_item.total_price}</p></div>
            </div>
            <hr>'''

        product_list += data

    if shipping_address is not None:
        shipping_address_name = f"{shipping_address.first_name} {shipping_address.last_name}"
        shipping_address_address = shipping_address.address
        shipping_address_city = shipping_address.city
        shipping_address_country = shipping_address.country
    else:
        shipping_address_name = ''
        shipping_address_address = ''
        shipping_address_city = ''
        shipping_address_country = ''

    if billing_address is not None:
        billing_address_name = f"{billing_address.first_name} {billing_address.last_name}"
        billing_address_address = billing_address.address
        billing_address_city = billing_address.city
        billing_address_country = billing_address.country
    else:
        billing_address_name = ''
        billing_address_address = ''
        billing_address_city = ''
        billing_address_country = ''

    try:
        # Send Email
        email_content = {
            'order_number': order.order_id,
            'customer_name': customer.first_name + ' ' + customer.last_name,
            'order_heading': email_heading,
            'description': f"Hi {customer.first_name} {customer.last_name}, {description}",

            'subtotal': str(order.subtotal_price),
            'shipping': str(order.total_shipping),
            'total_price': str(order.total_price),
            'payment_method': order.payment_method,

            'shipping_address_name': shipping_address_name,
            'shipping_address_address': shipping_address_address,
            'shipping_address_city': shipping_address_city,
            'shipping_address_country': shipping_address_country,

            'billing_address_name': billing_address_name,
            'billing_address_address': billing_address_address,
            'billing_address_city': billing_address_city,
            'billing_address_country': billing_address_country,

            'product_list': product_list
        }

        if customer.email is not None:
            email_template = email_templates(template_name='order', email_content=email_content)

            send_email(
                to_email=customer.email,
                email_subject=email_subject,
                email_template=email_template
            )

    except Exception as e:
        print(e)