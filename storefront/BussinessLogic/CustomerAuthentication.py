
from rest_framework import exceptions
from crm.models import Customer
from datetime import datetime, timedelta


def token_authentication(token):
    auth = str(token)
    if auth is None:
        raise exceptions.ParseError("Auth token is required for this api", code=404)
    else:
        customer = Customer.objects.filter(token=auth).first()
        if not customer:
            raise exceptions.ParseError("Invalid auth token", code=401)
        else:
            if customer.last_login < datetime.now() - timedelta(hours=6):
                raise exceptions.ParseError("Session Expired, Please login your account", code=408)
            return customer
