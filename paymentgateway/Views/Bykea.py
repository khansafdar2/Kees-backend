
import json
import datetime
import random
import re
import requests
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from order.models import Checkout, ShippingAddress
from paymentgateway.models import GatewayCredentials, PaymentTransactions
from setting.models import StoreInformation


@csrf_exempt
def index(request):
    if request.method == 'GET':
        try:
            store = StoreInformation.objects.get(deleted=False)
        except Exception as e:
            print(e)
            return HttpResponse('Store does not exist')

        success_url = f"{settings.HOST_URL}/paymentgateway/bykea_success_request"
        failure_url = f"{settings.HOST_URL}/paymentgateway/bykea_failure_request"
        order_place_url = f"{settings.HOST_URL}/order/place_order"
        complete_url = f"{settings.STOREFRONT_URL}/thankyou"
        bykea_base_url = "https://invoice.bykea.cash"

        checkout_id = request.GET.get('checkout_id')
        if not checkout_id:
            return redirect(failure_url)
        else:
            checkout = Checkout.objects.filter(checkout_id=checkout_id).first()

        # order amount
        amount = f"{float(checkout.subtotal_price) + float(checkout.total_shipping)}"

        current_date = datetime.datetime.now()
        transaction_number = (str(random.randint(1000, 1000000)) + '-' + current_date.strftime("%Y-%m-%dT%H-%M-%S")). \
            replace('-', '')

        try:
            gateway_credentials = GatewayCredentials.objects.filter(gateway_name='Bykea', is_active=True).first()
            if not gateway_credentials:
                return redirect(failure_url)

            if gateway_credentials.test_mode:
                headers = {
                    "username": gateway_credentials.credentials["test"]["Username"],
                    "password": gateway_credentials.credentials["test"]["Password"]
                }
            else:
                headers = {
                    "username": gateway_credentials.credentials["live"]["Username"],
                    "password": gateway_credentials.credentials["live"]["Password"]
                }

            secret_key_response = requests.get(bykea_base_url + "/open/api/customer/auth", headers=headers)
            parse_response = json.loads(secret_key_response.text)
            bykea_secret_key = parse_response['secret']

            customer = ShippingAddress.objects.filter(checkout__checkout_id=checkout_id).first()
            customer_phone = customer.phone.replace(" ", "")

            try:
                phone_validation = re.match(r'/^(0)-{0,1}\d{3}-{0,1}\d{7}$|^\d{11}$|^\d{4}-\d{7}$', customer_phone)
                if phone_validation is None:
                    customer_phone = ""
            except Exception as e:
                print(e)
                customer_phone = ""

            if customer_phone[:1] == "+" and len(customer_phone) == 13:
                customer_phone = customer_phone[3:]
                customer_phone = "0" + customer_phone
            elif len(customer_phone) == 14 and customer_phone[:4] == "0092":
                customer_phone = customer_phone[4:]
                customer_phone = "0" + customer_phone
            elif len(customer_phone) == 14 and customer_phone[:4] == "0+92":
                customer_phone = customer_phone[4:]
                customer_phone = "0" + customer_phone
            elif len(customer_phone) == 10 and customer_phone[:1] == "3":
                customer_phone = "0" + customer_phone

            payment_transaction = PaymentTransactions.objects.create(
                checkout_id=checkout_id,
                customer_first_name=customer.first_name,
                customer_last_name=customer.last_name,
                callback_url=order_place_url,
                cancel_url=failure_url,
                complete_url=complete_url,
                currency=store.store_currency,
                signature="",
                order_amount=amount,
                txn_ref_no=transaction_number,
                test_mode=gateway_credentials.test_mode,
                stripe_secret_key=bykea_secret_key,
            )
            customer_phone = '032112345223'
            payload = {
                "name": payment_transaction.customer_first_name + " " + payment_transaction.customer_last_name,
                "phone": customer_phone,
                "amount": payment_transaction.order_amount,
                "amount_type": "PKR",
                "return_url": settings.HOST_URL + "/bykea_success_request?transaction_id" + payment_transaction.txn_ref_no,
                "cancel_url": settings.HOST_URL + "/bykea_failure_request?transaction_id" + payment_transaction.txn_ref_no,
                "order": transaction_number,
                "detail": {
                    "notes": 'Ecommerce',
                    "image": "https://ps.w.org/bykea-cash-online-payments/assets/icon-256x256.png"
                },
                "from": {
                    "mobile": customer_phone,
                    "business": 'Ecommerce',
                    "email": checkout.email,
                    "reference": "Fees Id:" + transaction_number
                }
            }

            request_header = {
                "secret": bykea_secret_key,
                "Content-Type": "application/json",
                "Accept": "application/json"
            }

            invoice_response = requests.post(bykea_base_url + "/open/api/invoice/create", headers=request_header,
                                             data=json.dumps(payload))

            if invoice_response.status_code == 200:
                parse_response = json.loads(invoice_response.text)
                print(parse_response)
                if parse_response['subcode'] == "10001":
                    payment_transaction.invoice_reference = parse_response['reference']
                    payment_transaction.invoice_no = parse_response['invoice_no']
                    payment_transaction.invoice_url = parse_response['invoice_url']
                    payment_transaction.save()
                    return redirect(payment_transaction.invoice_url)
                else:
                    return HttpResponse("Exception in Bykea RESPONSE " + str(parse_response['data']['error']))
            else:
                return redirect(failure_url)
        except Exception as e:
            print(e)
            return redirect(failure_url)
    else:
        return redirect("https://www.google.com")


def success_response(self, request):
    txn_ref_no = self.request.GET.get('transaction_id')

    try:
        payment_transaction = PaymentTransactions.objects.get(txn_ref_no=txn_ref_no)
    except Exception as e:
        print("Exception in Bykea RESPONSE " + str(e))
        return redirect(f"{settings.STOREFRONT_URL}/checkout?error=Some Error Occured in retrieving transaction")

    payment_transaction.response_code = "200"

    payload = {
        'checkout_id': payment_transaction.checkout_id
    }

    headers = {
        "Content-Type": "application/json",
        'User-agent': 'Gecko/20100101 Firefox/12.0 Mozilla/5.0'
    }

    payload = json.dumps(payload)
    response = requests.post(payment_transaction.callback_url, data=payload, headers=headers)

    order_id = (response.json())['transaction_id']

    if response.status_code == 200:
        payment_transaction.transaction_id = request.GET.get('transaction_id')
        payment_transaction.transaction_status = "Success"
        payment_transaction.save()
        return redirect(f"{payment_transaction.complete_url}/{order_id}")
    elif response.status_code == 422:
        payment_transaction.response_message = "Order placement failed!"
        payment_transaction.transaction_status = "Failed"
        payment_transaction.save()
        return redirect(f"{payment_transaction.cancel_url}?error={payment_transaction.response_message}")


def failed_response(self, request):
    txn_ref_no = self.request.GET.get('transaction_id')

    try:
        payment_transaction = PaymentTransactions.objects.get(txn_ref_no=txn_ref_no)
    except Exception as e:
        print("Exception in Bykea RESPONSE " + str(e))
        return redirect(f"{settings.STOREFRONT_URL}/checkout?error=Some Error Occured in retrieving transaction")

    payment_transaction.response_code = "422"
    payment_transaction.response_message = "Order Not Placed"
    payment_transaction.save()
    return redirect(payment_transaction.cancel_url)
