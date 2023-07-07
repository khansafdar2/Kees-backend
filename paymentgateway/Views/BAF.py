
import datetime
import json
import random
import requests
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from order.models import Checkout, ShippingAddress
from paymentgateway.models import GatewayCredentials, PaymentTransactions
from setting.models import StoreInformation


@csrf_exempt
def baf_view(request):
    if request.method == 'GET':
        try:
            store = StoreInformation.objects.get(deleted=False)
        except Exception as e:
            print(e)
            return HttpResponse('Store does not exist')

        success_url = f"{settings.HOST_URL}/paymentgateway/baf_process_request"
        failure_url = f"{settings.HOST_URL}/paymentgateway/baf_process_request"
        order_place_url = f"{settings.HOST_URL}/order/place_order"
        complete_url = f"{settings.STOREFRONT_URL}/thankyou"

        checkout_id = request.GET.get('checkout_id')
        if not checkout_id:
            return redirect(failure_url)
        else:
            checkout = Checkout.objects.filter(checkout_id=checkout_id).first()

        # order amount
        amount = f"{float(checkout.subtotal_price) + float(checkout.total_shipping)}"

        current_date = datetime.datetime.now()
        txn_ref_no = (str(random.randint(1000, 1000000)) + '-' + current_date.strftime("%Y-%m-%dT%H-%M-%S")).\
            replace('-', '')

        try:
            gateway_credentials = GatewayCredentials.objects.filter(gateway_name='BAF',
                                                                    is_active=True).first()
            if not gateway_credentials:
                return redirect(failure_url)

            if gateway_credentials.test_mode:
                url = "https://test-bankalfalah.gateway.mastercard.com"
                html_url = "https://test-bankalfalah.gateway.mastercard.com/checkout/version/49/checkout.js"
                credentials = gateway_credentials.credentials["test"]
            else:
                url = "https://bankalfalah.gateway.mastercard.com"
                html_url = "https://bankalfalah.gateway.mastercard.com/checkout/version/49/checkout.js"
                credentials = gateway_credentials.credentials["live"]

            merchant_id = credentials["MERCHANT_ID"]
            password = credentials["password"]
            api_username = credentials["api_username"]

            payload = {
                'apiOperation': 'CREATE_CHECKOUT_SESSION',
                'order': {
                    'amount': amount,
                    'currency': store.store_currency,
                    'description': "test phase",
                    'id': txn_ref_no
                }
            }

            response = requests.post(
                url + "/api/rest/version/49/merchant/" + merchant_id + "/session",
                auth=(api_username, password), json=payload)
            data = response.json()

            customer = ShippingAddress.objects.filter(checkout__checkout_id=checkout_id).first()
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
                txn_ref_no=txn_ref_no,
                test_mode=gateway_credentials.test_mode
            )

            context_data = {
                'session_id': data['session']['id'],
                'payment': payment_transaction,
                'customer': customer,
                'merchant': gateway_credentials,
                'order_id': txn_ref_no,
                'html_url': html_url,
                'host_url': success_url,
                'merchant_id': merchant_id,
                'client_logo': '',
                'email': checkout.email
            }
            return render(request, 'baf.html', context_data)
        except Exception as e:
            print(e)
            return redirect(failure_url)
    else:
        return redirect("https://www.google.com")


