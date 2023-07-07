from requests import Response

from setting.models import StoreInformation


def SecuredApis(self):
    try:
        store = StoreInformation.objects.filter(deleted=False).first()
        if store:
            domains = store.domains.split(",")
            development = store.development
            data = {
                'domains': domains,
                'development': development
            }
            return data
    except Exception as e:
        return Response({"detail": str(e)}, status=200)
