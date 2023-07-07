
import json
from datetime import datetime

import requests
from ecomm_app.settings.local import LOYALTY_MICROSERVICE_URL
from setting.models import StoreInformation, LoyaltySetting, Rule
from rest_framework.response import Response
from rest_framework.views import APIView
from setting.Serializers.LoyaltySerializer import SettingSerializer, RuleSerializer


class SettingView(APIView):
    def get(self, request):
        try:
            query_set = LoyaltySetting.objects.filter(deleted=False).first()
            setting_serializer = SettingSerializer(query_set).data

            query_set = Rule.objects.filter(deleted=False)
            rule_serializer = RuleSerializer(query_set, many=True).data

            setting_serializer['rules'] = rule_serializer

            return Response(setting_serializer, status=200)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)

    def post(self, request):
        try:
            serializer = SettingSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

                return Response(serializer.data, status=200)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)


class RuleDetailView(APIView):
    def delete(self, request, pk):
        try:
            Rule.objects.filter(id=pk).update(deleted=True, deleted_at=datetime.now())
            return Response("Rule Deleted Successfully", status=200)
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=404)
