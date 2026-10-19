import uuid

import django.core.validators
import django.db.models.deletion
import django.db.models.functions.text
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Account",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("username", models.CharField(max_length=30)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        django.db.models.functions.text.Lower("username"), name="uniq_account_username_ci"
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="Receipt",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=200)),
                (
                    "price",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=12,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("purchase_date", models.DateField()),
                ("warranty_date", models.DateField(blank=True, null=True)),
                ("notes", models.TextField(blank=True, default="")),
                ("file_path", models.CharField(blank=True, default="", max_length=500)),
                ("file_name", models.CharField(blank=True, default="", max_length=255)),
                ("file_content_type", models.CharField(blank=True, default="", max_length=100)),
                ("file_size", models.PositiveBigIntegerField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="receipts",
                        to="vault.account",
                    ),
                ),
            ],
            options={"ordering": ["-purchase_date", "-created_at"]},
        ),
        migrations.AddIndex(
            model_name="receipt",
            index=models.Index(fields=["account", "-purchase_date"], name="receipt_acct_purchase_idx"),
        ),
        migrations.AddIndex(
            model_name="receipt",
            index=models.Index(fields=["account", "name"], name="receipt_acct_name_idx"),
        ),
        migrations.AddIndex(
            model_name="receipt",
            index=models.Index(fields=["account", "warranty_date"], name="receipt_acct_warranty_idx"),
        ),
    ]
