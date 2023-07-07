
import datetime
import random
import requests
import stripe
import json
from django.http import HttpResponse
from django.conf import settings
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

        success_url = f"{settings.HOST_URL}/paymentgateway/stripe_success_request"
        failure_url = f"{settings.HOST_URL}/paymentgateway/stripe_failed_request"
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
        transaction_number = (str(random.randint(1000, 1000000)) + '-' + current_date.strftime("%Y-%m-%dT%H-%M-%S")). \
            replace('-', '')

        try:
            gateway_credentials = GatewayCredentials.objects.filter(gateway_name='Stripe', is_active=True).first()
            if not gateway_credentials:
                return redirect(failure_url)

            if gateway_credentials.test_mode:
                stripe_publishable_key = gateway_credentials.credentials["test"]["Published Key"]
                stripe_secret_key = gateway_credentials.credentials["test"]["Secret Key"]
            else:
                stripe_publishable_key = gateway_credentials.credentials["live"]["Published Key"]
                stripe_secret_key = gateway_credentials.credentials["live"]["Secret Key"]

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
                txn_ref_no=transaction_number,
                test_mode=gateway_credentials.test_mode,
                stripe_publishable_key=stripe_publishable_key,
                stripe_secret_key=stripe_secret_key,
            )

            stripe.api_key = stripe_secret_key
            checkout_session = stripe.checkout.Session.create(
                customer_email=checkout.email,
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': store.store_currency,
                            'product_data': {
                                'name': 'test',
                            },
                            'unit_amount': int(float(amount)*100),
                        },
                        'quantity': 1,
                    }
                ],
                mode='payment',
                success_url=settings.HOST_URL + "/paymentgateway/stripe_success_request?session_id={CHECKOUT_SESSION_ID}&txn_ref_no=" + transaction_number,
                cancel_url=settings.HOST_URL + "/paymentgateway/stripe_failed_request?session_id={CHECKOUT_SESSION_ID}&txn_ref_no=" + transaction_number,
            )
            payment_transaction.stripe_payment_intent = checkout_session['payment_intent']
            payment_transaction.stripe_session_id = checkout_session.id
            payment_transaction.save()
            return redirect(checkout_session.url)
        except Exception as e:
            print(e)
            return redirect(failure_url)
    else:
        return redirect("https://www.google.com")


def success_response(request):
    session_id = request.GET.get('session_id')
    txn_ref_no = request.GET.get('txn_ref_no')
    if session_id is None:
        print("Stripe Session not Found")

    try:
        payment_transaction = PaymentTransactions.objects.get(txn_ref_no=txn_ref_no)
    except Exception as e:
        print("Exception in Stripe RESPONSE " + str(e))
        return redirect(f"{settings.STOREFRONT_URL}/checkout?error=Some Error Occured in retrieving transaction")

    stripe.api_key = payment_transaction.stripe_secret_key
    session = stripe.checkout.Session.retrieve(session_id)

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

    order_id = (response.json())['order_id']

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

    payment_transaction.transaction_status = "Failed"
    payment_transaction.save()
    return redirect(f"{payment_transaction.cancel_url}?error={payment_transaction.response_message}")


def failed_response(request):
    session_id = request.GET.get('session_id')
    txn_ref_no = request.GET.get('txn_ref_no')
    if session_id is None:
        print("Stripe Session not Found")

    try:
        payment_transaction = PaymentTransactions.objects.get(txn_ref_no=txn_ref_no)
    except Exception as e:
        print("Exception in Stripe RESPONSE " + str(e))
        return redirect(f"{settings.STOREFRONT_URL}/checkout?error=Some Error Occured in retrieving transaction")

    stripe.api_key = payment_transaction.stripe_secret_key
    session = stripe.checkout.Session.retrieve(session_id)

    payment_transaction.response_code = "422"
    payment_transaction.response_description = "Order Not Placed in Shopify"
    payment_transaction.save()
    return redirect(payment_transaction.cancel_url)
