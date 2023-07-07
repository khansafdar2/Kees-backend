
from discount.models import Discount
from setting.models import StoreInformation
from rest_framework import exceptions
from datetime import datetime
import pytz


def discount_status_change():
    store_information = StoreInformation.objects.filter(deleted=False).first()
    if not store_information:
        raise exceptions.ParseError('Please save store information first')
    if not store_information.time_zone:
        raise exceptions.ParseError('Please save time zone in store information first')

    today = datetime.now(pytz.timezone(store_information.time_zone))
    today = today.replace(tzinfo=None)
    # utc = pytz.UTC
    # today = utc.localize(today)

    discounts = Discount.objects.filter(start_date__isnull=False, end_date__isnull=False, deleted=False)

    for discount in discounts:
        print(discount)
        if discount.start_date <= today < discount.end_date:
            discount.is_active = True
            discount.save()
        elif today > discount.end_date:
            discount.is_active = False
            discount.save()
        else:
            break
