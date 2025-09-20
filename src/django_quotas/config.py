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


class __DjangoQuotasConfig:
    SETTINGS_PREFIX: Final[str] = "DJANGO_QUOTAS"

    @cached_property
    def TABLE_PREFIX(self) -> str:
        return getattr(settings, f"{self.SETTINGS_PREFIX}_TABLE_PREFIX", "django_quotas")

    @cached_property
    def TABLE_SCHEMA(self):
        return getattr(settings, f"{self.SETTINGS_PREFIX}_TABLE_SCHEMA", "public")

    @cached_property
    def QUOTA_MODEL(self) -> str:
        return getattr(settings, f"{self.SETTINGS_PREFIX}_QUOTA_MODEL_NAME", "django_quotas.QuotaModel")

    @cached_property
    def QUOTA_RELATED_ACCOUNT_MODEL(self) -> str:
        return getattr(settings, f"{self.SETTINGS_PREFIX}_QUOTA_RELATED_ACCOUNT_MODEL")

    @cached_property
    def quota_cls(self) -> type[BaseQuotaModel]:
        return get_model_by_name(self.QUOTA_MODEL)  # type: ignore

    @cached_property
    def quota_related_account_cls(self) -> type[models.Model]:
        return get_model_by_name(self.QUOTA_RELATED_ACCOUNT_MODEL)  # type: ignore


DjangoQuotasConfig = __DjangoQuotasConfig()
