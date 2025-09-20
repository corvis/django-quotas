#
#  Copyright 2025 by Dmitry Berezovsky, MIT License
#
from functools import cached_property
from typing import TYPE_CHECKING, Final

from django.conf import settings

from django_quotas.utils import get_model_by_name

if TYPE_CHECKING:
    from django_quotas.impl_db.models import QuotaUsageModel


class __DjangoQuotasDbConfig:
    SETTINGS_PREFIX: Final[str] = "DJANGO_QUOTAS"

    @cached_property
    def QUOTA_USAGE_MODEL(self) -> str:
        return getattr(settings, f"{self.SETTINGS_PREFIX}_IMPL_DB_USAGE_MODEL_NAME", "django_quotas_db.QuotaUsageModel")

    @cached_property
    def quota_usage_cls(self) -> type["QuotaUsageModel"]:
        return get_model_by_name(self.QUOTA_USAGE_MODEL)  # type: ignore


DjangoQuotasDbConfig = __DjangoQuotasDbConfig()
