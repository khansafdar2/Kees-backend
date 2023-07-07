from django.core.paginator import Paginator
from requests.auth import HTTPBasicAuth
from products.models import Product, MainCategory
from django.conf import settings
import json
import requests


class ElasticSearch(object):

    def __init__(self):
        self.username = settings.AWS_ELASTIC_USERNAME
        self.password = settings.AWS_ELASTIC_PASSWORD
        self.domain = settings.AWS_ELASTIC_DOMAIN
        self.index = settings.AWS_ELASTIC_SEARCH_INDEX_NAME

    @staticmethod
    def get_product_ids(response):
        product_ids = []
        hits = response.get('hits').get('hits') if response.get('hits') is not None else []
        for hit in hits:
            product_ids.append(int(hit['_id']))
        return product_ids

    def search(self, q):
        query = {
            "size": 1000,
            "from": 0,
            "sort": [
                {
                    "_score": {
                        "order": "desc"
                    }
                }
            ],
            "query": {
                "bool": {
                    "must": [
                        {
                            "more_like_this": {
                                "fields": [
                                    "title",
                                    # "super_sub_category",
                                    # "sub_category",
                                    # "main_category",
                                    # "description"
                                ],
                                "like": q,
                                "min_term_freq": 1,
                                "max_query_terms": 12,
                                "min_doc_freq": 1
                            }
                        }
                    ],
                    "filter": [
                        {
                            "match_phrase": {
                                "deleted": False
                            }
                        },
                        {
                            "match_phrase": {
                                "is_active": True
                            }
                        },
                        {
                            "match_phrase": {
                                "status": "Approved"
                            }
                        }
                    ]
                }
            }
        }

        url = self.domain + '/' + self.index + '/_search'
        response = requests.get(url=url, json=query, auth=HTTPBasicAuth(self.username, self.password))
        response = response.json()

        product_ids = self.get_product_ids(response)
        return product_ids

    def insert_or_update(self, product):
        document = {
            "title": product.title,
            'status': product.status,
            'is_active': product.is_active,
            'deleted': product.deleted
        }

        url = self.domain + '/' + self.index + '/_doc/' + str(product.id)
        response = requests.put(url=url, json=document, auth=HTTPBasicAuth(self.username, self.password))
        response = response.json()
        return response

    def bulk_pagination(self, ids=None):

        if ids is None:
            products = Product.objects.filter(deleted=False, is_active=True, status="Approved"). \
                prefetch_related('collection__main_category', 'collection__sub_category',
                                 'collection__super_sub_category', 'tag')
        else:
            products = Product.objects.filter(id__in=ids). \
                prefetch_related('collection__main_category', 'collection__sub_category',
                                 'collection__super_sub_category', 'tag')

        products_paginator: Paginator = Paginator(products, 1000)
        page_no = 1
        has_next_page = True

        while has_next_page:
            page = products_paginator.page(page_no)
            products = page.object_list

            self.bulk_insert_or_update(products)

            has_next_page = page.has_next()
            if has_next_page:
                page_no = page.next_page_number()

    def bulk_insert_or_update(self, products):
        bulk_file = ''
        for product in products:
            bulk_file += '{ "index" : { "_index" : "' + self.index + '", "_type" : "_doc", "_id" : "' + str(
                product.id) + '" } }\n'

            # tags_lst = []
            # tags = product.tag.all()
            # for tag in tags:
            #     if not tag.deleted and tag.is_active:
            #         tags_lst.append(tag.name)
            #
            # main_category_lst = []
            # sub_category_lst = []
            # super_sub_category_lst = []
            # product_collections = product.collection.all()
            # for product_collection in product_collections:
            #     for category_collection in product_collection.main_category.all():
            #         main_category_lst.append(category_collection.name)
            #     for category_collection in product_collection.sub_category.all():
            #         sub_category_lst.append(category_collection.name)
            #     for category_collection in product_collection.super_sub_category.all():
            #         super_sub_category_lst.append(category_collection.name)
            #
            # index = {'title': product.title, 'status': product.status, 'is_active': product.is_active,
            #          'deleted': product.deleted, 'description': product.description,
            #          'main_category': main_category_lst, 'sub_category': sub_category_lst,
            #          'super_sub_category': super_sub_category_lst, 'tags': tags_lst}

            index = {'title': product.title, 'status': product.status, 'is_active': product.is_active,
                     'deleted': product.deleted}
            bulk_file += json.dumps(index) + '\n'

        if len(products) > 0:
            url = self.domain + '/_bulk'
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url=url, auth=HTTPBasicAuth(self.username, self.password), data=bulk_file,
                                     headers=headers)
            print(response)
