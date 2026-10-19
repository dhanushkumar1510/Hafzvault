import logging
from urllib.parse import quote

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class StorageError(Exception):
    pass


class SupabaseStorage:
    """Talks to the Supabase Storage REST API with the service-role key (server-side only)."""

    def __init__(self):
        if not (settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY):
            raise StorageError("Supabase storage is not configured.")
        self.base = f"{settings.SUPABASE_URL}/storage/v1"
        self.bucket = settings.SUPABASE_BUCKET
        self.auth = {
            "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
            "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
        }

    def _object_url(self, prefix, path):
        return f"{self.base}/{prefix}/{self.bucket}/{quote(path, safe='/')}"

    def upload(self, path, data, content_type):
        try:
            r = requests.post(
                self._object_url("object", path),
                headers={**self.auth, "Content-Type": content_type, "x-upsert": "false"},
                data=data,
                timeout=45,
            )
        except requests.RequestException as exc:
            raise StorageError(f"Upload failed: {exc}") from exc
        if r.status_code not in (200, 201):
            raise StorageError(f"Upload failed ({r.status_code}): {r.text[:200]}")

    def delete(self, path):
        try:
            r = requests.delete(self._object_url("object", path), headers=self.auth, timeout=20)
        except requests.RequestException as exc:
            raise StorageError(f"Delete failed: {exc}") from exc
        if r.status_code not in (200, 204, 404):
            raise StorageError(f"Delete failed ({r.status_code}): {r.text[:200]}")

    def signed_url(self, path, expires_in):
        try:
            r = requests.post(
                self._object_url("object/sign", path),
                headers=self.auth,
                json={"expiresIn": expires_in},
                timeout=20,
            )
        except requests.RequestException as exc:
            raise StorageError(f"Could not sign URL: {exc}") from exc
        if r.status_code != 200:
            raise StorageError(f"Could not sign URL ({r.status_code}): {r.text[:200]}")
        signed = r.json().get("signedURL", "")
        if not signed:
            raise StorageError("Supabase returned no signed URL.")
        if signed.startswith("http"):
            return signed
        if signed.startswith("/storage/v1"):
            return f"{settings.SUPABASE_URL}{signed}"
        return f"{self.base}{signed}"


class MemoryStorage:
    """In-memory backend used by the test suite."""

    def __init__(self):
        self.files = {}
        self.fail = False

    def clear(self):
        self.files.clear()
        self.fail = False

    def upload(self, path, data, content_type):
        if self.fail:
            raise StorageError("simulated failure")
        self.files[path] = (data, content_type)

    def delete(self, path):
        self.files.pop(path, None)

    def signed_url(self, path, expires_in):
        if path not in self.files:
            raise StorageError("missing")
        return f"memory://{path}"


MEMORY = MemoryStorage()


def get_storage():
    if settings.STORAGE_BACKEND == "memory":
        return MEMORY
    return SupabaseStorage()


def delete_quietly(path):
    """Best-effort delete; failures are logged so orphans can be traced."""
    if not path:
        return
    try:
        get_storage().delete(path)
    except StorageError:
        logger.warning("Could not delete stored file %s; it may be orphaned.", path)
