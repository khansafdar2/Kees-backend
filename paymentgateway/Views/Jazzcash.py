
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests, random, json
from datetime import datetime
from datetime import timedelta
from order.models import Checkout, ShippingAddress
from ecomm_app.settings import staging as setting
from setting.models import StoreInformation
from paymentgateway.models import GatewayCredentials, PaymentTransactions


@csrf_exempt
def jazzcash_view(request):
    try:
        store = StoreInformation.objects.get(deleted=False)
    except Exception as e:
        print(e)
        return HttpResponse('Store not exist')

    success_url = f"{setting.HOST_URL}/paymentgateway/jazzcash_process_request"
    failure_url = f"{setting.HOST_URL}/paymentgateway/jazzcash_process_request"
    order_place_url = f"{setting.HOST_URL}/order/place_order"
    complete_url = f"{setting.STOREFRONT_URL}/thankyou"

    checkout_id = request.GET.get('checkout_id')
    if not checkout_id:
        return redirect(failure_url)
    else:
        checkout = Checkout.objects.filter(checkout_id=checkout_id).first()

    gateway_credentials = GatewayCredentials.objects.filter(gateway_name='jazzcash', brand_name=store.store_name, is_active=True).first()
    if not gateway_credentials:
        return redirect(failure_url)

    if gateway_credentials.test_mode:
        gateway_url = "https://sandbox.jazzcash.com.pk/CustomerPortal/transactionmanagement/merchantform"
        gateway_credentials = gateway_credentials.credentials['test']
    else:
        gateway_url = "https://payments.jazzcash.com.pk/CustomerPortal/transactionmanagement/merchantform"
        gateway_credentials = gateway_credentials.credentials['live']

    is_discount = gateway_credentials['IS_DISCOUNT']
    discount_type = gateway_credentials['DISCOUNT_TYPE']
    discount_value = gateway_credentials['DISCOUNT_VALUE']
    merchant_id = gateway_credentials['MERCHANT_ID']
    merchant_password = gateway_credentials['MERCHANT_PASSWORD']

    current_time = datetime.now()
    txn_ref_no = (str(random.randint(1000, 1000000)) + '-' + current_time.strftime("%Y-%m-%dT%H-%M-%S")).replace('-', '')

    amount = float(checkout.subtotal_price) + float(checkout.total_shipping)

    if is_discount:
        if discount_type == "Percentage":
            amount = float(amount * discount_value)/100.0
        elif amount > discount_value:
            amount = amount - float(discount_value)

    amount = round(float(amount))
    expiry_time = current_time + timedelta(days=5)

    customer = ShippingAddress.objects.filter(checkout__checkout_id=checkout_id).first()
    PaymentTransactions.objects.create(checkout_id=checkout_id,
                                       customer_first_name=customer.first_name,
                                       customer_last_name=customer.last_name,
                                       callback_url=order_place_url,
                                       cancel_url=failure_url,
                                       complete_url=complete_url,
                                       is_discount=is_discount,
                                       discount_type=discount_type,
                                       discount_value=discount_value,
                                       currency=store.store_currency,
                                       signature="",
                                       order_amount=amount,
                                       txn_ref_no=txn_ref_no,
                                       expiry_time=expiry_time,
                                       test_mode=gateway_credentials.test_mode)

    context = {
        "pp_MerchantID": merchant_id,
        "pp_Password": merchant_password,
        "pp_TxnRefNo": txn_ref_no,
        "pp_Amount": str(amount),
        "pp_TxnDateTime": current_time.strftime("%Y%m%d%H%M%S"),
        "pp_TxnExpiryDateTime": expiry_time.strftime("%Y%m%d%H%M%S"),
        "pp_BillReference": str(txn_ref_no),
        "pp_Description": "Goods",
        "gateway_url": gateway_url,
        "callback_url": success_url,
    }

    return render(request, 'jazz_cash_request.html', context)


@csrf_exempt
def jazzcash_process_request(request):
    txn_ref_no = request.GET.get('pp_BillReference')

    try:
        transaction = PaymentTransactions.objects.get(txn_ref_no=txn_ref_no)
    except Exception as e:
        print("Exception in retrieving transaction: " + str(e))
        return redirect(f"{setting.STOREFRONT_URL}/checkout?error=Some Error Occured in retrieving transaction")

    transaction.response_code = request.GET.get('pp_ResponseCode')
    transaction.response_message = request.GET.get('response_message')
    transaction.save()

    if transaction.response_message == 'Transaction Cancelled by User.':
        return redirect(f"{transaction.cancel_url}?error={transaction.response_message}")
    elif transaction.response_code == "000" or transaction.response_code == "121" or transaction.response_code == "200":
        transaction.transaction_status = "Success"
        transaction.save()

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
            transaction.order_status = 200
            transaction.save()
            return redirect(f"{transaction.complete_url}/{order_id}")
        elif response.status_code == 422:
            transaction.order_status = 200
            transaction.save()
            return redirect(f"{transaction.cancel_url}?error={transaction.response_message}")
