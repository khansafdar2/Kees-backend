
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.conf import settings


class ForgotPasswordEmail(object):
    def __init__(self):
        pass

    def send_password_email(self, email, code, url):
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = "Forgot Password"
            message["From"] = settings.EMAIL_HOST_USER
            message["To"] = email

            # Create the plain-text and HTML version of your message
            html = """
            <html>
              <body>
                   <a href="{url}/reset_password?code={code}">Click here to reset password</a> 
              </body>
            </html>
            """.format(url=url, code=code)

            # Turn these into plain/html MIMEText objects
            part1 = MIMEText(html, "html")

            # Add HTML/plain-text parts to MIMEMultipart message
            # The email client will try to render the last part first
            message.attach(part1)

            server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

            server.sendmail(settings.EMAIL_HOST_USER, email, message.as_string())
            server.quit()
            return True
        except Exception as e:
            print("Exception " + str(e))
            return False
