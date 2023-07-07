from datetime import datetime
from operator import itemgetter
from django.db.models import Sum, F, FloatField
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.BusinessLogic.ActivityStream import SystemLogs
from authentication.BusinessLogic.ApiPermissions import AccessApi
from rest_framework import exceptions
from order.models import Order, ChildOrder, LineItems, ChildOrderLineItems, ShippingAddress
from products.models import Variant, Product, Collection, ProductGroup, MainCategory, SubCategory, SuperSubCategory
from vendor.models import Vendor


class Revenue(APIView):
    def get(self, request):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "dashboard")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to this Api")

            vendor_id = self.request.GET.get('vendor_id', None)
            if vendor_id:
                vendor_id = int(vendor_id)
            start_date = self.request.GET.get('start_date', None)
            end_date = self.request.GET.get('end_date', None)

            if start_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')

            if end_date:
                end_date = datetime.strptime(f"{end_date} 23:59:59", '%Y-%m-%d %H:%M:%S')

            if self.request.user.is_vendor:
                vendor_id = self.request.user.vendor_id

            dic = dict()
            inventory_dic = dict()
            if vendor_id is not None:
                dic['child_order__vendor_id'] = vendor_id
                inventory_dic['vendor_id'] = vendor_id

            if start_date and end_date:
                total_orders_list = ChildOrderLineItems.objects. \
                    filter(**dic, child_order__order__created_at__gte=start_date,
                           child_order__order__created_at__lte=end_date, deleted=False)
                total_sale = total_orders_list.aggregate(
                    total_sale=Sum(F('price') * F('quantity') + F('shipping_amount'), output_field=FloatField()))
                canceled_orders = total_orders_list.filter(child_order__order__order_status='Cancelled')
                canceled_orders_sum = canceled_orders.aggregate(
                    total_cancelled=Sum(F('price') * F('quantity') + F('shipping_amount'), output_field=FloatField()))

                if total_sale['total_sale']:
                    total_sale_value = total_sale['total_sale']
                else:
                    total_sale_value = 0

                if canceled_orders_sum['total_cancelled']:
                    canceled_orders_sum_value = canceled_orders_sum['total_cancelled']
                else:
                    canceled_orders_sum_value = 0

                net_sale = total_sale_value - canceled_orders_sum_value
                all_products = Product.objects.filter(**inventory_dic)
                all_variant = Variant.objects.filter(product__in=all_products)
                inventory_size = all_variant.aggregate(Sum('inventory_quantity'))
            else:
                total_orders_list = ChildOrderLineItems.objects.filter(**dic, deleted=False)
                total_sale = total_orders_list.aggregate(
                    total_sale=Sum(F('price') * F('quantity') + F('shipping_amount'), output_field=FloatField()))
                canceled_orders = total_orders_list.filter(child_order__order__order_status='Cancelled')
                canceled_orders_sum = canceled_orders.aggregate(
                    total_cancelled=Sum(F('price') * F('quantity') + F('shipping_amount'), output_field=FloatField()))

                if total_sale['total_sale']:
                    total_sale_value = total_sale['total_sale']
                else:
                    total_sale_value = 0

                if canceled_orders_sum['total_cancelled']:
                    canceled_orders_sum_value = canceled_orders_sum['total_cancelled']
                else:
                    canceled_orders_sum_value = 0

                net_sale = total_sale_value - canceled_orders_sum_value
                all_products = Product.objects.filter(**inventory_dic)
                all_variant = Variant.objects.filter(product__in=all_products)
                inventory_size = all_variant.aggregate(Sum('inventory_quantity'))

            if not total_sale['total_sale']:
                total_sale = 0
            else:
                total_sale = total_sale['total_sale']

            if not inventory_size['inventory_quantity__sum']:
                inventory_size = 0
            else:
                inventory_size = inventory_size['inventory_quantity__sum']

            data = {
                'total_sale': total_sale,
                'net_sale': net_sale,
                'inventory_size': inventory_size,
            }

            # Post Entry in Logs
            action_performed = self.request.user.username + " Seen the dashboard"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            return Response(data, status=200)

        except Exception as e:
            print(e)
            return Response({'detail': str(e)}, status=422)


