import uuid

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.functions import Lower


class Account(models.Model):
    """A username + email pair. Intentionally unverified: no password, OTP or email check."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Lets DRF treat a matched Account as the request user.
    is_authenticated = True
    is_anonymous = False

    class Meta:
        constraints = [models.UniqueConstraint(Lower("username"), name="uniq_account_username_ci")]

    def __str__(self):
        return f"{self.username} <{self.email}>"


class Receipt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="receipts")
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    purchase_date = models.DateField()
    warranty_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    file_path = models.CharField(max_length=500, blank=True, default="")
    file_name = models.CharField(max_length=255, blank=True, default="")
    file_content_type = models.CharField(max_length=100, blank=True, default="")
    file_size = models.PositiveBigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-purchase_date", "-created_at"]
        indexes = [
            models.Index(fields=["account", "-purchase_date"], name="receipt_acct_purchase_idx"),
            models.Index(fields=["account", "name"], name="receipt_acct_name_idx"),
            models.Index(fields=["account", "warranty_date"], name="receipt_acct_warranty_idx"),
        ]

    def __str__(self):
        return self.name
