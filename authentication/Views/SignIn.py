
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.models import User, MessageProvider, EmailProvider, RolePermission, UserLastLogin
from authentication.Serializer.RolePermissionSerializer import RolePermissionSerializer
from authentication.Serializer.LoginSerializer import LoginSerializer
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from authentication.BusinessLogic.ActivityStream import SystemLogs, get_client_ip
import datetime, random, geocoder
from authentication.BusinessLogic.EmailService import EmailServiceProvider
from authentication.BusinessLogic.MessageService import MessageServiceProvider
from drf_yasg.utils import swagger_auto_schema


# SignIn API
class SignIn(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(responses={200: LoginSerializer}, request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            user.token = get_token(user.username)
            user.save()

            ip_address = get_client_ip(request)
            g = geocoder.ip(ip_address)
            try:
                country_code = str(g.geojson['features'][0]['properties']['country'])
            except Exception as e:
                print(e)
                country_code = str(g.geojson['features'][0]['properties']['status'])
            UserLastLogin.objects.create(user=user, ip_address=ip_address, location=country_code)

            if user.is_superuser:
                print("Super user found, giving all permissions")
                role_obj = {
                    "dashboard": True,
                    "theme": True,
                    "products": True,
                    "orders": True,
                    "customer": True,
                    "discounts": True,
                    "configuration": True,
                    "customization": True,
                    "vendor": True,
                    "approvals": True,
                    "product_list": True,
                    "product_groups": True,
                    "collections": True,
                    "categories": True,
                    "brands": True,
                    "homepage": True,
                    "static_pages": True,
                    "header": True,
                    "footer": True,
                    "navigation": True,
                    "filters": True,
                    "main_discounts": True,
                    "coupons": True,
                    "store_setting": True,
                    "user_management": True,
                    "loyalty": True,
                    "shipping_regions": True,
                    "shipping_methods": True,
                    "checkout_setting": True,
                    "notifications": True,
                    "socialfeed": True,
                    "featured_apps": True,
                    "blog": True,
                }
            else:
                try:
                    role_permission = RolePermission.objects.filter(user_id=user.id).first()
                    serializer = RolePermissionSerializer(role_permission)
                    role_obj = serializer.data
                except Exception as e:
                    print(e)
                    role_obj = dummy_permission()

            user_obj = {
                "id": user.id,
                "token": user.token,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "owner": user.is_owner,
                "is_vendor": user.is_vendor,
                "vendor_id": user.vendor_id,
                "permission": role_obj
            }

            # Post Entry in Logs
            action_performed = user.username + " login"
            SystemLogs.post_logs(self, request, user, action_performed)

            login_user = User.objects.get(id=user.id)
            if login_user.email_2fa or login_user.phone_2fa:
                now = datetime.datetime.now()
                login_user.otp_expiry = now
                sms = MessageServiceProvider()
                email = EmailServiceProvider()
                code = str(random.randint(1000, 9999)) + now.strftime('%S')
                msg = '''Dear Customer {name}, 
                            Your OTP: One-Time Authorization Passcode for {brand_name} is {code}.
                            For security reasons, please do not share your OTP with others.
                            '''.format(name=user.first_name + ' ' + user.last_name, code=code, brand_name="Khaadi")

            if user.email_2fa:
                email_provider = EmailProvider.objects.first()
                if email_provider is not None:
                    user.email_otp = code
                    email.send_email(email_provider, email, user.email, "OTP", msg, email_provider,
                                     email_provider.provider_type, request.META.get('REMOTE_ADDR'))
                    user.save()
            if user.phone_2fa:
                sms_provider = MessageProvider.objects.first()
                if sms_provider is not None:
                    user.phone_otp = code
                    sms.send_message(sms_provider, sms, user.phoneNumber, msg, sms_provider, sms_provider.provider_type,
                                     request.META.get('REMOTE_ADDR'))
                    user.save()

            return Response(user_obj, status=200, content_type='application/json')
        else:
            return Response(serializer.errors, status=422)


def get_token(username):
    token, created = Token.objects.get_or_create(user=User.objects.get(username=username))
    token.delete()
    token, created = Token.objects.get_or_create(user=User.objects.get(username=username))
    User.objects.filter(username=token.user.username).update(api_token_expired=False)

    api_token = "Token " + token.key

    return api_token


def dummy_permission():
    role_obj = {
        "dashboard": False,
        "theme": False,
        "products": False,
        "orders": False,
        "customer": False,
        "discounts": False,
        "configuration": False,
        "customization": False,
        "vendor": False,
        "approvals": False,
        "product_list": False,
        "product_groups": False,
        "collections": False,
        "categories": False,
        "brands": False,
        "homepage": False,
        "static_pages": False,
        "header": False,
        "footer": False,
        "navigation": False,
        "filters": False,
        "main_discounts": False,
        "coupons": False,
        "store_setting": False,
        "user_management": False,
        "loyalty": False,
        "shipping_regions": False,
        "shipping_methods": False,
        "checkout_setting": False,
        "notifications": False,
        "socialfeed": False,
        "featured_apps": False,
    }
    return role_obj
