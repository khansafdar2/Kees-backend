
import datetime
import json
import random
import requests
import re

from django.conf import settings
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

        success_url = f"{settings.HOST_URL}/paymentgateway/qissat_pay_process_request"
        failure_url = f"{settings.HOST_URL}/paymentgateway/qissat_pay_process_request"
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
        transaction_number = (str(random.randint(1000, 1000000)) + '-' + current_date.strftime("%Y-%m-%dT%H-%M-%S")).\
            replace('-', '')


        try:
            gateway_credentials = GatewayCredentials.objects.filter(gateway_name='QisstPay',
                                                                    is_active=True).first()
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

            if gateway_credentials.test_mode:
                gateway_url = "https://sandbox.qisstpay.com/api/send-data"
            else:
                gateway_url = "https://qisstpay.com/api/send-data"

            header = {
                'Authorization': 'Basic ' + password,
                'Content-Type': 'application/json'
            }
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
                stripe_secret_key=password,
            )

            payload = {
                "partner_id": "shopify",
                "fname": customer.first_name,
                "mname": "",
                "lname": customer.last_name,
                "email": checkout.email,
                "phone_no": customer_phone,
                "ip_addr": "3.216.133.205",
                "shipping_info": {
                    "addr1": customer.address,
                    "addr2": "",
                    "state": customer.city,
                    "city": customer.city,
                    "zip": ""
                },
                "billing_info": {
                    "addr1": customer.address,
                    "addr2": "",
                    "state": customer.city,
                    "city": customer.city,
                    "zip": ""
                },
                "total_amount": amount,
                "shipping_details": {},
                "card_details": {},
                "line_items": {},
                "itemFlag": False,
                "merchant_order_id": transaction_number,
                "call_back_url": settings.HOST + "/qisstpay_response?transaction_id="+transaction_number,
                "redirect_url": settings.HOST + "/qisstpay_response?transaction_id="+transaction_number
            }

            response = requests.post(gateway_url, headers=header, data=json.dumps(payload))
            if response.status_code == 200:
                try:
                    json_response = json.loads(response.text)
                except Exception as e:
                    print(e)
                    data = {
                        "error": str(response.content),
                        "cancel_url": failure_url
                    }
                    return render(request, 'error_page.html', data)
                print(json_response)

                if json_response['success'] == True:
                    redirect_url = json_response['result']['iframe_url']
                    return redirect(redirect_url)
                else:
                    print(response.text)
                    print(response.content)
                    data = {
                        "error": response.content,
                        "cancel_url": failure_url
                    }
                    return render(request, 'error_page.html', data)
            else:
                json_response = json.loads(response.text)
                if json_response['message'] is None:
                    data = {
                        "error": "Invalid Request",
                        "cancel_url": failure_url
                    }
                    return render(request, 'error_page.html', data)
                else:
                    data = {
                        "error": json_response['message'],
                        "cancel_url": failure_url
                    }
                    return render(request, 'error_page.html', data)

        except Exception as e:
            print(e)
            return redirect(failure_url)
    else:
        return redirect("https://www.google.com")


# @csrf_exempt
def response(request):
    txn_ref_no = request.GET.get('transaction_id')

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