class OrderAnalysis(APIView):
    def get(self, request):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "dashboard")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to this Api")

            vendor_id = self.request.GET.get('vendor_id', None)
            if vendor_id:
                vendor_id = int(vendor_id)
            start_date = self.request.GET.get('start_date', None)
            end_date = self.request.GET.get('end_date', None)

            if start_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                # start_date = start_date.strftime('%Y-%m-%d %H:%M:%S.%f')
                # start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S.%f')

            if end_date:
                end_date = datetime.strptime(f"{end_date} 23:59:59", '%Y-%m-%d %H:%M:%S')
                # end_date = end_date.strftime('%Y-%m-%d %H:%M:%S.%f')
                # end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S.%f')

            if self.request.user.is_vendor:
                vendor_id = self.request.user.vendor_id

            if not vendor_id:

                if start_date and end_date:
                    total_orders_list = Order.objects.filter(created_at__gte=start_date, created_at__lte=end_date)
                    total_sale = total_orders_list.aggregate(Sum('total_price'))
                    total_orders = 0

                    if total_orders_list:
                        total_orders = total_orders_list.count()

                    canceled_orders_count = 0
                    returned_orders_count = 0
                    canceled_orders = total_orders_list.filter(order_status='Cancelled')

                    if canceled_orders:
                        canceled_orders_count = canceled_orders.count()

                    returned_orders = total_orders_list.filter(order_status='Returned')

                    if returned_orders:
                        returned_orders_count = returned_orders.count()

                    all_line_items = LineItems.objects.filter(order__in=total_orders_list)
                    all_line_items_count = 0

                    if all_line_items:
                        for item in all_line_items:
                            if item.quantity != 1 and item.quantity != 0:
                                all_line_items_count += item.quantity
                            all_line_items_count += 1

                    average_basket_size = 0

                    if all_line_items_count != 0 and total_orders != 0:
                        average_basket_size = all_line_items_count / total_orders

                    if total_sale['total_price__sum']:
                        total_sale_value = total_sale['total_price__sum']
                    else:
                        total_sale_value = 0

                    average_basket_value = 0

                    if total_sale_value != 0 and total_orders != 0:
                        average_basket_value = total_sale_value / total_orders
                else:
                    total_orders_list = Order.objects.all()
                    total_sale = total_orders_list.aggregate(Sum('total_price'))
                    total_orders = 0

                    if total_orders_list:
                        total_orders = total_orders_list.count()

                    canceled_orders_count = 0
                    returned_orders_count = 0
                    canceled_orders = total_orders_list.filter(order_status='Cancelled')

                    if canceled_orders:
                        canceled_orders_count = canceled_orders.count()

                    returned_orders = total_orders_list.filter(order_status='Returned')

                    if returned_orders:
                        returned_orders_count = returned_orders.count()

                    all_line_items = LineItems.objects.all()
                    all_line_items_count = 0

                    if all_line_items:
                        for item in all_line_items:
                            if item.quantity != 1 and item.quantity != 0:
                                all_line_items_count += item.quantity
                            all_line_items_count += 1

                    average_basket_size = 0

                    if all_line_items_count != 0 and total_orders != 0:
                        average_basket_size = all_line_items_count / total_orders

                    if total_sale['total_price__sum']:
                        total_sale_value = total_sale['total_price__sum']
                    else:
                        total_sale_value = 0

                    average_basket_value = 0

                    if total_sale_value != 0 and total_orders != 0:
                        average_basket_value = total_sale_value / total_orders

            if vendor_id:
                if start_date and end_date:
                    total_orders_list = ChildOrder.objects.filter(vendor_id=vendor_id, created_at__gte=start_date,
                                                                  created_at__lte=end_date)
                    total_sale = total_orders_list.aggregate(Sum('total_price'))
                    total_orders = 0

                    if total_orders_list:
                        total_orders = total_orders_list.count()

                    canceled_orders_count = 0
                    returned_orders_count = 0
                    canceled_orders = total_orders_list.filter(order_status='Cancelled')

                    if canceled_orders:
                        canceled_orders_count = canceled_orders.count()

                    returned_orders = total_orders_list.filter(order_status='Returned')

                    if returned_orders:
                        returned_orders_count = returned_orders.count()

                    all_line_items = ChildOrderLineItems.objects.filter(child_order__in=total_orders_list)
                    all_line_items_count = 0

                    if all_line_items:
                        for item in all_line_items:
                            if item.quantity != 1 and item.quantity != 0:
                                all_line_items_count += item.quantity
                            all_line_items_count += 1

                    average_basket_size = 0

                    if all_line_items_count != 0 and total_orders != 0:
                        average_basket_size = all_line_items_count / total_orders

                    if total_sale['total_price__sum']:
                        total_sale_value = total_sale['total_price__sum']
                    else:
                        total_sale_value = 0

                    average_basket_value = 0

                    if total_sale_value != 0 and total_orders != 0:
                        average_basket_value = total_sale_value / total_orders
                else:
                    total_orders_list = ChildOrder.objects.filter(vendor_id=vendor_id)
                    total_sale = total_orders_list.aggregate(Sum('total_price'))
                    total_orders = 0

                    if total_orders_list:
                        total_orders = total_orders_list.count()

                    canceled_orders_count = 0
                    returned_orders_count = 0
                    canceled_orders = total_orders_list.filter(order_status='Cancelled')

                    if canceled_orders:
                        canceled_orders_count = canceled_orders.count()

                    returned_orders = total_orders_list.filter(order_status='Returned')

                    if returned_orders:
                        returned_orders_count = returned_orders.count()

                    all_line_items = ChildOrderLineItems.objects.filter(child_order__in=total_orders_list)
                    all_line_items_count = 0

                    if all_line_items:
                        for item in all_line_items:
                            if item.quantity != 1 and item.quantity != 0:
                                all_line_items_count += item.quantity
                            all_line_items_count += 1

                    average_basket_size = 0

                    if all_line_items_count != 0 and total_orders != 0:
                        average_basket_size = all_line_items_count / total_orders

                    if total_sale['total_price__sum']:
                        total_sale_value = total_sale['total_price__sum']
                    else:
                        total_sale_value = 0

                    average_basket_value = 0

                    if total_sale_value != 0 and total_orders != 0:
                        average_basket_value = total_sale_value / total_orders

            if not total_sale['total_price__sum']:
                total_sale = 0
            else:
                total_sale = total_sale['total_price__sum']

            data = {
                'total_orders': total_orders,
                'canceled_orders_count': canceled_orders_count,
                'returned_orders_count': returned_orders_count,
                'average_basket_size': average_basket_size,
                'average_basket_value': average_basket_value
            }

            # Post Entry in Logs
            action_performed = self.request.user.username + " Seen the dashboard"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            return Response(data, status=200)

        except Exception as e:
            print(e)
            return Response({'detail': str(e)}, status=422)


