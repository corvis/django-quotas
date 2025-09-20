#
#  Copyright 2025 by Dmitry Berezovsky, MIT License
#
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as gt


class QuotasDbConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_quotas.impl_db"
    label = "django_quotas_db"
    verbose_name = gt("Quotas DB Impl")
    default = True
