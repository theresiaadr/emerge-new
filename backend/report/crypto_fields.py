import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken
from django import forms
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models


def _get_fernet():
    key = (getattr(settings, "FIELD_ENCRYPTION_KEY", "") or "").strip()
    if not key:
        if not settings.DEBUG:
            raise ImproperlyConfigured(
                "DJANGO_FIELD_ENCRYPTION_KEY wajib diisi saat DEBUG=0."
            )
        digest = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
        key = base64.urlsafe_b64encode(digest).decode()
    try:
        return Fernet(key.encode())
    except (ValueError, TypeError) as exc:
        raise ImproperlyConfigured("DJANGO_FIELD_ENCRYPTION_KEY tidak valid.") from exc


def encrypt(value: str) -> str:
    return _get_fernet().encrypt(value.encode()).decode()


def decrypt(value: str) -> str:
    try:
        return _get_fernet().decrypt(value.encode()).decode()
    except (InvalidToken, ValueError):
        return value


class EncryptedMixin:
    def from_db_value(self, value, expression, connection):
        if value in (None, ""):
            return value
        return decrypt(value)

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value in (None, ""):
            return value
        return encrypt(str(value))

    def get_lookup(self, lookup_name):
        if lookup_name not in ("exact", "isnull", "in"):
            raise NotImplementedError("Lookup tidak didukung pada field terenkripsi.")
        return super().get_lookup(lookup_name)


class EncryptedTextField(EncryptedMixin, models.TextField):
    pass


class EncryptedCharField(EncryptedMixin, models.TextField):
    def __init__(self, *args, max_length=255, **kwargs):
        self.form_max_length = max_length
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["max_length"] = self.form_max_length
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        defaults = {"form_class": forms.CharField, "max_length": self.form_max_length}
        defaults.update(kwargs)
        defaults.pop("widget", None)
        return models.Field.formfield(self, **defaults)