class ProductAnalysis(APIView):
    def get(self, request):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "dashboard")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to this Api")

            vendor_id = self.request.GET.get('vendor_id', None)
            if vendor_id:
                vendor_id = int(vendor_id)

            if self.request.user.is_vendor:
                vendor_id = self.request.user.vendor_id

            if vendor_id:
                total_vendor_count = 0
                total_collections_count = 0
                total_collections = Collection.objects.filter(vendor_id=vendor_id, deleted=False)

                if total_collections:
                    total_collections_count = total_collections.count()

                total_product_group_count = 0
                total_product_group = ProductGroup.objects.filter(vendor_id=vendor_id, deleted=False)

                if total_product_group:
                    total_product_group_count = total_product_group.count()

                total_products_count = 0
                total_products = Product.objects.filter(vendor_id=vendor_id, deleted=False)

                if total_products:
                    total_products_count = total_products.count()

                total_active_products_count = 0
                total_active_products = total_products.filter(is_active=True)

                if total_active_products:
                    total_active_products_count = total_active_products.count()

                total_inactive_products_count = 0
                total_inactive_products = total_products.filter(is_active=False)

                if total_inactive_products:
                    total_inactive_products_count = total_inactive_products.count()
            else:
                total_vendor_count = 0
                total_vendor = Vendor.objects.filter(is_active=True)

                if total_vendor:
                    total_vendor_count = total_vendor.count()

                total_collections_count = 0
                total_collections = Collection.objects.filter(deleted=False)

                if total_collections:
                    total_collections_count = total_collections.count()

                total_product_group_count = 0
                total_product_group = ProductGroup.objects.filter(deleted=False)

                if total_product_group:
                    total_product_group_count = total_product_group.count()

                total_products_count = 0
                total_products = Product.objects.filter(deleted=False)

                if total_products:
                    total_products_count = total_products.count()

                total_active_products_count = 0
                total_active_products = total_products.filter(is_active=True)

                if total_active_products:
                    total_active_products_count = total_active_products.count()

                total_inactive_products_count = 0
                total_inactive_products = total_products.filter(is_active=False)

                if total_inactive_products:
                    total_inactive_products_count = total_inactive_products.count()

            data = {
                'total_vendor_count': total_vendor_count,
                'total_collections_count': total_collections_count,
                'total_product_group_count': total_product_group_count,
                'total_products_count': total_products_count,
                'total_active_products_count': total_active_products_count,
                'total_inactive_products_count': total_inactive_products_count
            }

            # Post Entry in Logs
            action_performed = self.request.user.username + " Seen the dashboard"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            return Response(data, status=200)

        except Exception as e:
            print(e)
            return Response({'detail': str(e)}, status=422)


