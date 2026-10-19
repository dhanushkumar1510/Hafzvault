from datetime import date, timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APITestCase

from vault import storage
from vault.models import Account, Receipt

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32
JPG = b"\xff\xd8\xff\xe0" + b"\x00" * 32
PDF = b"%PDF-1.4\n%%EOF\n"
WEBP = b"RIFF\x24\x00\x00\x00WEBPVP8 " + b"\x00" * 32


def make_file(name, data, ctype):
    return SimpleUploadedFile(name, data, content_type=ctype)


class Base(APITestCase):
    def setUp(self):
        storage.MEMORY.clear()
        self.alice = Account.objects.create(username="alice", email="alice@example.com")
        self.bob = Account.objects.create(username="bob", email="bob@example.com")

    def login_as(self, account):
        self.client.credentials(
            HTTP_X_ACCOUNT_USERNAME=account.username, HTTP_X_ACCOUNT_EMAIL=account.email
        )

    def payload(self, **kw):
        data = {"name": "Laptop", "price": "1200.50", "purchase_date": "2026-01-15"}
        data.update(kw)
        return data

    def create_receipt(self, account=None, **kw):
        fields = {"name": "Item", "price": "10.00", "purchase_date": date(2026, 1, 1)}
        fields.update(kw)
        return Receipt.objects.create(account=account or self.alice, **fields)


