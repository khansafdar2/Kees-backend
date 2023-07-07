import datetime
import hashlib
import hmac
import json
import random
import requests
import urllib.parse

from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from order.models import Checkout, ShippingAddress
from paymentgateway.BusinessLogic.UBL.Finalization import Finalization
from paymentgateway.models import GatewayCredentials, PaymentTransactions
from paymentgateway.BusinessLogic.UBL.GenerateSession import GenerateSession
from setting.models import StoreInformation


@csrf_exempt
def index(request):
    if request.method == 'GET':
        try:
            store = StoreInformation.objects.get(deleted=False)
        except Exception as e:
            print(e)
            return HttpResponse('Store does not exist')

        success_url = f"{settings.HOST_URL}/paymentgateway/ubl_response"
        failure_url = f"{settings.HOST_URL}/paymentgateway/ubl_response"
        x_url_complete = f"{settings.STOREFRONT_URL}/thankyou"

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
        transaction_number = transaction_number[:16]
        print(len(transaction_number))
        order_place_url = f"{settings.HOST_URL}/order/place_order"
        try:
            gateway_credentials = GatewayCredentials.objects.filter(gateway_name='UBL', is_active=True).first()

            if not gateway_credentials:
                return redirect(failure_url)

            if gateway_credentials.test_mode:
                url = "https://demo-ipg.ctdev.comtrust.ae:2443"
            else:
                url = "https://ipg.comtrust.ae:2443"
            if gateway_credentials.is_active:
                if gateway_credentials.test_mode:
                    username = gateway_credentials.credentials["Username"]
                    password = gateway_credentials.credentials["Password"]
                    customer_data = gateway_credentials.credentials["Customer Data"]
                else:
                    username = gateway_credentials.credentials["Username"]
                    password = gateway_credentials.credentials["Password"]
                    customer_data = gateway_credentials.credentials["Customer Data"]

                success = "Success"
                GS = GenerateSession()

                if gateway_credentials.certificatePath is not None:
                    response = GS.withCertificate(gateway_credentials, 'PKR', transaction_number, url,
                                                  amount)
                else:
                    response = GS.withOutCertificate(gateway_credentials, 'PKR', transaction_number, url,
                                                     amount)

                data = response.json()

                customer = ShippingAddress.objects.filter(checkout__checkout_id=checkout_id).first()

                print(data)

                payment_transaction = PaymentTransactions.objects.create(
                    checkout_id=checkout_id,
                    customer_first_name=customer.first_name,
                    customer_last_name=customer.last_name,
                    callback_url=order_place_url,
                    cancel_url=failure_url,
                    complete_url=x_url_complete,
                    currency=store.store_currency,
                    signature="",
                    order_amount=amount,
                    txn_ref_no=transaction_number,
                    test_mode=gateway_credentials.test_mode,
                )

                context = {'action': data['Transaction']['PaymentPortal'],
                           'TransactionID': data['Transaction']['TransactionID']}

                return render(request, 'ubl.html', context)

            else:
                return redirect(failure_url)
        except Exception as e:
            print(e)
            return redirect(failure_url)
    else:
        return redirect("https://www.google.com")


@csrf_exempt
def response(request):
    txn_ref_no = request.POST["TransactionID"]

    try:
        transaction = PaymentTransactions.objects.get(txn_ref_no=txn_ref_no)
    except Exception as e:
        print("Exception in retrieving transaction: " + str(e))
        return redirect(f"{settings.STOREFRONT_URL}/checkout?error=Some Error Occured in retrieving transaction")

    payload = {
            'checkout_id': transaction.checkout_id
        }

    headers = {
            "Content-Type": "application/json",
            'User-agent': 'Gecko/20100101 Firefox/12.0 Mozilla/5.0'
        }

    payload = json.dumps(payload)
    response = requests.post(transaction.callback_url, data=payload, headers=headers)

    order_id = (response.json())['order_id']

    if response.status_code == 200:
        transaction.response_code = response.status_code
        transaction.response_message = request.GET.get('err_msg')
        transaction.response_status = "Success"
        transaction.save()
        return redirect(f"{transaction.complete_url}/{order_id}")
    elif response.status_code == 422:
        transaction.response_code = response.status_code
        transaction.response_status = "Failed"
        transaction.save()
        return redirect(f"{transaction.cancel_url}?error={transaction.response_message}")

    transaction.err_code = response.status_code
    transaction.response_status = "Failed"
    transaction.save()
    return redirect(f"{transaction.cancel_url}?error={transaction.response_message}")