class TopSoldItems(APIView):
    def get(self, request):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "dashboard")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to this Api")

            vendor_id = self.request.GET.get('vendor_id', None)
            if vendor_id:
                vendor_id = int(vendor_id)
            start_date = self.request.GET.get('start_date', None)
            end_date = self.request.GET.get('end_date', None)

            if start_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                # start_date = start_date.strftime('%Y-%m-%d %H:%M:%S.%f')
                # start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S.%f')

            if end_date:
                end_date = datetime.strptime(f"{end_date} 23:59:59", '%Y-%m-%d %H:%M:%S')
                # end_date = end_date.strftime('%Y-%m-%d %H:%M:%S.%f')
                # end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S.%f')

            if self.request.user.is_vendor:
                vendor_id = self.request.user.vendor_id

            top_sold_items_list = []

            if not vendor_id:

                if start_date and end_date:
                    total_orders_list = Order.objects.filter(created_at__gte=start_date, created_at__lte=end_date)
                    all_line_items_db = LineItems.objects.filter(order_id__isnull=False).count()
                    all_line_items = LineItems.objects.filter(order__in=total_orders_list)
                    all_line_items_count = 0

                    if all_line_items_db:
                        all_line_items_count = all_line_items_db

                    print(all_line_items_count)
                    variant_ids = all_line_items.filter().values_list('variant_id', flat=True)
                    variant_ids = list(set(variant_ids))
                    if variant_ids:
                        list_of_lineitems = []

                        for variant_id in variant_ids:
                            unique_line_item = {
                                'id': variant_id,
                                'quantity': 0,
                            }

                            for line_item in all_line_items:

                                if variant_id == line_item.variant_id:
                                    unique_line_item['quantity'] += line_item.quantity

                            list_of_lineitems.append(unique_line_item)

                        list_of_lineitems.sort(key=itemgetter('quantity'))
                        list_of_lineitems = list_of_lineitems[-10:]
                        for item in list_of_lineitems:
                            top_sold_items = {
                                'value': 0.00,
                                'name': '',
                                'id': item['id']
                            }
                            quantity = item['quantity']
                            if all_line_items_count != 0:
                                average = (quantity / all_line_items_count) * 100
                                top_sold_items['value'] = average
                            top_sold_items_list.append(top_sold_items)
                        print(top_sold_items_list)
                        for item in top_sold_items_list:
                            variant = Variant.objects.filter(id=item['id']).select_related('product').first()
                            if variant.product:
                                if variant.title != 'Default Title':
                                    item['name'] = variant.product.title + ' ' + variant.title
                                else:
                                    item['name'] = variant.product.title
                else:
                    all_line_items = LineItems.objects.filter(order__isnull=False)  # Do it in all functions
                    all_line_items_count = 0
                    all_line_items_count = all_line_items.count()
                    print(all_line_items_count)
                    variant_ids = all_line_items.filter().values_list('variant_id', flat=True)
                    variant_ids = list(set(variant_ids))
                    if variant_ids:
                        list_of_lineitems = []

                        for variant_id in variant_ids:
                            unique_line_item = {
                                'id': variant_id,
                                'quantity': 0,
                            }

                            for line_item in all_line_items:

                                if variant_id == line_item.variant_id:
                                    unique_line_item['quantity'] += line_item.quantity

                            list_of_lineitems.append(unique_line_item)

                        list_of_lineitems.sort(key=itemgetter('quantity'))
                        list_of_lineitems = list_of_lineitems[-10:]
                        for item in list_of_lineitems:
                            top_sold_items = {
                                'value': 0.00,
                                'name': '',
                                'id': item['id']
                            }
                            quantity = item['quantity']
                            if all_line_items_count != 0:
                                average = (quantity / all_line_items_count) * 100
                                top_sold_items['value'] = average
                            top_sold_items_list.append(top_sold_items)
                        print(top_sold_items_list)
                        for item in top_sold_items_list:
                            variant = Variant.objects.filter(id=item['id']).select_related('product').first()

                            if variant.product:
                                if variant.title != 'Default Title':
                                    item['name'] = variant.product.title + ' ' + variant.title
                                else:
                                    item['name'] = variant.product.title

            if vendor_id:
                if start_date and end_date:
                    total_orders_list = ChildOrder.objects.filter(vendor_id=vendor_id, created_at__gte=start_date,
                                                                  created_at__lte=end_date)
                    all_line_items_db = ChildOrderLineItems.objects.filter(child_order_id__isnull=False).count()
                    all_line_items = ChildOrderLineItems.objects.filter(child_order__in=total_orders_list)
                    all_line_items_count = 0

                    if all_line_items_db:
                        all_line_items_count = all_line_items_db

                    print(all_line_items_count)
                    variant_ids = all_line_items.filter().values_list('variant_id', flat=True)
                    variant_ids = list(set(variant_ids))
                    if variant_ids:
                        list_of_lineitems = []

                        for variant_id in variant_ids:
                            unique_line_item = {
                                'id': variant_id,
                                'quantity': 0,
                            }

                            for line_item in all_line_items:

                                if variant_id == line_item.variant_id:
                                    unique_line_item['quantity'] += line_item.quantity

                            list_of_lineitems.append(unique_line_item)

                        list_of_lineitems.sort(key=itemgetter('quantity'))
                        list_of_lineitems = list_of_lineitems[-10:]
                        for item in list_of_lineitems:
                            top_sold_items = {
                                'value': 0.00,
                                'name': '',
                                'id': item['id']
                            }
                            quantity = item['quantity']
                            if all_line_items_count != 0:
                                average = (quantity / all_line_items_count) * 100
                                top_sold_items['value'] = average
                            top_sold_items_list.append(top_sold_items)
                        print(top_sold_items_list)
                        for item in top_sold_items_list:
                            variant = Variant.objects.filter(id=item['id']).select_related('product').first()
                            if variant.product:
                                if variant.title != 'Default Title':
                                    item['name'] = variant.product.title + ' ' + variant.title
                                else:
                                    item['name'] = variant.product.title
                else:
                    total_orders_list = ChildOrder.objects.filter(vendor_id=vendor_id)
                    all_line_items_db = ChildOrderLineItems.objects.filter(child_order_id__isnull=False).count()
                    all_line_items = ChildOrderLineItems.objects.filter(child_order__in=total_orders_list)
                    all_line_items_count = 0

                    if all_line_items_db:
                        all_line_items_count = all_line_items_db

                    print(all_line_items_count)
                    variant_ids = all_line_items.filter().values_list('variant_id', flat=True)
                    variant_ids = list(set(variant_ids))
                    if variant_ids:
                        list_of_lineitems = []

                        for variant_id in variant_ids:
                            unique_line_item = {
                                'id': variant_id,
                                'quantity': 0,
                            }

                            for line_item in all_line_items:

                                if variant_id == line_item.variant_id:
                                    unique_line_item['quantity'] += line_item.quantity

                            list_of_lineitems.append(unique_line_item)

                        list_of_lineitems.sort(key=itemgetter('quantity'))
                        list_of_lineitems = list_of_lineitems[-10:]
                        for item in list_of_lineitems:
                            top_sold_items = {
                                'value': 0.00,
                                'name': '',
                                'id': item['id']
                            }
                            quantity = item['quantity']
                            if all_line_items_count != 0:
                                average = (quantity / all_line_items_count) * 100
                                top_sold_items['value'] = average
                            top_sold_items_list.append(top_sold_items)
                        print(top_sold_items_list)
                        for item in top_sold_items_list:
                            variant = Variant.objects.filter(id=item['id']).select_related('product').first()
                            if variant.product:
                                if variant.title != 'Default Title':
                                    item['name'] = variant.product.title + ' ' + variant.title
                                else:
                                    item['name'] = variant.product.title

            # Post Entry in Logs
            action_performed = self.request.user.username + " Seen the dashboard"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            return Response(top_sold_items_list, status=200)
        except Exception as e:
            print(e)
            return Response({'detail': str(e)}, status=422)


