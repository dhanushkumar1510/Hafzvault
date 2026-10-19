import re

from rest_framework import serializers

from .attachments import attach_file, clear_file_fields
from .models import Account, Receipt
from .storage import delete_quietly
from .validators import validate_upload

USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,30}$")


class AccountInputSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    email = serializers.EmailField(max_length=254)

    def validate_username(self, value):
        value = value.strip()
        if not USERNAME_RE.match(value):
            raise serializers.ValidationError(
                "Username must be 3-30 characters: letters, numbers, dots, underscores or hyphens."
            )
        return value

    def validate_email(self, value):
        return value.strip().lower()


class AccountSerializer(serializers.ModelSerializer):
    receipt_count = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ["id", "username", "email", "created_at", "receipt_count"]

    def get_receipt_count(self, obj):
        return obj.receipts.count()


class ReceiptSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0)
    file = serializers.FileField(write_only=True, required=False)
    remove_file = serializers.BooleanField(write_only=True, required=False, default=False)
    has_file = serializers.SerializerMethodField()

    class Meta:
        model = Receipt
        fields = [
            "id", "name", "price", "purchase_date", "warranty_date", "notes",
            "has_file", "file_name", "file_content_type", "file_size",
            "created_at", "updated_at", "file", "remove_file",
        ]
        read_only_fields = ["id", "file_name", "file_content_type", "file_size", "created_at", "updated_at"]

    def get_has_file(self, obj):
        return bool(obj.file_path)

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Receipt name is required.")
        return value

    def validate_file(self, value):
        try:
            validate_upload(value)
        except serializers.ValidationError as exc:
            raise serializers.ValidationError(exc.detail["file"])
        return value

    def validate(self, attrs):
        purchase = attrs.get("purchase_date", getattr(self.instance, "purchase_date", None))
        warranty = attrs.get("warranty_date", getattr(self.instance, "warranty_date", None))
        if purchase and warranty and warranty < purchase:
            raise serializers.ValidationError(
                {"warranty_date": ["Warranty date cannot be before the purchase date."]}
            )
        return attrs

    def create(self, validated_data):
        upload = validated_data.pop("file", None)
        validated_data.pop("remove_file", None)
        receipt = Receipt(account=self.context["request"].user, **validated_data)
        new_path = attach_file(receipt, upload) if upload else None
        try:
            receipt.save()
        except Exception:
            delete_quietly(new_path)
            raise
        return receipt

    def update(self, instance, validated_data):
        upload = validated_data.pop("file", None)
        remove = validated_data.pop("remove_file", False)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        old_path = instance.file_path
        new_path = None
        if upload:
            new_path = attach_file(instance, upload)
        elif remove:
            clear_file_fields(instance)
        try:
            instance.save()
        except Exception:
            delete_quietly(new_path)
            raise
        if old_path and (upload or remove):
            delete_quietly(old_path)
        return instance
