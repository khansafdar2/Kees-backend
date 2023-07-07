
import smtplib
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from authentication.models import EmailProvider, EmailLogs


class EmailServiceProvider(object):
    def send_email(self, email, subject, body, provider=None, provider_type=None, ip_address=None):
        try:
            if provider_type is None:
                provider_type = self.provider_type

            if provider_type == "SMTP":

                if provider is None:
                    provider = EmailProvider.objects.get(id=self.id)

                server = smtplib.SMTP(provider.smtp_host, provider.smtp_port)
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(provider.from_email, provider.smtp_password)

                message = MIMEMultipart("alternative")
                message["Subject"] = subject
                message["From"] = provider.from_email
                message["To"] = email

                message.attach(MIMEText(body, "plain"))
                server.sendmail(provider.from_email, email, message.as_string())
                print("smtp email sent")
                server.quit()

                EmailLogs.objects.create(email_body=body,
                                         to_address=email,
                                         provider=provider.provider_type,
                                         from_address=provider.from_email,
                                         created_at=datetime.datetime.now(),
                                         updated_at=datetime.datetime.now(),
                                         response_status=True,
                                         response_message="Email Successfully Send",
                                         ip_address=ip_address)

                return True, "Email Successfully Send"

            elif provider_type == "SendGrid":

                if provider is None:
                    provider = EmailProvider.objects.get(id=self.id)

                message = Mail(
                    from_email=provider.from_email,
                    to_emails=email,
                    subject=subject,
                    # cc=cc_list,
                    html_content=body)

                sg = SendGridAPIClient(provider.api_key)

                sg.send(message)
                print("sendgrid email sent")

                EmailLogs.objects.create(email_body=body,
                                         to_address=email,
                                         provider=provider.provider_type,
                                         from_address=provider.from_email,
                                         created_at=datetime.datetime.now(),
                                         updated_at=datetime.datetime.now(),
                                         response_status=True,
                                         response_message="Email Successfully Send",
                                         ip_address=ip_address)

                return True, "Email Successfully Send"

        except Exception as e:
            print("Exception in email" + str(e))
            return False
