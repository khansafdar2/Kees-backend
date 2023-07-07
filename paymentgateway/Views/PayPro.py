
import datetime
import json
import random
import requests
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from setting.models import StoreInformation
from order.models import Checkout, ShippingAddress
from paymentgateway.models import GatewayCredentials, PaymentTransactions


@csrf_exempt
def index(request):
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
        transaction_number = (str(random.randint(1000, 1000000)) + '-' + current_date.strftime("%Y-%m-%dT%H-%M-%S")).\
            replace('-', '')

        try:
            gateway_credentials = GatewayCredentials.objects.filter(gateway_name='PayPro',
                                                                    is_active=True).first()
            if not gateway_credentials:
                return redirect(failure_url)

            if gateway_credentials.test_mode:
                html_url = "https://demoapi.paypro.com.pk/cpay/co"
                gateway_credentials = gateway_credentials.credentials["test"]
            else:
                html_url = "https://api.paypro.com.pk/cpay/co"
                gateway_credentials = gateway_credentials.credentials["live"]

            merchant_id = gateway_credentials["Merchant ID"]
            password = gateway_credentials["Password"]

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
                test_mode=gateway_credentials.test_mode)

            current_time = datetime.datetime.now()
            order_amount = round(float(payment_transaction.order_amount))
            url_params = [
                {
                    "MerchantId": merchant_id,
                    "MerchantPassword": password
                },
                {
                    "OrderNumber": transaction_number,
                    "OrderAmount": order_amount,
                    "OrderDueDate": current_time.strftime('%d/%m/%Y'),
                    "OrderAmountWithinDueDate": order_amount,
                    "OrderAmountAfterDueDate": order_amount,
                    "OrderTypeId": "Service",
                    "OrderType": "Service",
                    "IssueDate": current_time.strftime('%d/%m/%Y'),
                    "TransactionStatus": "UNPAID",
                    "CustomerName": payment_transaction.x_customer_first_name,
                    "CustomerMobile": customer_phone,
                    "CustomerEmail": checkout.email,
                    "CustomerAddress": customer.address,
                    "CustomerBank": "",
                    "Ecommerce_return_url": settings.HOST_URL + "/paypro_listener_response?transaction_number" + transaction_number + "/"
                }
            ]

            order_request_url = html_url + "?oJson=" + str(url_params)

            order_request = requests.post(order_request_url)
            order_response_in_json = json.loads(order_request.text)

            if order_response_in_json[0]["Status"] == "00":
                payment_transaction.request_status = order_response_in_json[0]["Status"]
                payment_transaction.fetch_order_type = order_response_in_json[1]["FetchOrderType"]
                payment_transaction.click_2Pay = order_response_in_json[1]["Click2Pay"]
                payment_transaction.description = order_response_in_json[1]["Description"]
                payment_transaction.connect_pay_id = order_response_in_json[1]["ConnectPayId"]
                payment_transaction.order_number = order_response_in_json[1]["OrderNumber"]
                payment_transaction.order_amount = order_response_in_json[1]["OrderAmount"]
                payment_transaction.is_fee_applied = order_response_in_json[1]["IsFeeApplied"]
                payment_transaction.connect_pay_fee = order_response_in_json[1]["ConnectPayFee"]
                payment_transaction.save()

                redirect_url = order_response_in_json[1]["Click2Pay"] + "&callback_url=" + settings.HOST_URL +"/paymentgateway/paypro_response?transaction_number=" + transaction_number
                return redirect(redirect_url)
            else:
                return HttpResponse(str(order_response_in_json))
        except Exception as e:
            print(e)
            return redirect(failure_url)
    else:
        return redirect("https://www.google.com")


def response(request):
    transaction_number = request.GET.get('transaction_number')

    try:
        payment_transaction = PaymentTransactions.objects.get(txn_ref_no=transaction_number)
    except Exception as e:
        print("Exception in Pay Pro RESPONSE " + str(e))
        return redirect(f"{settings.STOREFRONT_URL}/checkout?error=Some Error Occured in retrieving transaction")

    payload = {
        'checkout_id': payment_transaction.checkout_id
    }

    headers = {
        "Content-Type": "application/json",
        'User-agent': 'Gecko/20100101 Firefox/12.0 Mozilla/5.0'
    }

    payload = json.dumps(payload)
    request_response = requests.post(payment_transaction.x_url_callback, data=payload, headers=headers)

    order_id = (request_response.json())['order_id']

    if request_response.status_code == 200:
        payment_transaction.transaction_id = request.GET.get('transaction_id')
        payment_transaction.transaction_status = "Success"
        payment_transaction.save()
        return redirect(f"{payment_transaction.complete_url}/{order_id}")
    elif request_response.status_code == 422:
        payment_transaction.response_message = "Order placement failed!"
        payment_transaction.transaction_status = "Failed"
        payment_transaction.save()
        return redirect(f"{payment_transaction.cancel_url}?error={payment_transaction.response_message}")

    payment_transaction.transaction_status = "Failed"
    payment_transaction.save()
    return redirect(f"{payment_transaction.cancel_url}?error={payment_transaction.response_message}")


def listener_response(request):
    transaction_number = request.GET.get('transaction_number')
    try:
        payment_transaction = PaymentTransactions.objects.get(txn_ref_no=transaction_number)
    except Exception as e:
        print("Exception in Pay Pro RESPONSE " + str(e))
        return redirect(f"{settings.STOREFRONT_URL}/checkout?error=Some Error Occured in retrieving transaction")

    payment_transaction.transaction_status = "Failed"
    payment_transaction.save()
    return redirect(f"{payment_transaction.x_url_cancel}?error={payment_transaction.response_message}")
