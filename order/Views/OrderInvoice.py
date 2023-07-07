
from django.http import HttpResponse
from django.views.generic import View
from rest_framework.views import APIView
from order.BusinessLogic.PdfRender import render_to_pdf
from order.models import Order, LineItems, ShippingAddress
from products.models import Variant, Product, Media
from crm.models import Customer, Address


class Invoice(View):
    def get(self, request):
        order_id = request.GET.get('order_id', None)

        order = Order.objects.filter(id=order_id).first()
        customer = Customer.objects.filter(order_customer=order, deleted=False).first()
        customer_address = ShippingAddress.objects.filter(order=order).first()
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
                image = image.replace(" ", "%20")
            else:
                image = None

            if line_item.price != line_item.compare_at_price:
                discount = int(line_item.compare_at_price) - int(line_item.price)
                discount = discount * int(line_item.quantity)
            else:
                discount = 0

            base_price = int(line_item.compare_at_price)
            sub_price = base_price * int(line_item.quantity)

            products = f'''<tr style="text-align: center; font-size: 14px; border-bottom: 1px solid lightgrey; ">
                            <td style="text-align:center; padding: 8px 0 3px 0;"><img style=" max-width: 90px;" src="{image}" alt="product_image"></td>
                            <td style="text-align:center; padding: 8px 0 3px 0;"><p>{product.title}</p></td>
                            <td style="padding: 8px 0 3px 0;"><p>{variant.sku}</p></td>
                            <td style="padding: 8px 0 3px 0;"><p>{line_item.quantity}</p></td>
                            <td style="padding: 8px 0 3px 0;"><p>{base_price}</p></td>
                            <td style="padding: 8px 0 3px 0;"><p>{sub_price}</p></td>
                            <td style="padding: 8px 0 3px 0;"><p>{discount}</p></td>
                            <td style="padding: 8px 0 3px 0;"><p>{sub_price-discount} <span>QAR</span></p></td>
                        </tr>'''
            product_list += products

        customer_phone = ['' if not customer.phone else customer.phone]
        customer_email = ['' if not customer.email else customer.email]

        if customer_address.apartment is None:
            apartment = ''
        else:
            apartment = customer_address.apartment + ' '

        invoice_content = {
            'order_number': order.order_id,
            'customer_name': customer.first_name + ' ' + customer.last_name,
            'customer_phone': customer_address.phone,
            'customer_email': customer_email[0],
            'customer_address': apartment + customer_address.address,

            'subtotal': order.subtotal_price,
            'shipping': order.total_shipping,
            'total_price': order.total_price,
            'date': str(order.created_at)[0:10],

            'shipping_address': order.total_shipping,
            'paid_amount': order.paid_amount,

            'product_list': product_list
        }

        pdf = render_to_pdf(invoice_content)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "Invoice.pdf"
            content = "inline; filename='%s'" % filename
            download = request.GET.get("download")
            if download:
                content = "attachment; filename='%s'" % filename
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")
