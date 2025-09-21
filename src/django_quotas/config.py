#
#  Copyright 2025 by Dmitry Berezovsky, MIT License
#
from functools import cached_property
from typing import TYPE_CHECKING, Final

from django.conf import settings
from django.db import models

from django_quotas.utils import get_model_by_name

if TYPE_CHECKING:
    from django_quotas.models import BaseQuotaModel


__all__ = ["__DjangoQuotasConfig"]


class __DjangoQuotasConfig:
    """Configuration accessor for django_quotas settings and related models."""

    SETTINGS_PREFIX: Final[str] = "DJANGO_QUOTAS"

    @cached_property
    def TABLE_PREFIX(self) -> str:
        """Return the table prefix for quota tables.

        :return: Table prefix string.
        """
        return getattr(settings, f"{self.SETTINGS_PREFIX}_TABLE_PREFIX", "django_quotas")

    @cached_property
    def TABLE_SCHEMA(self) -> str:
        """Return the schema name for quota tables.

        :return: Schema name string.
        """
        return getattr(settings, f"{self.SETTINGS_PREFIX}_TABLE_SCHEMA", "public")

    @cached_property
    def QUOTA_MODEL(self) -> str:
        """Get the full model name for the quota model.

        :return: Model name string.
        """
        return getattr(settings, f"{self.SETTINGS_PREFIX}_QUOTA_MODEL_NAME", "django_quotas.QuotaModel")

    @cached_property
    def QUOTA_RELATED_ACCOUNT_MODEL(self) -> str:
        """Get the related account model name for quotas.

        :return: Related account model name string.
        """
        return getattr(settings, f"{self.SETTINGS_PREFIX}_QUOTA_RELATED_ACCOUNT_MODEL_NAME", "auth.User")

    @cached_property
    def quota_cls(self) -> type[BaseQuotaModel]:
        """Get the quota model class.

        :return: Quota model class.
        """
        return get_model_by_name(self.QUOTA_MODEL)  # type: ignore

    @cached_property
    def quota_related_account_cls(self) -> type[models.Model]:
        """Get the related account model class for quotas.

        :return: Related account model class.
        """
        return get_model_by_name(self.QUOTA_RELATED_ACCOUNT_MODEL)


DjangoQuotasConfig = __DjangoQuotasConfig()