class AccountTests(Base):
    def test_create_account(self):
        r = self.client.post("/api/accounts/", {"username": "carol", "email": "Carol@Example.com"}, format="json")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["email"], "carol@example.com")
        self.assertTrue(Account.objects.filter(username="carol").exists())

    def test_lookup_existing_matches(self):
        r = self.client.post("/api/accounts/lookup/", {"username": "Alice", "email": "ALICE@example.com"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["username"], "alice")

    def test_lookup_unknown_returns_404_with_code(self):
        r = self.client.post("/api/accounts/lookup/", {"username": "zed", "email": "z@example.com"}, format="json")
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.data["code"], "account_not_found")

    def test_username_with_different_email_is_mismatch(self):
        r = self.client.post("/api/accounts/lookup/", {"username": "alice", "email": "other@example.com"}, format="json")
        self.assertEqual(r.status_code, 409)
        self.assertEqual(r.data["code"], "username_email_mismatch")
        self.assertIn("does not match", r.data["detail"])

    def test_create_with_taken_username_is_rejected(self):
        r = self.client.post("/api/accounts/", {"username": "alice", "email": "new@example.com"}, format="json")
        self.assertEqual(r.status_code, 409)
        self.assertEqual(Account.objects.count(), 2)

    def test_email_with_different_username_is_rejected(self):
        r = self.client.post("/api/accounts/", {"username": "alice2", "email": "alice@example.com"}, format="json")
        self.assertEqual(r.status_code, 409)
        self.assertEqual(r.data["code"], "email_username_mismatch")

    def test_create_existing_pair_conflicts(self):
        r = self.client.post("/api/accounts/", {"username": "alice", "email": "alice@example.com"}, format="json")
        self.assertEqual(r.status_code, 409)
        self.assertEqual(r.data["code"], "account_exists")

    def test_invalid_username_and_email(self):
        r = self.client.post("/api/accounts/", {"username": "a b", "email": "nope"}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertIn("username", r.data)
        self.assertIn("email", r.data)

    def test_profile(self):
        self.login_as(self.alice)
        self.create_receipt()
        r = self.client.get("/api/profile/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["receipt_count"], 1)

    def test_no_password_fields_exist(self):
        names = {f.name for f in Account._meta.get_fields()}
        self.assertFalse({"password", "otp", "is_verified"} & names)


class AuthHeaderTests(Base):
    def test_missing_headers_rejected(self):
        self.assertEqual(self.client.get("/api/receipts/").status_code, 401)

    def test_mismatched_headers_rejected(self):
        self.client.credentials(HTTP_X_ACCOUNT_USERNAME="alice", HTTP_X_ACCOUNT_EMAIL="bob@example.com")
        self.assertEqual(self.client.get("/api/receipts/").status_code, 401)

    def test_health_is_public(self):
        self.assertEqual(self.client.get("/api/health/").status_code, 200)


class ReceiptCrudTests(Base):
    def setUp(self):
        super().setUp()
        self.login_as(self.alice)

    def test_create_and_retrieve(self):
        r = self.client.post("/api/receipts/", self.payload(warranty_date="2027-01-15", notes="n"), format="json")
        self.assertEqual(r.status_code, 201, r.data)
        self.assertFalse(r.data["has_file"])
        got = self.client.get(f"/api/receipts/{r.data['id']}/")
        self.assertEqual(got.status_code, 200)
        self.assertEqual(got.data["price"], "1200.50")
        self.assertEqual(Receipt.objects.get().account, self.alice)

    def test_update(self):
        rec = self.create_receipt()
        r = self.client.patch(f"/api/receipts/{rec.id}/", {"name": "Phone", "price": "99.99"}, format="json")
        self.assertEqual(r.status_code, 200)
        rec.refresh_from_db()
        self.assertEqual(rec.name, "Phone")

    def test_delete(self):
        rec = self.create_receipt()
        self.assertEqual(self.client.delete(f"/api/receipts/{rec.id}/").status_code, 204)
        self.assertFalse(Receipt.objects.exists())

    def test_validation_errors(self):
        for bad, field in [
            ({"name": "  "}, "name"),
            ({"price": "-5"}, "price"),
            ({"price": "abc"}, "price"),
            ({"purchase_date": "not-a-date"}, "purchase_date"),
            ({"warranty_date": "2020-01-01"}, "warranty_date"),
        ]:
            r = self.client.post("/api/receipts/", self.payload(**bad), format="json")
            self.assertEqual(r.status_code, 400, bad)
            self.assertIn(field, r.data)
        r = self.client.post("/api/receipts/", {}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertEqual({"name", "price", "purchase_date"}, set(r.data))

    def test_ownership_isolation(self):
        mine = self.create_receipt(name="Mine")
        theirs = self.create_receipt(account=self.bob, name="Theirs")
        names = [x["name"] for x in self.client.get("/api/receipts/").data]
        self.assertEqual(names, ["Mine"])
        self.assertEqual(self.client.get(f"/api/receipts/{theirs.id}/").status_code, 404)
        self.assertEqual(self.client.patch(f"/api/receipts/{theirs.id}/", {"name": "x"}, format="json").status_code, 404)
        self.assertEqual(self.client.delete(f"/api/receipts/{theirs.id}/").status_code, 404)
        self.assertEqual(self.client.get(f"/api/receipts/{theirs.id}/attachment/").status_code, 404)
        self.assertTrue(Receipt.objects.filter(id=theirs.id).exists())
        self.assertTrue(Receipt.objects.filter(id=mine.id).exists())

    def test_search_sort_filter(self):
        today = date.today()
        self.create_receipt(name="Banana Blender", purchase_date=date(2026, 3, 1), warranty_date=today + timedelta(days=5))
        self.create_receipt(name="apple Watch", purchase_date=date(2026, 1, 1), warranty_date=today - timedelta(days=5))
        self.create_receipt(name="Cable", purchase_date=date(2026, 2, 1))

        def names(qs):
            return [x["name"] for x in self.client.get(f"/api/receipts/?{qs}").data]

        self.assertEqual(names("q=blend"), ["Banana Blender"])
        self.assertEqual(names("ordering=name"), ["apple Watch", "Banana Blender", "Cable"])
        self.assertEqual(names("ordering=-name"), ["Cable", "Banana Blender", "apple Watch"])
        self.assertEqual(names("ordering=purchase_date"), ["apple Watch", "Cable", "Banana Blender"])
        self.assertEqual(names("ordering=-purchase_date"), ["Banana Blender", "Cable", "apple Watch"])
        self.assertEqual(names("ordering=warranty_date"), ["apple Watch", "Banana Blender", "Cable"])
        self.assertEqual(names("warranty=active"), ["Banana Blender"])
        self.assertEqual(names("warranty=expired"), ["apple Watch"])
        self.assertEqual(names("warranty=none"), ["Cable"])
        self.assertEqual(self.client.get("/api/receipts/?ordering=bogus").status_code, 400)
        self.assertEqual(self.client.get("/api/receipts/?warranty=bogus").status_code, 400)

    def test_summary(self):
        today = date.today()
        self.create_receipt(price="10.00", warranty_date=today + timedelta(days=10))
        self.create_receipt(price="5.50", warranty_date=today - timedelta(days=1))
        self.create_receipt(account=self.bob, price="999")
        r = self.client.get("/api/summary/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["receipt_count"], 2)
        self.assertEqual(r.data["total_spent"], "15.50")
        self.assertEqual(r.data["expiring_soon"], 1)
        self.assertEqual(r.data["expired_warranties"], 1)


class FileTests(Base):
    def setUp(self):
        super().setUp()
        self.login_as(self.alice)

    def post_with(self, f, **kw):
        return self.client.post("/api/receipts/", {**self.payload(**kw), "file": f}, format="multipart")

    def test_all_supported_types_upload(self):
        for name, data, ctype in [
            ("a.jpg", JPG, "image/jpeg"), ("a.jpeg", JPG, "image/jpeg"),
            ("a.png", PNG, "image/png"), ("a.webp", WEBP, "image/webp"),
            ("a.pdf", PDF, "application/pdf"),
        ]:
            r = self.post_with(make_file(name, data, ctype))
            self.assertEqual(r.status_code, 201, (name, r.data))
            self.assertTrue(r.data["has_file"])
            self.assertEqual(r.data["file_name"], name)
        self.assertEqual(len(storage.MEMORY.files), 5)

    def test_upload_stores_path_scoped_to_account_and_metadata(self):
        r = self.post_with(make_file("scan.png", PNG, "image/png"))
        rec = Receipt.objects.get(id=r.data["id"])
        self.assertTrue(rec.file_path.startswith(f"{self.alice.id}/{rec.id}/"))
        self.assertIn(rec.file_path, storage.MEMORY.files)
        self.assertEqual(rec.file_size, len(PNG))
        self.assertEqual(rec.file_content_type, "image/png")

    def test_rejects_bad_type_empty_spoofed_and_oversize(self):
        self.assertEqual(self.post_with(make_file("x.exe", b"MZ" + b"\x00" * 20, "application/octet-stream")).status_code, 400)
        self.assertEqual(self.post_with(make_file("x.png", b"", "image/png")).status_code, 400)
        r = self.post_with(make_file("x.png", b"not really a png at all", "image/png"))
        self.assertEqual(r.status_code, 400)
        self.assertIn("file", r.data)
        with override_settings(MAX_UPLOAD_BYTES=10):
            r = self.post_with(make_file("big.png", PNG, "image/png"))
            self.assertEqual(r.status_code, 400)
        self.assertFalse(Receipt.objects.exists())
        self.assertFalse(storage.MEMORY.files)

    def test_storage_failure_returns_502_and_creates_nothing(self):
        storage.MEMORY.fail = True
        r = self.post_with(make_file("a.png", PNG, "image/png"))
        self.assertEqual(r.status_code, 502)
        self.assertFalse(Receipt.objects.exists())

    def test_replace_via_attachment_endpoint_deletes_old_file(self):
        r = self.post_with(make_file("a.png", PNG, "image/png"))
        rid = r.data["id"]
        old = Receipt.objects.get(id=rid).file_path
        r2 = self.client.put(f"/api/receipts/{rid}/attachment/", {"file": make_file("b.pdf", PDF, "application/pdf")}, format="multipart")
        self.assertEqual(r2.status_code, 200, r2.data)
        new = Receipt.objects.get(id=rid).file_path
        self.assertNotEqual(old, new)
        self.assertNotIn(old, storage.MEMORY.files)
        self.assertIn(new, storage.MEMORY.files)
        self.assertEqual(Receipt.objects.get(id=rid).file_content_type, "application/pdf")

    def test_replace_via_patch_and_remove_file_flag(self):
        r = self.post_with(make_file("a.png", PNG, "image/png"))
        rid = r.data["id"]
        r2 = self.client.patch(f"/api/receipts/{rid}/", {"file": make_file("b.jpg", JPG, "image/jpeg")}, format="multipart")
        self.assertEqual(r2.status_code, 200, r2.data)
        self.assertEqual(len(storage.MEMORY.files), 1)
        r3 = self.client.patch(f"/api/receipts/{rid}/", {"remove_file": True}, format="json")
        self.assertEqual(r3.status_code, 200)
        self.assertFalse(r3.data["has_file"])
        self.assertFalse(storage.MEMORY.files)

    def test_failed_replacement_keeps_old_file(self):
        r = self.post_with(make_file("a.png", PNG, "image/png"))
        rid = r.data["id"]
        storage.MEMORY.fail = True
        r2 = self.client.put(f"/api/receipts/{rid}/attachment/", {"file": make_file("b.png", PNG, "image/png")}, format="multipart")
        self.assertEqual(r2.status_code, 502)
        self.assertTrue(Receipt.objects.get(id=rid).file_path in storage.MEMORY.files)

    def test_delete_attachment_endpoint(self):
        rid = self.post_with(make_file("a.png", PNG, "image/png")).data["id"]
        self.assertEqual(self.client.delete(f"/api/receipts/{rid}/attachment/").status_code, 200)
        self.assertFalse(storage.MEMORY.files)
        self.assertEqual(self.client.delete(f"/api/receipts/{rid}/attachment/").status_code, 404)

    def test_delete_receipt_removes_stored_file(self):
        rid = self.post_with(make_file("a.png", PNG, "image/png")).data["id"]
        self.assertEqual(self.client.delete(f"/api/receipts/{rid}/").status_code, 204)
        self.assertFalse(storage.MEMORY.files)

    def test_attachment_info(self):
        rid = self.post_with(make_file("a.pdf", PDF, "application/pdf")).data["id"]
        r = self.client.get(f"/api/receipts/{rid}/attachment/")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.data["url"].startswith("memory://"))
        self.assertEqual(r.data["content_type"], "application/pdf")
        plain = self.create_receipt()
        self.assertEqual(self.client.get(f"/api/receipts/{plain.id}/attachment/").status_code, 404)

    def test_put_without_file_is_400(self):
        rec = self.create_receipt()
        r = self.client.put(f"/api/receipts/{rec.id}/attachment/", {}, format="multipart")
        self.assertEqual(r.status_code, 400)
