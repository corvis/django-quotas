#
#  Copyright 2025 by Dmitry Berezovsky, MIT License
#
import abc
from typing import cast
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as gt

from django_quotas.base.dto import Quota, ValuePerBucket
from django_quotas.config import DjangoQuotasConfig as cfg

__all__ = ["BaseQuotaModel", "DefaultQuotaModel"]


class BaseQuotaModel(models.Model):
    """Base model for quotas that can be converted to Quota interface when needed."""

    class Meta:
        abstract = True

    owner_tag = models.CharField(max_length=300, null=True, blank=True)
    feature_name = models.CharField(max_length=300, null=False, blank=False)
    hourly_limit = models.IntegerField(null=True, blank=True)
    daily_limit = models.IntegerField(null=True, blank=True)
    monthly_limit = models.IntegerField(null=True, blank=True)
    total_limit = models.IntegerField(null=True, blank=True)

    @property
    def get_limits(self) -> ValuePerBucket:
        """Return the quota limits as a ValuePerBucket instance.

        :return: ValuePerBucket with limits for each bucket.
        """
        return ValuePerBucket(
            hourly=self.hourly_limit, daily=self.daily_limit, monthly=self.monthly_limit, total=self.total_limit
        )

    @property
    @abc.abstractmethod
    def id(self) -> uuid.UUID:
        """Return the unique identifier for the quota instance.

        :return: UUID of the quota instance.
        """
        ...


class _QuotaModelMetaclass(type(models.Model), abc.ABCMeta, type(Quota)):  # type: ignore[misc]
    """Specific metaclass to satisfy django migrations creating class in a non-standard way."""

    pass


class DefaultQuotaModel(BaseQuotaModel, Quota, metaclass=_QuotaModelMetaclass):  # type: ignore[metaclass]
    """Model for actual quota assigned to a user."""

    class Meta:
        abstract = True
        db_table = f'"{cfg.TABLE_SCHEMA}"."{cfg.TABLE_PREFIX}_quota"'
        verbose_name = gt("Account Quota")
        unique_together = ("account", "feature_name")
        indexes = (models.Index(fields=["account", "feature_name"]),)

    account: models.Model = models.ForeignKey(  # type: ignore[assignment]
        cfg.QUOTA_RELATED_ACCOUNT_MODEL,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="quotas",
        db_index=True,
    )

    @property
    def id(self) -> uuid.UUID:
        """Return the unique identifier for the quota instance.

        :return: UUID of the quota instance.
        """
        return self.pk

    @property
    def account_id(self) -> uuid.UUID:
        """Return the unique identifier for the associated account.

        :return: Account UUID.
        """
        return cast(uuid.UUID, self.account.pk)