class SaleByCity(APIView):
    def get(self, request):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "dashboard")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to this Api")

            vendor_id = self.request.GET.get('vendor_id', None)
            if vendor_id:
                vendor_id = int(vendor_id)
            start_date = self.request.GET.get('start_date', None)
            end_date = self.request.GET.get('end_date', None)

            if start_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                # start_date = start_date.strftime('%Y-%m-%d %H:%M:%S.%f')
                # start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S.%f')

            if end_date:
                end_date = datetime.strptime(f"{end_date} 23:59:59", '%Y-%m-%d %H:%M:%S')
                # end_date = end_date.strftime('%Y-%m-%d %H:%M:%S.%f')
                # end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S.%f')

            if self.request.user.is_vendor:
                vendor_id = self.request.user.vendor_id

            sale_by_city_list = []

            if not vendor_id:

                if start_date and end_date:
                    total_orders_list = Order.objects.filter(created_at__gte=start_date, created_at__lte=end_date)
                    all_cities = ShippingAddress.objects.filter(order__in=total_orders_list).values_list('city',
                                                                                                         flat=True)  # Do it in all functions
                    unique_cities = []

                    for item in all_cities:
                        unique_cities.append(item.strip())

                    unique_cities = list(set(unique_cities))

                    for city in unique_cities:
                        sale_by_city = {
                            'name': city,
                            'value': 0
                        }
                        for item in all_cities:

                            if item.strip() == city.strip():
                                sale_by_city['value'] += 1

                        sale_by_city_list.append(sale_by_city)

                    sale_by_city_list.sort(key=itemgetter('value'))
                    sale_by_city_list = sale_by_city_list[-5:]
                else:
                    all_cities = ShippingAddress.objects.filter(order__isnull=False).values_list('city',
                                                                                                 flat=True)  # Do it in all functions
                    unique_cities = []

                    for item in all_cities:
                        unique_cities.append(item.strip())

                    unique_cities = list(set(unique_cities))

                    for city in unique_cities:
                        sale_by_city = {
                            'name': city,
                            'value': 0
                        }
                        for item in all_cities:

                            if item.strip() == city.strip():
                                sale_by_city['value'] += 1

                        sale_by_city_list.append(sale_by_city)

                    sale_by_city_list.sort(key=itemgetter('value'))
                    sale_by_city_list = sale_by_city_list[-5:]

            if vendor_id:
                if start_date and end_date:
                    total_orders_list = ChildOrder.objects.filter(vendor_id=vendor_id, created_at__gte=start_date,
                                                                  created_at__lte=end_date).values_list('order_id',
                                                                                                        flat=True)
                    all_cities = ShippingAddress.objects.filter(order__in=total_orders_list).values_list('city',
                                                                                                         flat=True)  # Do it in all functions
                    unique_cities = []

                    for item in all_cities:
                        unique_cities.append(item.strip())

                    unique_cities = list(set(unique_cities))

                    for city in unique_cities:
                        sale_by_city = {
                            'name': city,
                            'value': 0
                        }
                        for item in all_cities:

                            if item.strip() == city.strip():
                                sale_by_city['value'] += 1

                        sale_by_city_list.append(sale_by_city)

                    sale_by_city_list.sort(key=itemgetter('value'))
                    sale_by_city_list = sale_by_city_list[-5:]
                else:
                    total_orders_list = ChildOrder.objects.filter(vendor_id=vendor_id).values_list('order_id',
                                                                                                   flat=True)
                    all_cities = ShippingAddress.objects.filter(order__in=total_orders_list).values_list('city',
                                                                                                         flat=True)  # Do it in all functions
                    unique_cities = []

                    for item in all_cities:
                        unique_cities.append(item.strip())

                    unique_cities = list(set(unique_cities))

                    for city in unique_cities:
                        sale_by_city = {
                            'name': city,
                            'value': 0
                        }
                        for item in all_cities:

                            if item.strip() == city.strip():
                                sale_by_city['value'] += 1

                        sale_by_city_list.append(sale_by_city)

                    sale_by_city_list.sort(key=itemgetter('value'))
                    sale_by_city_list = sale_by_city_list[-5:]

            # Post Entry in Logs
            action_performed = self.request.user.username + " Seen the dashboard"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            return Response(sale_by_city_list, status=200)
        except Exception as e:
            print(e)
            return Response({'detail': str(e)}, status=422)


