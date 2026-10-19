import os

from django.conf import settings
from rest_framework.exceptions import ValidationError

ALLOWED = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
    "pdf": "application/pdf",
}


def _matches_signature(ext, head):
    if ext in ("jpg", "jpeg"):
        return head.startswith(b"\xff\xd8\xff")
    if ext == "png":
        return head.startswith(b"\x89PNG\r\n\x1a\n")
    if ext == "webp":
        return head[:4] == b"RIFF" and head[8:12] == b"WEBP"
    if ext == "pdf":
        return head.startswith(b"%PDF-")
    return False


def validate_upload(upload):
    """Returns (content_type, extension) or raises a 400 ValidationError on `file`."""
    ext = os.path.splitext(upload.name or "")[1].lstrip(".").lower()
    if ext not in ALLOWED:
        raise ValidationError({"file": ["Unsupported file type. Use JPG, JPEG, PNG, WEBP or PDF."]})
    if not upload.size:
        raise ValidationError({"file": ["The selected file is empty."]})
    if upload.size > settings.MAX_UPLOAD_BYTES:
        mb = settings.MAX_UPLOAD_BYTES / (1024 * 1024)
        raise ValidationError({"file": [f"File is too large. Maximum size is {mb:g} MB."]})
    upload.seek(0)
    head = upload.read(12)
    upload.seek(0)
    if not _matches_signature(ext, head):
        raise ValidationError({"file": ["The file contents do not match its type. It may be corrupted."]})
    return ALLOWED[ext], ext
