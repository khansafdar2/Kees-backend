
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests, random, json
from datetime import datetime
from order.models import Checkout, ShippingAddress
from django.conf import settings
from setting.models import StoreInformation
from paymentgateway.models import GatewayCredentials, PaymentTransactions


@csrf_exempt
def pay2m_view(request):
    try:
        store = StoreInformation.objects.get(deleted=False)
    except Exception as e:
        print(e)
        return HttpResponse('Store not exist')

    success_url = f"{settings.HOST_URL}/paymentgateway/process_request"
    failure_url = f"{settings.HOST_URL}/paymentgateway/process_request"
    checkout_url = f"{settings.HOST_URL}/paymentgateway/process_request"
    order_place_url = f"{settings.HOST_URL}/order/place_order"
    complete_url = f"{settings.STOREFRONT_URL}/thankyou"

    checkout_id = request.GET.get('checkout_id')
    if not checkout_id:
        return redirect(failure_url)
    else:
        checkout = Checkout.objects.filter(checkout_id=checkout_id).first()

    gateway_credentials = GatewayCredentials.objects.filter(gateway_name='pay2m', brand_name=store.store_name, is_active=True).first()
    if not gateway_credentials:
        return redirect(failure_url)

    current_date = datetime.now()
    transaction_number = (str(random.randint(1000, 1000000)) + '-' + current_date.strftime("%Y-%m-%dT%H-%M-%S")).replace('-', '')

    amount = f"{float(checkout.subtotal_price) + float(checkout.total_shipping)}"
    merchant_name = gateway_credentials.brand_name

    if gateway_credentials.test_mode:
        token_url = "https://payments.pay2m.com/Ecommerce/api/Transaction/GetAccessToken"
        gateway_url = "https://payments.pay2m.com/Ecommerce/api/Transaction/PostTransaction"
        gateway_credentials_json = gateway_credentials.credentials['test']
    else:
        token_url = "https://pay.pay2m.com/Ecommerce/api/Transaction/GetAccessToken"
        gateway_url = "https://pay.pay2m.com/Ecommerce/api/Transaction/PostTransaction"
        gateway_credentials_json = gateway_credentials.credentials['live']

    get_token = {
        "MERCHANT_ID": gateway_credentials_json['MERCHANT_ID'],
        "SECURED_KEY": gateway_credentials_json['SECURED_KEY']
    }

    headers = {
        "Content-Type": "application/json",
        'User-agent': 'Gecko/20100101 Firefox/12.0 Mozilla/5.0'
    }

    data = json.dumps(get_token)
    response = requests.post(token_url, data=data, headers=headers)
    if response.status_code == 200:
        response_json = response.json()
        token = response_json['ACCESS_TOKEN']
        order_date = current_date.strftime("%Y-%m-%d")

        customer = ShippingAddress.objects.filter(checkout__checkout_id=checkout_id).first()
        PaymentTransactions.objects.create(checkout_id=checkout_id,
                                           customer_first_name=customer.first_name,
                                           customer_last_name=customer.last_name,
                                           callback_url=order_place_url,
                                           cancel_url=failure_url,
                                           complete_url=complete_url,
                                           access_token=token,
                                           currency=store.store_currency,
                                           signature="",
                                           order_amount=amount,
                                           txn_ref_no=transaction_number,
                                           test_mode=gateway_credentials.test_mode)

        context = {
            "gateway_url": gateway_url,
            "MERCHANT_ID": gateway_credentials_json['MERCHANT_ID'],
            "MERCHANT_NAME": merchant_name,
            "TOKEN": token,
            "PROCCODE": "00",
            "TXNAMT": amount,
            "CUSTOMER_MOBILE_NO": checkout.phone,
            "CUSTOMER_EMAIL_ADDRESS": checkout.email,
            "SIGNATURE": "",
            "VERSION": "MY_VER_1.0",
            "TXNDESC": "",
            "SUCCESS_URL": success_url,
            "FAILURE_URL": failure_url,
            "BASKET_ID": transaction_number,
            "ORDER_DATE": order_date,
            "CHECKOUT_URL": checkout_url
        }

        return render(request, settings.PAY2M_TEMPLATE, context)


@csrf_exempt
def process_request(request):
    err_code = request.GET.get('err_code')
    txn_ref_no = request.GET.get('basket_id')

    try:
        transaction = PaymentTransactions.objects.get(txn_ref_no=txn_ref_no)
    except Exception as e:
        print("Exception in retrieving transaction: " + str(e))
        return redirect(f"{settings.STOREFRONT_URL}/checkout?error=Some Error Occured in retrieving transaction")

    if err_code == '000':
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
            transaction.response_code = err_code
            transaction.response_message = request.GET.get('err_msg')
            transaction.transaction_id = request.GET.get('transaction_id')
            transaction.response_status = "Success"
            transaction.save()
            return redirect(f"{transaction.complete_url}/{order_id}")
        elif response.status_code == 422:
            transaction.response_code = err_code
            transaction.response_message = request.GET.get('err_msg')
            transaction.response_status = "Failed"
            transaction.save()
            return redirect(f"{transaction.cancel_url}?error={transaction.response_message}")

    transaction.err_code = err_code
    transaction.response_message = request.GET.get('err_msg')
    transaction.response_status = "Failed"
    transaction.save()
    return redirect(f"{transaction.cancel_url}?error={transaction.response_message}")


