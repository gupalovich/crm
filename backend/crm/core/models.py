from django.db import models
from django.utils.translation import gettext_lazy as _

from .validators import validate_phone_number


class BaseModel(models.Model):
    """Model with created_at, updated_at fields"""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseUser(BaseModel):
    """BaseUser fields for User and Customer models"""

    first_name = models.CharField(_("Имя"), max_length=50)
    middle_name = models.CharField(_("Отчество"), max_length=50, blank=True)
    last_name = models.CharField(_("Фамилия"), max_length=50)
    email = models.EmailField(_("Email адресс"), blank=True, default="")
    phone_number = models.CharField(
        _("Номер телефона"),
        max_length=30,
        validators=[validate_phone_number],
    )

    class Meta:
        abstract = True
