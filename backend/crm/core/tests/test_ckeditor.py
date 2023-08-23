from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import resolve, reverse

from crm.users.tests.factories import UserFactory


class CKEditorTests(TestCase):
    def setUp(self):
        self.credentials = {"username": "testuser", "password": "testpassword"}
        # create users
        self.user = UserFactory(**self.credentials)
        # create test image
        self.image = open("crm/static/img/tests/img_150x150.png", "rb").read()
        self.image_file = SimpleUploadedFile("image.png", self.image, content_type="image/png")

    def test_browse_url(self):
        self.assertEqual(reverse("ckeditor_browse"), "/ckeditor/browse/")
        self.assertEqual(resolve("/ckeditor/browse/").view_name, "ckeditor_browse")

    def test_upload_url(self):
        self.assertEqual(reverse("ckeditor_upload"), "/ckeditor/upload/")
        self.assertEqual(resolve("/ckeditor/upload/").view_name, "ckeditor_upload")

    def test_browse_anon(self):
        response = self.client.get(reverse("ckeditor_browse"))
        self.assertEqual(response.status_code, 302)

    def test_image_upload(self):
        self.client.login(**self.credentials)
        response = self.client.post(reverse("ckeditor_upload"), {"upload": self.image_file})
        # Test response
        self.assertEqual(response.status_code, 200)
        self.assertIn("url", response.json())
        self.assertTrue(response.json()["url"].startswith("/media/uploads/"))

    def test_image_upload_anon(self):
        response = self.client.post(reverse("ckeditor_upload"), {"upload": self.image_file})
        self.assertEqual(response.status_code, 302)