class SaleByCategory(APIView):
    def get(self, request):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "dashboard")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to this Api")

            vendor_id = self.request.GET.get('vendor_id', None)
            if vendor_id:
                vendor_id = int(vendor_id)
            start_date = self.request.GET.get('start_date', None)
            end_date = self.request.GET.get('end_date', None)

            if start_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                # start_date = start_date.strftime('%Y-%m-%d %H:%M:%S.%f')
                # start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S.%f')

            if end_date:
                end_date = datetime.strptime(f"{end_date} 23:59:59", '%Y-%m-%d %H:%M:%S')
                # end_date = end_date.strftime('%Y-%m-%d %H:%M:%S.%f')
                # end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S.%f')

            if self.request.user.is_vendor:
                vendor_id = self.request.user.vendor_id

            sale_by_city_list = []
            sale_by_category = []

            if not vendor_id:

                if start_date and end_date:
                    variant_ids = LineItems.objects.filter(order_id__isnull=False, created_at__gte=start_date,
                                                           created_at__lte=end_date).values_list('variant_id',
                                                                                                 flat=True)
                    product_ids = Variant.objects.filter(id__in=variant_ids, product_id__isnull=False) \
                        .values_list('product_id', flat=True)
                    product_ids = list(product_ids)
                    unique_product_ids = list(set(product_ids))

                    for item in unique_product_ids:
                        data = {
                            'name': '',
                            'value': product_ids.count(item)
                        }

                        products = Product.objects.filter(id=item)
                        main_cat = MainCategory.objects.filter(collection_main_category__product__in=products). \
                            values('name').first()
                        if main_cat:
                            data['name'] = main_cat['name']
                        else:
                            sub_cat = SubCategory.objects.filter(collection_sub_category__product__in=products). \
                                values('name').first()
                            if sub_cat:
                                data['name'] = sub_cat['name']
                            else:
                                super_sub_cat = SuperSubCategory.objects.filter(
                                    collection_super_sub_category__product__in=products). \
                                    values('name').first()
                                if super_sub_cat:
                                    data['name'] = super_sub_cat['name']
                                else:
                                    continue
                        sale_by_city_list.append(data)
                    unique_cat_names = []

                    for item in sale_by_city_list:
                        if not item['name'] in unique_cat_names:
                            unique_cat_names.append(item['name'])

                    for item in unique_cat_names:
                        data = {
                            'name': item,
                            'value': 0
                        }
                        for item2 in sale_by_city_list:

                            if item == item2['name']:
                                data['value'] += item2['value']
                        sale_by_category.append(data)
                    sale_by_category.sort(key=itemgetter('value'))
                    sale_by_category = sale_by_category[-5:]
                else:
                    varient_ids = LineItems.objects.filter(order_id__isnull=False).values_list('variant_id',
                                                                                               flat=True)
                    product_ids = Variant.objects.filter(id__in=varient_ids, product_id__isnull=False) \
                        .values_list('product_id', flat=True)
                    product_ids = list(product_ids)
                    unique_product_ids = list(set(product_ids))

                    for item in unique_product_ids:
                        data = {
                            'name': '',
                            'value': product_ids.count(item)
                        }

                        products = Product.objects.filter(id=item)
                        main_cat = MainCategory.objects.filter(collection_main_category__product__in=products). \
                            values('name').first()
                        if main_cat:
                            data['name'] = main_cat['name']
                        else:
                            sub_cat = SubCategory.objects.filter(collection_sub_category__product__in=products). \
                                values('name').first()
                            if sub_cat:
                                data['name'] = sub_cat['name']
                            else:
                                super_sub_cat = SuperSubCategory.objects.filter(
                                    collection_super_sub_category__product__in=products). \
                                    values('name').first()
                                if super_sub_cat:
                                    data['name'] = super_sub_cat['name']
                                else:
                                    continue
                        sale_by_city_list.append(data)
                    unique_cat_names = []

                    for item in sale_by_city_list:
                        if not item['name'] in unique_cat_names:
                            unique_cat_names.append(item['name'])

                    for item in unique_cat_names:
                        data = {
                            'name': item,
                            'value': 0
                        }
                        for item2 in sale_by_city_list:

                            if item == item2['name']:
                                data['value'] += item2['value']
                        sale_by_category.append(data)
                    sale_by_category.sort(key=itemgetter('value'))
                    sale_by_category = sale_by_category[-5:]

            if vendor_id:
                if start_date and end_date:
                    variant_ids = ChildOrderLineItems.objects.filter(child_order_id__isnull=False,
                                                                     created_at__gte=start_date,
                                                                     created_at__lte=end_date).values_list('variant_id',
                                                                                                           flat=True)
                    product_ids = Variant.objects.filter(id__in=variant_ids, product_id__isnull=False) \
                        .values_list('product_id', flat=True)
                    product_ids = list(product_ids)
                    unique_product_ids = list(set(product_ids))

                    for item in unique_product_ids:
                        products = Product.objects.filter(id=item, vendor_id=vendor_id)
                        if not products:
                            continue
                        data = {
                            'name': '',
                            'value': product_ids.count(item)
                        }
                        main_cat = MainCategory.objects.filter(collection_main_category__product__in=products). \
                            values('name').first()
                        if main_cat:
                            data['name'] = main_cat['name']
                        else:
                            sub_cat = SubCategory.objects.filter(collection_sub_category__product__in=products). \
                                values('name').first()
                            if sub_cat:
                                data['name'] = sub_cat['name']
                            else:
                                super_sub_cat = SuperSubCategory.objects.filter(
                                    collection_super_sub_category__product__in=products). \
                                    values('name').first()
                                if super_sub_cat:
                                    data['name'] = super_sub_cat['name']
                                else:
                                    continue
                        sale_by_city_list.append(data)
                    unique_cat_names = []

                    for item in sale_by_city_list:
                        if not item['name'] in unique_cat_names:
                            unique_cat_names.append(item['name'])

                    for item in unique_cat_names:
                        data = {
                            'name': item,
                            'value': 0
                        }
                        for item2 in sale_by_city_list:

                            if item == item2['name']:
                                data['value'] += item2['value']
                        sale_by_category.append(data)
                    sale_by_category.sort(key=itemgetter('value'))
                    sale_by_category = sale_by_category[-5:]
                else:
                    variant_ids = ChildOrderLineItems.objects.filter(child_order_id__isnull=False) \
                        .values_list('variant_id', flat=True)
                    product_ids = Variant.objects.filter(id__in=variant_ids, product_id__isnull=False) \
                        .values_list('product_id', flat=True)
                    product_ids = list(product_ids)
                    unique_product_ids = list(set(product_ids))

                    for item in unique_product_ids:
                        products = Product.objects.filter(id=item, vendor_id=vendor_id)
                        if not products:
                            continue
                        data = {
                            'name': '',
                            'value': product_ids.count(item)
                        }
                        main_cat = MainCategory.objects.filter(collection_main_category__product__in=products). \
                            values('name').first()
                        if main_cat:
                            data['name'] = main_cat['name']
                        else:
                            sub_cat = SubCategory.objects.filter(collection_sub_category__product__in=products). \
                                values('name').first()
                            if sub_cat:
                                data['name'] = sub_cat['name']
                            else:
                                super_sub_cat = SuperSubCategory.objects.filter(
                                    collection_super_sub_category__product__in=products). \
                                    values('name').first()
                                if super_sub_cat:
                                    data['name'] = super_sub_cat['name']
                                else:
                                    continue
                        sale_by_city_list.append(data)
                    unique_cat_names = []

                    for item in sale_by_city_list:
                        if not item['name'] in unique_cat_names:
                            unique_cat_names.append(item['name'])
                    for item in unique_cat_names:
                        data = {
                            'name': item,
                            'value': 0
                        }
                        for item2 in sale_by_city_list:

                            if item == item2['name']:
                                data['value'] += item2['value']
                        sale_by_category.append(data)
                    sale_by_category.sort(key=itemgetter('value'))
                    # sale_by_category = sale_by_category[-5:]

            # Post Entry in Logs
            action_performed = self.request.user.username + " Seen the dashboard"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            return Response(sale_by_category, status=200)
        except Exception as e:
            print(e)
            return Response({'detail': str(e)}, status=422)


