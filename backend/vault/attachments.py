import logging
import os
import uuid

from .exceptions import StorageUnavailable
from .storage import StorageError, get_storage
from .validators import validate_upload

logger = logging.getLogger(__name__)

FILE_FIELDS = ["file_path", "file_name", "file_content_type", "file_size"]


def attach_file(receipt, upload):
    """Validates and uploads `upload`, sets file fields on `receipt` (unsaved). Returns the new path."""
    content_type, ext = validate_upload(upload)
    data = upload.read()
    path = f"{receipt.account_id}/{receipt.id}/{uuid.uuid4().hex}.{ext}"
    try:
        get_storage().upload(path, data, content_type)
    except StorageError as exc:
        logger.error("Storage upload failed: %s", exc)
        raise StorageUnavailable() from exc
    receipt.file_path = path
    receipt.file_name = os.path.basename(upload.name)[:255]
    receipt.file_content_type = content_type
    receipt.file_size = len(data)
    return path


def clear_file_fields(receipt):
    receipt.file_path = ""
    receipt.file_name = ""
    receipt.file_content_type = ""
    receipt.file_size = None
