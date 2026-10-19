from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import Account

USERNAME_HEADER = "X-Account-Username"
EMAIL_HEADER = "X-Account-Email"


class HeaderIdentityAuthentication(BaseAuthentication):
    """Identifies the account from the username + email headers.

    This is NOT verified identity: anyone who knows a username/email pair can
    act as that account. That is the product requirement (no passwords/OTPs).
    """

    def authenticate(self, request):
        username = request.headers.get(USERNAME_HEADER, "").strip()
        email = request.headers.get(EMAIL_HEADER, "").strip().lower()
        if not username and not email:
            return None
        if not username or not email:
            raise AuthenticationFailed("Both username and email are required.")
        try:
            account = Account.objects.get(username__iexact=username, email=email)
        except Account.DoesNotExist:
            raise AuthenticationFailed("This username and email combination does not match an account.")
        return (account, None)

    def authenticate_header(self, request):
        return "X-Account"
