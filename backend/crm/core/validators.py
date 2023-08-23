import re

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.forms import ValidationError


def validate_phone_number(value: str) -> None:
    # Remove all non-numeric symbols
    value = re.sub(r"\D", "", value)
    # Check if the number starts with 7 or 8 and has a length of 11 digits
    if not re.match(r"^[78]\d{10}$", value):
        raise ValidationError("Номер телефона должен состоять из 11 цифр и начинаться с '8' или '7'.")


def validate_image_size(
    image: InMemoryUploadedFile,
    max_size_kb: int = 3000,
    max_w: int = 3000,
    max_h: int = 3000,
    min_w: int = 50,
    min_h: int = 50,
) -> None:
    max_size = max_size_kb * 1024
    errors = []

    if image.size > max_size:
        msg = f"Размер изображения не должен превышать {round(max_size / 1024 / 1000, 2)}mb"
        errors.append(msg)

    width, height = image.image.size
    if width > max_w or height > max_h:
        msg = f"Разрешение изображения не должно превышать - {max_w}x{max_h}."
        errors.append(msg)
    if width < min_w or height < min_h:
        msg = f"Разрешение изображения не должно быть меньше - {min_w}x{min_h}."
        errors.append(msg)

    if errors:
        raise ValidationError(errors)
