
from order.models import OrderHistory


def create_orderhistory(order=None, childorder=None, message=None):
    order_history = OrderHistory(order=order, child_order=childorder, message=message)
    order_history.save()