class SaleByMonth(APIView):
    def get(self, request):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "dashboard")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to this Api")

            vendor_id = self.request.GET.get('vendor_id', None)
            if vendor_id:
                vendor_id = int(vendor_id)
            today = datetime.today()
            if today.month == 1:
                one_month_ago = today.replace(year=today.year - 1, month=12)
            else:
                one_month_ago = today.replace(month=today.month - 1)

            start_date = one_month_ago.replace(hour=00, minute=00, second=00, microsecond=000000)
            end_date = one_month_ago.replace(hour=23, minute=59, second=59, microsecond=999999)

            if self.request.user.is_vendor:
                vendor_id = self.request.user.vendor_id

            sale_by_month = []

            if not vendor_id:
                for x in range(1, 31):
                    if x == 29 and start_date.month == 2:
                        break
                    start_date = start_date.replace(day=x)
                    end_date = end_date.replace(day=x)

                    total_orders_list = Order.objects.filter(created_at__gte=start_date, created_at__lte=end_date)
                    total_sale = total_orders_list.aggregate(Sum('total_price'))

                    if total_sale['total_price__sum']:
                        total_sale_value = total_sale['total_price__sum']
                    else:
                        total_sale_value = 0
                    data = {
                        'name': x,
                        'value': total_sale_value
                    }
                    sale_by_month.append(data)

            if vendor_id:
                for x in range(1, 31):
                    if x == 29 and start_date.month == 2:
                        break
                    start_date = start_date.replace(day=x)
                    end_date = end_date.replace(day=x)

                    total_orders_list = ChildOrder.objects.filter(vendor_id=vendor_id, created_at__gte=start_date,
                                                                  created_at__lte=end_date)
                    total_sale = total_orders_list.aggregate(Sum('total_price'))

                    if total_sale['total_price__sum']:
                        total_sale_value = total_sale['total_price__sum']
                    else:
                        total_sale_value = 0
                    data = {
                        'name': x,
                        'value': total_sale_value
                    }
                    sale_by_month.append(data)

            # Post Entry in Logs
            action_performed = self.request.user.username + " Seen the dashboard"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            return Response(sale_by_month, status=200)
        except Exception as e:
            print(e)
            return Response({'detail': str(e)}, status=422)


