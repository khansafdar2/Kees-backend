
import datetime
import json
import random
import requests
from django.conf import settings as setting
from django.http import HttpResponse
from django.shortcuts import render, redirect
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

        success_url = f"{setting.HOST_URL}/paymentgateway/mcb_process_request"
        failure_url = f"{setting.HOST_URL}/paymentgateway/mcb_process_request"
        order_place_url = f"{setting.HOST_URL}/order/place_order"
        complete_url = f"{setting.STOREFRONT_URL}/thankyou"

        checkout_id = request.GET.get('checkout_id')
        if not checkout_id:
            return redirect(failure_url)
        else:
            checkout = Checkout.objects.filter(checkout_id=checkout_id).first()

        # order amount
        amount = f"{float(checkout.subtotal_price) + float(checkout.total_shipping)}"

        current_date = datetime.datetime.now()
        transaction_number = (str(random.randint(1000, 1000000)) + '-' + current_date.strftime("%Y-%m-%dT%H-%M-%S")).\
            replace('-', '')

        try:
            gateway_credentials = GatewayCredentials.objects.filter(gateway_name='MCB', is_active=True).first()
            if not gateway_credentials:
                return redirect(failure_url)

            if gateway_credentials.test_mode:
                merchant_id = gateway_credentials.credentials["test"]["MERCHANT_ID"]
                password = gateway_credentials.credentials["test"]["password"]
                api_username = gateway_credentials.credentials["test"]["api_username"]
            else:
                merchant_id = gateway_credentials.credentials["live"]["MERCHANT_ID"]
                password = gateway_credentials.credentials["live"]["password"]
                api_username = gateway_credentials.credentials["live"]["api_username"]

            payload = {
                'apiOperation': 'CREATE_CHECKOUT_SESSION',
                'order': {
                    'amount': amount,
                    'currency': store.store_currency,
                    'description': "",
                    'id': transaction_number
                }
            }

            if gateway_credentials.test_mode:
                url = "https://test-mcbpk.mtf.gateway.mastercard.com"
                html_url = "https://test-mcbpk.mtf.gateway.mastercard.com/checkout/version/49/checkout.js"
            else:
                url = "https://mcbpk.gateway.mastercard.com"
                html_url = "https://mcbpk.gateway.mastercard.com/checkout/version/49/checkout.js"

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
                order_currency=store.store_currency,
                signature="",
                order_amount=amount,
                txn_ref_no=transaction_number,
                test_mode=gateway_credentials.test_mode)

            logo = 'https://d109eq6v2p18ca.cloudfront.net/products/product_images/keeslogoooo.svg'
            context_data = {
                'session_id': data['session']['id'],
                'payment': payment_transaction,
                'customer': customer,
                'merchant': gateway_credentials,
                'order_id': transaction_number,
                'html_url': html_url,
                'host_url': success_url,
                'date': datetime.datetime.today().strftime('%Y-%m-%d'),
                'merchant_id': merchant_id,
                'client_logo': logo,
                'email': checkout.email
            }

            return render(request, 'mcb.html', context_data)
        except Exception as e:
            print(e)
            return redirect(failure_url)
    else:
        return redirect("https://www.google.com")


# @csrf_exempt
def mcb_response(request):
    transaction_id = request.GET.get('transaction_id')

    try:
        mcb_transaction = PaymentTransactions.objects.get(txn_ref_no=transaction_id)
    except Exception as e:
        print("Exception in BAF RESPONSE " + str(e))
        return redirect(f"{setting.STOREFRONT_URL}/checkout?error=Some Error Occured in retrieving transaction")

    gateway_credentials = GatewayCredentials.objects.filter(gateway_name='BAF', is_active=True).first()

    if mcb_transaction.test_mode:
        url = "https://test-mcbpk.mtf.gateway.mastercard.com"
        gateway_credentials = gateway_credentials.credentials['test']
    else:
        url = "https://mcbpk.gateway.mastercard.com"
        gateway_credentials = gateway_credentials.credentials['live']

    merchant_id = gateway_credentials["MERCHANT_ID"]
    password = gateway_credentials["password"]
    api_username = gateway_credentials["api_username"]

    gateway_url = url + "/api/rest/version/49/merchant/" + merchant_id + "/order/" + transaction_id
    response = requests.get(gateway_url, auth=(api_username, password))
    result_hash = response.json()

    if result_hash["result"] == "SUCCESS" and result_hash["status"] == "CAPTURED":
        mcb_transaction.card_band = result_hash["sourceOfFunds"]["provided"]["card"]["brand"]
        mcb_transaction.card_expiry_month = result_hash["sourceOfFunds"]["provided"]["card"]["expiry"]["month"]
        mcb_transaction.card_expiry_year = result_hash["sourceOfFunds"]["provided"]["card"]["expiry"]["year"]
        mcb_transaction.card_funding_method = result_hash["sourceOfFunds"]["provided"]["card"]["fundingMethod"]
        mcb_transaction.card_name_on_card = result_hash["sourceOfFunds"]["provided"]["card"]["nameOnCard"]
        mcb_transaction.card_number = result_hash["sourceOfFunds"]["provided"]["card"]["number"]
        mcb_transaction.card_scheme = result_hash["sourceOfFunds"]["provided"]["card"]["scheme"]
        mcb_transaction.fund_type = result_hash["sourceOfFunds"]["type"]
        mcb_transaction.payment_status = result_hash["status"]
        mcb_transaction.total_authorized_amount = result_hash["totalAuthorizedAmount"]
        mcb_transaction.total_captured_amount = result_hash["totalCapturedAmount"]
        mcb_transaction.total_refunded_amount = result_hash["totalRefundedAmount"]
        mcb_transaction.save()

        if result_hash["transaction"] is not None:
            if result_hash["transaction"][0] is not None:
                mcb_transaction.order_amount = result_hash["transaction"][0]["order"]["amount"]
                mcb_transaction.save()

        payload = {
            'checkout_id': mcb_transaction.checkout_id
        }

        headers = {
            "Content-Type": "application/json",
            'User-agent': 'Gecko/20100101 Firefox/12.0 Mozilla/5.0'
        }

        payload = json.dumps(payload)
        response = requests.post(mcb_transaction.callback_url, data=payload, headers=headers)

        order_id = (response.json())['order_id']

        if response.status_code == 200:
            mcb_transaction.response_code = result_hash["result"]
            mcb_transaction.transaction_id = request.GET.get('transaction_id')
            mcb_transaction.transaction_status = "Success"
            mcb_transaction.save()
            return redirect(f"{mcb_transaction.complete_url}/{order_id}")
        elif response.status_code == 422:
            mcb_transaction.response_code = result_hash["result"]
            mcb_transaction.response_message = "Order placement failed!"
            mcb_transaction.transaction_status = "Failed"
            mcb_transaction.save()
            return redirect(f"{mcb_transaction.cancel_url}?error={mcb_transaction.response_message}")

    mcb_transaction.response_code = result_hash["result"]
    mcb_transaction.response_message = request.GET.get('err_msg')
    mcb_transaction.transaction_status = "Failed"
    mcb_transaction.save()
    return redirect(f"{mcb_transaction.cancel_url}?error={mcb_transaction.response_message}")
