#
#  Copyright 2025 by Dmitry Berezovsky, MIT License
#
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as gt


class QuotasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_quotas"
    label = "django_quotas"
    verbose_name = gt("Quotas")
    default = True
