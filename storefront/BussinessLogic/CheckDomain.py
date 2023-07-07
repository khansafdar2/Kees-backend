
from django.http.request import split_domain_port
from setting.models import StoreSetting
import httpagentparser
from rest_framework import exceptions


def check_domain(request):
    store_setting = StoreSetting.objects.filter(deleted=False).first()
    if store_setting:
        if not store_setting.development:
            agent = request.environ.get('HTTP_USER_AGENT')
            browser = httpagentparser.detect(agent)
            if browser and 'browser' in browser:
                browser = browser['browser']['name']
            else:
                browser = False

            domains = store_setting.domains.split(",")
            if not request.headers.__contains__("Origin") or (request.headers["Origin"]).replace('https://', '') not in domains or not browser:
                return True
    return False

