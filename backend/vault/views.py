import logging
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.db import IntegrityError
from django.db.models import F, Sum
from django.db.models.functions import Lower
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .attachments import FILE_FIELDS, attach_file, clear_file_fields
from .exceptions import StorageUnavailable
from .models import Account, Receipt
from .serializers import AccountInputSerializer, AccountSerializer, ReceiptSerializer
from .storage import StorageError, delete_quietly, get_storage

logger = logging.getLogger(__name__)

USERNAME_TAKEN = (
    "username_email_mismatch",
    "This username is already registered with a different email address. "
    "The username and email combination does not match.",
)
EMAIL_TAKEN = (
    "email_username_mismatch",
    "This email is already registered with a different username. "
    "The username and email combination does not match.",
)


def _conflict(pair):
    return Response({"code": pair[0], "detail": pair[1]}, status=status.HTTP_409_CONFLICT)


def _find(username, email):
    """Returns (exact_match, conflict_pair_or_None)."""
    exact = Account.objects.filter(username__iexact=username, email=email).first()
    if exact:
        return exact, None
    if Account.objects.filter(username__iexact=username).exists():
        return None, USERNAME_TAKEN
    if Account.objects.filter(email=email).exists():
        return None, EMAIL_TAKEN
    return None, None


class HealthView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = []

    def get(self, request):
        Account.objects.exists()  # touches the database
        return Response({"status": "ok"})


class AccountLookupView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        data = AccountInputSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        account, conflict = _find(data.validated_data["username"], data.validated_data["email"])
        if conflict:
            return _conflict(conflict)
        if not account:
            return Response(
                {"code": "account_not_found",
                 "detail": "No account exists for this username and email yet. You can create one."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(AccountSerializer(account).data)


class AccountCreateView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        data = AccountInputSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        username, email = data.validated_data["username"], data.validated_data["email"]
        account, conflict = _find(username, email)
        if account:
            return Response(
                {"code": "account_exists", "detail": "This account already exists. Log in instead."},
                status=status.HTTP_409_CONFLICT,
            )
        if conflict:
            return _conflict(conflict)
        try:
            account = Account.objects.create(username=username, email=email)
        except IntegrityError:
            _, conflict = _find(username, email)
            return _conflict(conflict or USERNAME_TAKEN)
        return Response(AccountSerializer(account).data, status=status.HTTP_201_CREATED)


class ProfileView(APIView):
    def get(self, request):
        return Response(AccountSerializer(request.user).data)


class SummaryView(APIView):
    def get(self, request):
        qs = Receipt.objects.filter(account=request.user)
        today = timezone.localdate()
        soon = today + timedelta(days=30)
        total = qs.aggregate(t=Sum("price"))["t"] or Decimal("0")
        return Response({
            "receipt_count": qs.count(),
            "total_spent": str(Decimal(total).quantize(Decimal("0.01"))),
            "active_warranties": qs.filter(warranty_date__gte=today).count(),
            "expiring_soon": qs.filter(warranty_date__gte=today, warranty_date__lte=soon).count(),
            "expired_warranties": qs.filter(warranty_date__lt=today).count(),
            "recent": ReceiptSerializer(qs.order_by("-created_at")[:5], many=True).data,
        })


ORDERINGS = {
    "purchase_date": (F("purchase_date").asc(), "created_at"),
    "-purchase_date": (F("purchase_date").desc(), "-created_at"),
    "warranty_date": (F("warranty_date").asc(nulls_last=True), "name"),
    "-warranty_date": (F("warranty_date").desc(nulls_last=True), "name"),
    "name": (Lower("name").asc(), "created_at"),
    "-name": (Lower("name").desc(), "created_at"),
}


def _file_info(receipt):
    try:
        url = get_storage().signed_url(receipt.file_path, settings.SIGNED_URL_SECONDS)
    except StorageError as exc:
        logger.error("Signed URL failed: %s", exc)
        raise StorageUnavailable() from exc
    return {
        "url": url,
        "expires_in": settings.SIGNED_URL_SECONDS,
        "file_name": receipt.file_name,
        "content_type": receipt.file_content_type,
        "file_size": receipt.file_size,
    }


class ReceiptViewSet(viewsets.ModelViewSet):
    serializer_class = ReceiptSerializer

    def get_queryset(self):
        qs = Receipt.objects.filter(account=self.request.user)  # ownership filter on every query
        if self.action != "list":
            return qs
        params = self.request.query_params
        q = params.get("q", "").strip()
        if q:
            qs = qs.filter(name__icontains=q)
        today = timezone.localdate()
        warranty = params.get("warranty")
        if warranty == "active":
            qs = qs.filter(warranty_date__gte=today)
        elif warranty == "expired":
            qs = qs.filter(warranty_date__lt=today)
        elif warranty == "none":
            qs = qs.filter(warranty_date__isnull=True)
        elif warranty:
            raise ValidationError({"warranty": ["Use active, expired or none."]})
        ordering = params.get("ordering", "-purchase_date")
        if ordering not in ORDERINGS:
            raise ValidationError({"ordering": [f"Use one of: {', '.join(ORDERINGS)}."]})
        return qs.order_by(*ORDERINGS[ordering])

    def perform_destroy(self, instance):
        path = instance.file_path
        instance.delete()
        delete_quietly(path)

    @action(detail=True, methods=["get", "put", "delete"], url_path="attachment")
    def attachment(self, request, pk=None):
        receipt = self.get_object()
        if request.method == "GET":
            if not receipt.file_path:
                raise NotFound("This receipt has no attachment.")
            return Response(_file_info(receipt))

        old_path = receipt.file_path
        if request.method == "PUT":
            upload = request.data.get("file")
            if not upload or not hasattr(upload, "read"):
                raise ValidationError({"file": ["Choose a file to upload."]})
            new_path = attach_file(receipt, upload)
        else:
            if not old_path:
                raise NotFound("This receipt has no attachment.")
            new_path = None
            clear_file_fields(receipt)
        try:
            receipt.save(update_fields=FILE_FIELDS + ["updated_at"])
        except Exception:
            delete_quietly(new_path)
            raise
        delete_quietly(old_path)
        return Response(ReceiptSerializer(receipt).data)
