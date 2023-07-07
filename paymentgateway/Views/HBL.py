
import json
import datetime
import random
import re

import requests
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

import setting
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
            gateway_credentials = GatewayCredentials.objects.filter(gateway_name='HBL', is_active=True).first()
            if not gateway_credentials:
                return redirect(failure_url)

            if gateway_credentials.test_mode:
                    secret_key = gateway_credentials.credentials["test"]["secret_key"],
                    profile_id = gateway_credentials.credentials["test"]["profile_id"],
                    access_key = gateway_credentials.credentials["test"]["access_key"],

            else:
                    secret_key = gateway_credentials.credentials["live"]["secret_key"],
                    profile_id = gateway_credentials.credentials["live"]["profile_id"],
                    access_key = gateway_credentials.credentials["live"]["access_key"]

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
                test_mode=gateway_credentials.test_mode
            )
            locale = 'en'
            transaction_type = 'sale'
            reference_number = transaction_number
            amount = amount
            currency = "PKR"
            merchant_defined_data1 = "WC"
            merchant_defined_data2 = "YES"
            merchant_defined_data3 = "Test"
            merchant_defined_data4 = "Default"
            merchant_defined_data5 = "YES"
            merchant_defined_data6 = "Standard"
            merchant_defined_data7 = "NO"
            merchant_defined_data8 = "Pakistan"
            merchant_defined_data20 = "NO"

            payload = {
                'access_key': access_key,
                'transaction_uuid': transaction_number,
                'signed_date_time': current_date,
                'locale': locale,
                'transaction_type': transaction_type,
                'reference_number': reference_number,
                'amount': amount,
                'currency': currency,
                'bill_to_address_city': customer.city,
                'bill_to_address_country': customer.country,
                'bill_to_address_line1': customer.address,
                'bill_to_address_line2': customer.address,
                'bill_to_address_postal_code': customer.postal_code,
                'bill_to_address_state': customer.country,
                'bill_to_company_name': 'KEES',
                'bill_to_email': checkout.email,
                'bill_to_forename': customer.first_name,
                'bill_to_surname': customer.last_name,
                'bill_to_phone': customer_phone,
                'ship_to_address_city': customer.city,
                'ship_to_address_country': customer.country,
                'ship_to_address_line1': customer.address,
                'ship_to_address_postal_code': customer.postal_code,
                'ship_to_address_state': customer.address,
                'ship_to_forename': customer.first_name,
                'ship_to_phone': customer_phone,
                'ship_to_surname': customer.last_name,
                'ship_to_email': customer.email,
                'customer_ip_address': 'test ip',
                'line_item_count': '1',
                'consumer_id': reference_number,
                'merchant_defined_data1': merchant_defined_data1,
                'merchant_defined_data2': merchant_defined_data2,
                'merchant_defined_data3': merchant_defined_data3,
                'merchant_defined_data4': merchant_defined_data4,
                'merchant_defined_data5': merchant_defined_data5,
                'merchant_defined_data6': merchant_defined_data6,
                'merchant_defined_data7': merchant_defined_data7,
                'merchant_defined_data8': merchant_defined_data8,
                'merchant_defined_data20': merchant_defined_data20,
                'unsigned_field_names': "",
            }
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
