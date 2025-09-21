#
#  Copyright 2025 by Dmitry Berezovsky, MIT License
#
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as gt

from django_quotas.config import DjangoQuotasConfig as cfg


class QuotaUsageModel(models.Model):
    """Model for tracking quota usage per account, feature, and time point."""

    class Meta:
        db_table = f"{cfg.TABLE_PREFIX}_quota_usage"
        verbose_name = gt("Quota Usage")
        unique_together = ("account", "feature_name", "point_in_time")
        indexes = (
            models.Index(fields=["account", "feature_name", "point_in_time"]),
            models.Index(fields=["account", "point_in_time"]),
        )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(  # type: ignore[call-arg]
        cfg.QUOTA_RELATED_ACCOUNT_MODEL, null=False, blank=False, on_delete=models.CASCADE, swappable=True
    )
    feature_name = models.CharField(max_length=300, null=False, blank=False)
    point_in_time = models.DateTimeField(null=False, blank=False)
    usage_count = models.IntegerField(null=False, blank=False, default=0)

    @property
    def account_id(self) -> uuid.UUID:  # type: ignore[no-untyped-def]
        """Return the unique identifier for the associated account.

        :return: Account UUID.
        """
        return self.account.pk
