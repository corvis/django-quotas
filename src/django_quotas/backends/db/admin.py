#
#  Copyright 2025 by Dmitry Berezovsky, MIT License
#
from django.contrib import admin
from django.http import HttpRequest

from django_quotas.backends.db.models import QuotaUsageModel
from django_quotas.config import DjangoQuotasConfig as cfg


@admin.register(QuotaUsageModel)
class QuotaUsageAdmin(cfg.base_admin_cls()):  # type: ignore[misc]
    def has_add_permission(self, request: HttpRequest) -> bool:
        return False
