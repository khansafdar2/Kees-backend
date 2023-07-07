
from rest_framework.response import Response
from rest_framework.views import APIView
from setting.models import CheckoutSetting
from setting.Serializers.CheckoutCustomizationSerializer import CheckoutCustomizationSerializer


class CheckoutCustomizationView(APIView):
    def get(self, request):
        query_set = CheckoutSetting.objects.filter(deleted=False).first()
        if not query_set:
            data = {}
            return Response(data, status=200)

        serializer = CheckoutCustomizationSerializer(query_set)
        return Response(serializer.data, status=200)
