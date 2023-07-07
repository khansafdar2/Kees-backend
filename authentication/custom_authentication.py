
from authentication.models import User
from rest_framework.authtoken.models import Token
from rest_framework import authentication, HTTP_HEADER_ENCODING, exceptions
from django.utils.translation import gettext_lazy as _
from datetime import timedelta, datetime


class TokenAuthentication(authentication.BaseAuthentication):

    keyword = 'Token'

    def authenticate(self, request):
        auth = request.META.get('HTTP_AUTHORIZATION', b'')
        if isinstance(auth, str):
            auth = auth.encode(HTTP_HEADER_ENCODING)
        auth = auth.split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        try:
            token = Token.objects.select_related('user').get(key=key)
        except Token.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Session expired, Reopen the application!'))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        utc_now = datetime.now()

        if token.created < utc_now - timedelta(hours=6):
            User.objects.filter(email=token.user.email).update(api_token_expired=True)
            raise exceptions.AuthenticationFailed(_('Session expired, Reopen the application!'))

        return (token.user, token)