class SaleByVendor(APIView):
    def get(self, request):
        try:
            if not self.request.user.is_vendor:
                access = AccessApi(self.request.user, "dashboard")
                if not access:
                    raise exceptions.ParseError("This user does not have permission to this Api")

            vendor_id = self.request.GET.get('vendor_id', None)
            if vendor_id:
                vendor_id = int(vendor_id)

            if self.request.user.is_vendor:
                vendor_id = self.request.user.vendor_id

            sale_by_vendor = []

            if not vendor_id:
                all_vendor = Vendor.objects.filter(is_active=True)

                for vendor in all_vendor:
                    name = vendor.name
                    total_orders_list = ChildOrder.objects.filter(vendor_id=vendor.id)
                    total_value = total_orders_list.aggregate(Sum('total_price'))
                    paid_value_sum = total_orders_list.aggregate(Sum('paid_amount'))
                    total_orders = 0

                    if total_orders_list:
                        total_orders = total_orders_list.count()

                    if total_value['total_price__sum']:
                        total_sale_value = total_value['total_price__sum']
                    else:
                        total_sale_value = 0

                    if paid_value_sum['paid_amount__sum']:
                        paid_value = paid_value_sum['paid_amount__sum']
                    else:
                        paid_value = 0

                    pending_value = total_sale_value - paid_value
                    commission_value = vendor.commission_value
                    data = {
                        'name': name,
                        'total_orders': total_orders,
                        'total_value': total_sale_value,
                        'paid_value': paid_value,
                        'pending_value': pending_value,
                        'commission_value': commission_value
                    }
                    sale_by_vendor.append(data)

            if vendor_id:
                vendor = Vendor.objects.filter(is_active=True, id=vendor_id).first()

                if vendor:

                    name = vendor.name
                    total_orders_list = ChildOrder.objects.filter(vendor_id=vendor_id)
                    total_value = total_orders_list.aggregate(Sum('total_price'))
                    paid_value_sum = total_orders_list.aggregate(Sum('paid_amount'))
                    total_orders = 0

                    if total_orders_list:
                        total_orders = total_orders_list.count()

                    if total_value['total_price__sum']:
                        total_sale_value = total_value['total_price__sum']
                    else:
                        total_sale_value = 0

                    if paid_value_sum['paid_amount__sum']:
                        paid_value = paid_value_sum['paid_amount__sum']
                    else:
                        paid_value = 0

                    pending_value = total_sale_value - paid_value
                    commission_value = vendor.commission_value
                    data = {
                        'name': name,
                        'total_orders': total_orders,
                        'total_value': total_sale_value,
                        'paid_value': paid_value,
                        'pending_value': pending_value,
                        'commission_value': commission_value
                    }
                    sale_by_vendor.append(data)

            # Post Entry in Logs
            action_performed = self.request.user.username + " Seen the dashboard"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)

            return Response(sale_by_vendor, status=200)
        except Exception as e:
            print(e)
            return Response({'detail': str(e)}, status=422)
