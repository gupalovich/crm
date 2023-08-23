from io import BytesIO

import pytest
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import TestCase
from PIL import Image

from ..validators import ValidationError, validate_image_size, validate_phone_number


def test_validate_phone_number_valid():
    test_cases = ["+79234567890", "+7 (923) 456-78-90", "89923456789"]
    for case in test_cases:
        validate_phone_number(case)


def test_validate_phone_number_invalid():
    test_cases = ["+19234567890", "(923) 456-78-90", "899234567890"]
    for case in test_cases:
        with pytest.raises(ValidationError):
            validate_phone_number(case)


class ValidateImageSizeTests(TestCase):
    def setUp(self):
        # image
        self.image_data = self.load_image_data("crm/static/img/tests/img_150x150.png")
        self.image = self.create_in_memory_uploaded_file(self.image_data)
        # image sm
        self.image_sm_data = self.load_image_data("crm/static/img/tests/img_50x50.png")
        self.image_sm = self.create_in_memory_uploaded_file(self.image_sm_data)
        # image lg
        self.image_lg_data = self.load_image_data("crm/static/img/tests/img_1500x1500.png")
        self.image_lg = self.create_in_memory_uploaded_file(self.image_lg_data)

    def load_image_data(self, path):
        return open(path, "rb").read()

    def create_in_memory_uploaded_file(self, image_data):
        image = InMemoryUploadedFile(image_data, None, "image.png", "image/png", len(image_data), None)
        image.image = Image.open(BytesIO(image_data))
        return image

    def test_valid_cases(self):
        test_cases = [  # target_image, validation kwargs
            (self.image, {}),
            (self.image_sm, {}),
            (self.image_lg, {}),
        ]
        for image, kwargs in test_cases:
            validate_image_size(image, **kwargs)

    def test_invalid_cases(self):
        test_cases = [  # target_image, error count, validation kwargs
            (self.image_sm, 1, {"min_w": 51, "min_h": 51}),
            (self.image_lg, 1, {"max_w": 1499, "max_h": 1499}),
            (self.image_lg, 1, {"max_size_kb": 5}),  # image size is 6kb
            (self.image_lg, 2, {"max_size_kb": 5, "max_w": 1499, "max_h": 1499}),
        ]
        for image, error_count, kwargs in test_cases:
            with self.assertRaises(ValidationError) as context:
                validate_image_size(image, **kwargs)
            self.assertEqual(len(context.exception.messages), error_count)
