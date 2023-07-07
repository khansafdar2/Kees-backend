from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.BusinessLogic.Threading import start_new_thread
from order.models import Order, OrderHistory, ChildOrder
from products.BusinessLogic.CategoriesAsTagsLogic import CategoriesAsTagsLogic
from products.BusinessLogic.ElasticSearch import ElasticSearch
from products.models import Product, Tags


class ScriptView(APIView):

    def get(self, request):
        # self.func()
        self.test()
        return Response("ok")

    @start_new_thread
    def func(self):
        products = Product.objects.filter(deleted=False).prefetch_related('tag',
                                                                          'collection__main_category',
                                                                          'collection__sub_category',
                                                                          'collection__super_sub_category')
        bl = CategoriesAsTagsLogic()
        for product in products:
            try:
                tags_list = []
                tags = bl.get_tags(product)
                for tag_name in tags:
                    tag = Tags.objects.filter(name__iexact=tag_name, is_option=False).first()
                    if not tag:
                        Tags.objects.create(name=tag_name)
                    tags_list.append(tag.id)
                if len(tags_list) > 0:
                    product.tag.set(tags_list)
            except Exception as e:
                print(e)

    def test(self):
        bl = ElasticSearch()
        bl.bulk_pagination()

    def delete_order(self):
        order = Order.objects.filter(name="#10003797").first()
        child_orders = ChildOrder.objects.filter(order=order)
        for child_order in child_orders:
            OrderHistory.objects.filter(child_order=child_order).delete()
            child_order.delete()

        OrderHistory.objects.filter(order=order).delete()
        order.delete()