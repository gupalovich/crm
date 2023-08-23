from django.db import models
from django.test import TestCase

from ..models import BaseModel, BaseUser


class BaseModelTests(TestCase):
    def test_init(self):
        with self.assertRaises(TypeError):
            BaseModel()

    def test_fields(self):
        self.assertTrue(BaseModel.created_at)
        self.assertTrue(BaseModel.updated_at)


class BaseUserTests(TestCase):
    def test_init(self):
        with self.assertRaises(TypeError):
            BaseUser()

    def test_fields(self):
        self.assertTrue(BaseUser.first_name)
        self.assertTrue(BaseUser.middle_name)
        self.assertTrue(BaseUser.last_name)
        self.assertTrue(BaseUser.email)
        self.assertTrue(BaseUser.phone_number)
