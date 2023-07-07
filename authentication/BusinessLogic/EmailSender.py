
from django.conf import settings
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.template import Context

from authentication.models import EmailTemplates


def send_email(to_email, email_template, email_subject, bcc_email=None):
    try:
        to = [to_email]
        email = EmailMultiAlternatives(
            subject=email_subject,
            from_email=settings.EMAIL_HOST_USER,
            to=to,
            bcc=[bcc_email]
        )

        email.attach_alternative(email_template, "text/html")
        email.send()
        return True
    except Exception as e:
        print(e)
        return False


def email_templates(template_name, email_content):
    template_content = EmailTemplates.objects.filter(title=template_name).first()
    email_template = template_content.template
    email_content = email_content

    for key, value in email_content.items():
        key = '{{' + key + '}}'
        email_template = email_template.replace(key, value)

    return email_template