def baf_response(request):
    txn_ref_no = request.GET.get('transaction_id')

    try:
        bank_alfalah_transaction = PaymentTransactions.objects.get(txn_ref_no=txn_ref_no)
    except Exception as e:
        print("Exception in BAF RESPONSE " + str(e))
        return redirect(f"{settings.STOREFRONT_URL}/checkout?error=Some Error Occured in retrieving transaction")

    gateway_credentials = GatewayCredentials.objects.filter(gateway_name='BAF', is_active=True).first()
    if bank_alfalah_transaction.test_mode:
        url = "https://test-bankalfalah.gateway.mastercard.com"
    else:
        url = "https://bankalfalah.gateway.mastercard.com"

    if gateway_credentials.test_mode:
        merchant_id = gateway_credentials.credentials["test"]["MERCHANT_ID"]
        password = gateway_credentials.credentials["test"]["password"]
        api_username = gateway_credentials.credentials["test"]["api_username"]
    else:
        merchant_id = gateway_credentials.credentials["live"]["MERCHANT_ID"]
        password = gateway_credentials.credentials["live"]["password"]
        api_username = gateway_credentials.credentials["live"]["api_username"]

    gateway_url = url + "/api/rest/version/49/merchant/" + merchant_id + "/order/" + txn_ref_no
    response = requests.get(gateway_url, auth=(api_username, password))
    result_hash = response.json()

    if result_hash["result"] == "SUCCESS" and result_hash["status"] == "AUTHORIZED":
        bank_alfalah_transaction.card_band = result_hash["sourceOfFunds"]["provided"]["card"]["brand"]
        bank_alfalah_transaction.card_expiry_month = result_hash["sourceOfFunds"]["provided"]["card"]["expiry"]["month"]
        bank_alfalah_transaction.card_expiry_year = result_hash["sourceOfFunds"]["provided"]["card"]["expiry"]["year"]
        bank_alfalah_transaction.card_funding_method = result_hash["sourceOfFunds"]["provided"]["card"]["fundingMethod"]
        bank_alfalah_transaction.card_name_on_card = result_hash["sourceOfFunds"]["provided"]["card"]["nameOnCard"]
        bank_alfalah_transaction.card_number = result_hash["sourceOfFunds"]["provided"]["card"]["number"]
        bank_alfalah_transaction.card_scheme = result_hash["sourceOfFunds"]["provided"]["card"]["scheme"]
        bank_alfalah_transaction.fund_type = result_hash["sourceOfFunds"]["type"]
        bank_alfalah_transaction.payment_status = result_hash["status"]
        bank_alfalah_transaction.total_authorized_amount = result_hash["totalAuthorizedAmount"]
        bank_alfalah_transaction.total_captured_amount = result_hash["totalCapturedAmount"]
        bank_alfalah_transaction.total_refunded_amount = result_hash["totalRefundedAmount"]
        bank_alfalah_transaction.save()

        if result_hash["transaction"] is not None:
            if result_hash["transaction"][0] is not None:
                bank_alfalah_transaction.order_amount = result_hash["transaction"][0]["order"]["amount"]
                bank_alfalah_transaction.save()

        payload = {
            'checkout_id': bank_alfalah_transaction.checkout_id
        }

        headers = {
            "Content-Type": "application/json",
            'User-agent': 'Gecko/20100101 Firefox/12.0 Mozilla/5.0'
        }

        payload = json.dumps(payload)
        response = requests.post(bank_alfalah_transaction.callback_url, data=payload, headers=headers)

        order_id = (response.json())['order_id']

        if response.status_code == 200:
            bank_alfalah_transaction.response_code = result_hash["result"]
            bank_alfalah_transaction.transaction_id = request.GET.get('transaction_id')
            bank_alfalah_transaction.response_code = "Success"
            bank_alfalah_transaction.save()
            return redirect(f"{bank_alfalah_transaction.complete_url}/{order_id}")
        elif response.status_code == 422:
            bank_alfalah_transaction.response_code = result_hash["result"]
            bank_alfalah_transaction.response_message = "Order placement failed!"
            bank_alfalah_transaction.response_status = "Failed"
            bank_alfalah_transaction.save()
            return redirect(f"{bank_alfalah_transaction.cancel_url}?error={bank_alfalah_transaction.response_message}")

    bank_alfalah_transaction.response_code = result_hash["result"]
    bank_alfalah_transaction.response_message = request.GET.get('err_msg')
    bank_alfalah_transaction.response_status = "Failed"
    bank_alfalah_transaction.save()
    return redirect(f"{bank_alfalah_transaction.cancel_url}?error={bank_alfalah_transaction.response_message}")
