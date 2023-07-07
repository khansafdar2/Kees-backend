import firebase_admin
from firebase_admin import credentials, messaging
from authentication.BusinessLogic.ActivityStream import SystemLogs
from authentication.BusinessLogic.Threading import start_new_thread
from notification.models import FirebaseSettings, FirebaseNotification, FirebaseDeviceToken, FirebaseNotificationHistory


def send_web_push_notification(registration_tokens, message_title, message_body, image_link, redirect_url):
    ##########################################
    ######## Load this from Database #########
    ##########################################

    # config = {
    #     "type": "service_account",
    #     "project_id": "comverse-295a4",
    #     "private_key_id": "3ec32fd58a7690584b9e44a7a77bb1602819805c",
    #     "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCzQwkgEoYBWI37\nHZAxcaqJ+FTlqTTzQLTRhUE3VQjZ+G1r2q1ffNS0WCWz4TwDy0qgdpXQisq8Ywnt\nXkTwkqe9e7K456GxxR2Da2wLBqVgXD4vi+6gemCYc/l4q8MF3O0V1EKBsGOjBwRu\nU+rlylfmPV0p3pUEY8e5/c9IheEoQ2ldpGg+mVwBUV5gDFhbo8UBpb9zP66DmUPI\nmhnnytYv4dJHU6PWumeo0h2eXL/jQwMu+CAshk7iWJCoFkryPLHRbjUqSEnDuZzx\nTOZ68K39aYL8nyKLCsO8SXDOHCjeM4E5LCGYkys4vaSKZroE4jqnicYQGpbyTocY\n0UoqHsdbAgMBAAECggEAGFeWr6I+9tkoPodJ2KJPaXjX88UXCZ5/GfchtKUkFI/l\nhpXP9n15rMZOKFpXefRrEoByi4+tRAj22iLI8xoXE7tDuP7LODFEzAm+8X2vi0w7\nWDLaQ98aVYQPcPwcpCPXQKBC1QriHMs2e3zYaD0ifoNVWVAo+sr0iM8XDLQRWmls\n4IZN2s76P/Sia/WPF/DNx5adeofp8jTLSdaEy0jSe4DvYcC8VDJ81LIRyvgqH6KS\nmgCxFxUK+2ULbpbZBUXgmWoH/z2kbh2OkLPmh7KzupSseIksk7DvFzb1j6QmYQS8\nz7JpIw84XPQ/7/zHccmbtCqf3b2xSIzHsFw7aWHEIQKBgQD4G3mHJjooP46bnQ5Y\nSR7JGzc4C+ZT4LR+AEynZAK0dMm4OLWxHcrQMBenkZ53EUZoCVrMdy3wJRSGxbRJ\n7dsJWh7NaTe3YC0pH+ZfdTuHAwNyoX2/CN2Zb4T9VIZQR2Vxl8PVjZ9Bydc9KE/0\nE2DT1ncPKclCkEhAQOKIkdnu+QKBgQC49uZ7ROqXh5HxeueXA24Edg9DT1ZPbubD\nLN/tAcUDNcoGJnhqXOsJRmZkajwTjQ/kStu8xOAHlZY6h2WZ9DVN5F+bpnAHDWdh\nyJ98xh45EF1O0g9jLUDlQbhAReQlph1iSsROQ3B3iIDkG0jJA8BWaEJBI7erYlRc\nShku78e58wKBgQDOtM0+TRn8+F7OxT3zThApCtSpjDh8P2UA6Szz9P3P7NE2+4Bc\nrO6RHtBGWqsElk7rVIfie5S5U5tTYZoAUfvAQeYRywyRab6WWa5sb1aF+HvB4EvM\ngg1lzSSmjupMLf+VcRTGcfRyMkByAokCV7a/JxoQdwbnvx+C8MwLbkB8uQKBgQCT\nEc6lyWB26BcFWWJ30wRRi8YLETRhqJ7YJgBPJY8PRF/EkCZC/GruTwnvYgEu0oUG\nUvdxm2E+5pQzKaGBzonry2CyFJ8THHdNawZVYfp6CScIG0Kc60ikgaMNiAUmYnUO\nyMBaMolkoidKON+g5dizW+cCgHH0VhUZ5NktVv8KPQKBgDgurh7icdZsIAn1ZfQf\naIdciW7mSEnIynt861hwIv6chZQbOCkRRIJJLNLd0Ls8gWxFhoEbsheSI7yaLY0c\nR+I8qoqAnWEWCVKv9d1q6sTWa9BgOAFxmFAQMBUoGFBpdNiKTiton7wFRmyFM6nV\nJrE5q+W6Fp2bmcqEPmcCP7t1\n-----END PRIVATE KEY-----\n",
    #     "client_email": "firebase-adminsdk-edhfb@comverse-295a4.iam.gserviceaccount.com",
    #     "client_id": "114349513555172871007",
    #     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    #     "token_uri": "https://oauth2.googleapis.com/token",
    #     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    #     "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-edhfb%40comverse-295a4.iam.gserviceaccount.com"
    # }

    setting = FirebaseSettings.objects.filter(deleted=False).first()
    if setting:
        firebase_cred = credentials.Certificate(setting.credentials_json)
        try:
            firebase_admin.initialize_app(firebase_cred)
        except Exception as e:
            print(e)

        if image_link is not None:
            if redirect_url is not None:
                message = messaging.MulticastMessage(
                    notification=messaging.Notification(title=message_title, body=message_body, image=image_link),
                    tokens=registration_tokens, webpush=messaging.WebpushConfig(notification=messaging.WebpushNotification(
                        title=message_title, body=message_body, image=image_link), fcm_options=messaging.WebpushFCMOptions(
                        link=redirect_url)))
            else:
                message = messaging.MulticastMessage(
                    notification=messaging.Notification(title=message_title, body=message_body, image=image_link),
                    tokens=registration_tokens,
                    webpush=messaging.WebpushConfig(notification=messaging.WebpushNotification(
                        title=message_title, body=message_body, image=image_link)))
        else:
            if redirect_url is not None:
                message = messaging.MulticastMessage(
                    notification=messaging.Notification(title=message_title, body=message_body),
                    tokens=registration_tokens, webpush=messaging.WebpushConfig(notification=messaging.WebpushNotification(
                        title=message_title, body=message_body), fcm_options=messaging.WebpushFCMOptions(
                        link=redirect_url)))
            message = messaging.MulticastMessage(
                notification=messaging.Notification(title=message_title, body=message_body),
                tokens=registration_tokens)

        response = messaging.send_multicast(message)
        print('{0} messages were sent successfully'.format(response.success_count))
        return True


class BackgroundNotification:

    @start_new_thread
    def send_notification_in_background(self, notification_id):
        notification = FirebaseNotification.objects.filter(id=notification_id).first()
        if notification:
            off_set = 0
            limit = 500
            count = 0

            if notification.message_image_url:
                image_url = notification.message_image_url
            else:
                image_url = None

            if notification.redirect_url:
                redirect_url = notification.redirect_url
            else:
                redirect_url = None

            while True:
                device_tokens = list(FirebaseDeviceToken.objects.filter(deleted=False).values_list('device_token',
                                                                                                   flat=True)[
                                     off_set:limit])
                response_from_firebase = send_web_push_notification(registration_tokens=device_tokens,
                                                                    message_title=notification.message_title,
                                                                    message_body=notification.message_description,
                                                                    image_link=image_url,
                                                                    redirect_url=redirect_url)
                if response_from_firebase:
                    count += len(device_tokens)
                    off_set += 500
                    limit += 500

                if len(device_tokens) < 500:
                    break

            FirebaseNotificationHistory.objects.create(firebase_notification=notification, count=count)

            # Post Entry in Logs
            action_performed = self.request.user.username + "send notifications"
            SystemLogs.post_logs(self, self.request, self.request.user, action_performed)
