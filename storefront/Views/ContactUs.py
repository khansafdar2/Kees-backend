
from rest_framework.response import Response
from rest_framework.views import APIView
from cms.models import Newsletter
from storefront.Serializers.CustomizationSerializer import NewsletterSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework import exceptions
from django.conf import settings
from django.core.mail import EmailMessage
from setting.models import StoreInformation
from storefront.BussinessLogic.CheckDomain import check_domain


class ContactUs(APIView):
    def post(self, request):
        access = check_domain(self.request)
        if access:
            raise exceptions.ParseError("This user does not have permission to this Api")

        request_data = request.data
        try:
            subject = "Customer Contact"
            contact_email = settings.EMAIL_HOST_USER
            store = StoreInformation.objects.get(deleted=False)
            to = store.store_contact_email
            content = f'''Name: {request_data['name']} \nEmail:  {request_data['email']} \nMessage: {request_data['message']}'''
            email = EmailMessage(
                subject,
                content,
                contact_email,
                [to],
                headers={'Reply-To': contact_email}
            )
            email.send()
            return Response({"email send successfully"}, status=200)
        except Exception as e:
            return Response(str(e), status=400)
