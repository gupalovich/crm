from django.test import TestCase
from qrcode.image.pil import PilImage

from ..utils import convert_img_to_base64, generate_qr_code


class TestUtils(TestCase):
    def setUp(self):
        pass

    def test_generate_qr_code(self):
        qr_code = generate_qr_code("test")
        self.assertIsInstance(qr_code, PilImage)

    def test_convert_img_to_base64(self):
        qr_code = generate_qr_code("test")
        qr_code_base64 = convert_img_to_base64(qr_code)
        self.assertIn("data:image/png;base64,", qr_code_base64)
        self.assertIsInstance(qr_code_base64, str)
