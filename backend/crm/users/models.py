from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils import FieldTracker

from crm.core.models import BaseUser


class User(BaseUser, AbstractUser):
    class Roles(models.TextChoices):
        SUPERUSER = "superuser", _("Суперпользователь")
        ADMIN = "admin", _("Администратор")
        MANAGER = "manager", _("Менеджер")

    role = models.CharField(_("Роль"), max_length=10, choices=Roles.choices, default=Roles.MANAGER)
    is_active = models.BooleanField(_("Активен"), default=True)
    tracker = FieldTracker()

    def __str__(self):
        return str(self.username)

    @property
    def is_crm_superuser(self):
        return self.role == self.Roles.SUPERUSER

    @property
    def is_crm_admin(self):
        return self.role == self.Roles.ADMIN

    @property
    def is_crm_manager(self):
        return self.role == self.Roles.MANAGER
