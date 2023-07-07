
from setting.models import StoreInformation


def api_secure():
    store = StoreInformation.objects.filter(deleted=False).first()
    if store:
        data = {
            'domains': store.domains,
            'development': store.development
        }
        return data
