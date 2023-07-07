import datetime

from crm.models import Customer
from order.models import Order
from setting.models import LoyaltySetting, Rule


def calculate_points(customer_id, total_no_of_order, total_spending_amount, latest_order_amount, order_status):
    total_spending_amount = float(total_spending_amount)
    latest_order_amount = float(latest_order_amount)

    customer = Customer.objects.get(id=customer_id, deleted=False)
    setting = LoyaltySetting.objects.filter(deleted=False).first()
    rules = Rule.objects.filter(deleted=False, is_active=True)

    start_loyalty_amount = float(setting.start_loyalty_amount)
    amount_equal_point = float(setting.amount_equal_point)

    #  Check Paid Orders
    if setting.is_paid:
        if order_status != 'Paid':
            return customer.points

    # Setting Points Calculation
    points = 0.00
    is_given = False
    if total_spending_amount >= start_loyalty_amount:
        amount_greater_spending = total_spending_amount - start_loyalty_amount
        is_given = True
        if amount_greater_spending >= latest_order_amount:
            points = latest_order_amount / amount_equal_point
        else:
            points = amount_greater_spending / amount_equal_point

    if total_no_of_order > setting.minimum_orders_loyalty_start:
        if not is_given:
            points = latest_order_amount / amount_equal_point

    # Rule Points Calculation
    for rule in rules:
        rules = list(set(Customer.objects.filter(id=customer.id, deleted=False).values_list('rule', flat='True')))
        if rule.type == 'amount':
            if rule.id not in rules:
                if rule.spending_amount <= total_spending_amount and rule.start_date is None:
                    points += float(rule.no_of_point)
                    customer.rule.add(rule.id)
                    customer.save()

                if rule.start_date and rule.end_date:
                    start_date = str(rule.start_date)[:16]
                    end_date = str(rule.end_date)[:16]

                    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M')
                    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M')

                    orders = Order.objects.filter(created_at__range=[start_date, end_date], customer_id=customer_id)
                    total_orders = orders.count()
                    total_price = 0.00
                    for order in orders:
                        total_price += float(order.total_price)

                    if total_price >= rule.spending_amount:
                        points += float(rule.no_of_point)
                        customer.rule.add(rule.id)
                        customer.save()

        if rule.type == 'order':
            if rule.no_of_order == total_no_of_order and rule.start_date is None:
                points += float(rule.no_of_point)

            if rule.start_date and rule.end_date:
                start_date = str(rule.start_date)
                end_date = str(rule.end_date)

                orders = Order.objects.filter(created_at__range=[start_date, end_date], customer_id=customer_id)
                total_orders = orders.count()
                total_price = 0.00
                for order in orders:
                    total_price += float(order.total_price)

                if total_orders == int(rule.no_of_order):
                    points += float(rule.no_of_point)

    customer.points = float(customer.points) + float(points)
    customer.save()
