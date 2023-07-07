
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.models import MessageProvider, EmailProvider
from authentication.BusinessLogic.EmailService import EmailServiceProvider
from authentication.BusinessLogic.MessageService import MessageServiceProvider
import datetime
import random

from setting.models import StoreInformation


class ResendOTP(APIView):

    def get(self, request):
        user = request.user
        if user is not None:
            try:
                store = StoreInformation.objects.get(deleted=False)
            except Exception as e:
                print(e)
                return Response({'detail': 'Store not exist'}, status=404)

            now = datetime.datetime.now()
            code = str(random.randint(1000, 9999)) + now.strftime('%S')
            sms = MessageServiceProvider()
            email = EmailServiceProvider()
            msg = f'''Dear Customer {user.first_name + ' ' + user.last_name}, 
            Your OTP: One-Time Authorization Passcode for {store.store_name} is {code}.
            For security reasons, please do not share your OTP with others.
            '''

            if user.email_2fa or user.phone_2fa:
                user.otp_expiry = now

            if user.email_2fa:
                email_provider = EmailProvider.objects.filter(deleted=False).first()

                if email_provider is not None:
                    user.email_otp = code
                    email.send_email(email_provider, email, user.email, "OTP", msg, email_provider, email_provider.provider_type, request.META.get('REMOTE_ADDR'))
                    user.save()

            if user.phone_2fa:
                sms_provider = MessageProvider.objects.filter(deleted=False).first()

                if sms_provider is not None:
                    user.phone_otp = code
                    sms.send_message(sms_provider, sms, user.phoneNumber, msg,  sms_provider, sms_provider.provider_type, request.META.get('REMOTE_ADDR'))
                    user.save()

            if user.phone_2fa or user.email_2fa:
                return Response({"detail": "OTP sent"}, status=200, content_type='application/json')
            return Response({"detail": "2FA not found"}, status=401)
        else:
            return Response({"detail": "User not found"}, status=401)
