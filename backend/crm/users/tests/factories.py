from collections.abc import Sequence
from typing import Any

from django.contrib.auth import get_user_model
from factory import Faker, post_generation
from factory.django import DjangoModelFactory
from faker import Faker as OriginalFaker

User = get_user_model()
ru_fake = OriginalFaker(locale="ru_RU")


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ["username"]

    username = Faker("user_name")
    email = Faker("email")
    phone_number = Faker("phone_number", locale="ru_RU")
    first_name = Faker("first_name")
    middle_name = Faker("last_name")
    last_name = Faker("last_name")
    is_active = True

    @post_generation
    def password(self, create: bool, extracted: Sequence[Any], **kwargs):
        password = (
            extracted
            if extracted
            else Faker(
                "password",
                length=42,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True,
            ).evaluate(None, None, extra={"locale": None})
        )
        self.set_password(password)


class SuperUserFactory(UserFactory):
    role = User.Roles.SUPERUSER


class AdminUserFactory(UserFactory):
    role = User.Roles.ADMIN


class ManagerUserFactory(UserFactory):
    role = User.Roles.MANAGER
