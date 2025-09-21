#
#  Copyright 2025 by Dmitry Berezovsky, MIT License
#
import asyncio
import datetime
from typing import Any, cast
import uuid

from asgiref.sync import sync_to_async
from django.db import transaction
from django.db.models import F, Sum

from django_quotas.backends.db.config import DjangoQuotasDbConfig as cfg_db
from django_quotas.backends.db.models import QuotaUsageModel
from django_quotas.base.dto import Quota, QuotaStats, QuotaStatus, ValuePerBucket
from django_quotas.base.service import QuotaService
from django_quotas.config import DjangoQuotasConfig as cfg
from django_quotas.models import BaseQuotaModel
from django_quotas.utils import datetime_now


class DbQuotaService(QuotaService):
    def register_usage(self, account_id: uuid.UUID, feature_name: str, increment: int = 1) -> None:
        """Register usage for the given account and feature.

        :param account_id: The account ID.
        :param feature_name: The feature name.
        :param increment: The value to be added to quota usage.
        """
        # Current hour
        current_time = datetime_now().replace(minute=0, second=0, microsecond=0)

        with transaction.atomic():
            usage, _ = cfg_db.quota_usage_cls.objects.get_or_create(
                account_id=account_id, feature_name=feature_name, point_in_time=current_time
            )
            cfg_db.quota_usage_cls.objects.filter(id=usage.id, point_in_time=current_time).update(
                usage_count=F("usage_count") + increment
            )

    async def aregister_usage(self, account_id: uuid.UUID, feature_name: str | set[str], increment: int = 1) -> None:
        """Asynchronously register usage for the given account and feature(s).

        :param account_id: The account ID.
        :param feature_name: The feature name or set of feature names.
        :param increment: The value to be added to quota usage.
        """
        if isinstance(feature_name, str):
            feature_names = {feature_name}
        else:
            feature_names = feature_name
        await asyncio.gather(*[sync_to_async(self.register_usage)(account_id, f, increment) for f in feature_names])

    def get_quotas_utilization(self, account_id: uuid.UUID, feature_name: str | set[str] | None) -> QuotaStats:
        """Get the quota utilization for the given account and features.

        :param account_id: The account ID.
        :param feature_name: Name of the feature or a set of feature names. None means all features having quotas.
        :return: QuotaStats instance with utilization data.
        """
        if feature_name and isinstance(feature_name, str):
            feature_name = {feature_name}
        current_hour = self.__get_current_hour()  # Current hour
        today = current_hour.replace(hour=0, minute=0, second=0, microsecond=0)  # Current day
        first__day_of_month = today.replace(day=1)
        quotas_qs = cfg.quota_cls.objects.filter(account_id=account_id)  # type: ignore[attr-defined]
        if feature_name:
            quotas_qs = quotas_qs.filter(feature_name__in=feature_name)

        quotas: list[BaseQuotaModel] = list(quotas_qs)
        feature_name = {quota.feature_name for quota in quotas}

        # Calculate usage per bucket

        hourly_usage = self.__create_usage_for_bucket(account_id, feature_name, point_in_time=current_hour)
        daily_usage = self.__create_usage_for_bucket(account_id, feature_name, point_in_time__date=today)
        monthly_usage = self.__create_usage_for_bucket(
            account_id, feature_name, point_in_time__date__gte=first__day_of_month
        )
        total_usage = self.__create_usage_for_bucket(account_id, feature_name)

        result = QuotaStats(account_id=account_id, feature_stats={})

        # Compile the stats for each feature
        for quota in quotas:
            result.feature_stats[quota.feature_name] = QuotaStatus(
                quota_id=quota.id,
                limits=ValuePerBucket(
                    hourly=quota.hourly_limit,
                    daily=quota.daily_limit,
                    monthly=quota.monthly_limit,
                    total=quota.total_limit,
                ),
                usage=ValuePerBucket(
                    hourly=hourly_usage.get(quota.feature_name, 0),
                    daily=daily_usage.get(quota.feature_name, 0),
                    monthly=monthly_usage.get(quota.feature_name, 0),
                    total=total_usage.get(quota.feature_name, 0),
                ),
            )

        return result

    async def aget_quotas_utilization(self, account_id: uuid.UUID, feature_name: str | set[str] | None) -> QuotaStats:
        return await sync_to_async(self.get_quotas_utilization)(account_id, feature_name)

    def set_quota(
        self, account_id: uuid.UUID | int, feature_name: str, limits: ValuePerBucket, owner_tag: str | None = None
    ) -> Quota:
        quota_model, _ = cfg.quota_cls.objects.update_or_create(  # type: ignore[attr-defined]
            account_id=account_id,
            feature_name=feature_name,
            defaults={
                "hourly_limit": limits.hourly,
                "daily_limit": limits.daily,
                "monthly_limit": limits.monthly,
                "total_limit": limits.total,
                "owner_tag": owner_tag,
            },
        )
        return quota_model

    async def aset_quota(
        self, account_id: uuid.UUID, feature_name: str, limits: ValuePerBucket, owner_tag: str | None = None
    ) -> Quota:
        return await sync_to_async(self.set_quota)(account_id, feature_name, limits, owner_tag)

    @staticmethod
    def __get_current_hour() -> datetime.datetime:
        return datetime_now().replace(minute=0, second=0, microsecond=0)

    @staticmethod
    def __create_usage_for_bucket(
        account_id: uuid.UUID, feature_name: set[str] | None, **extra_query_args: Any
    ) -> dict[str, int]:
        """
        Get usage for the given account and, optionally, list of specific features.

        Returns a dict with feature names as keys and usage as values.
        """
        qs = QuotaUsageModel.objects.filter(
            account_id=cast(Any, account_id), feature_name__in=feature_name, **extra_query_args
        )
        if feature_name is not None:
            qs = qs.filter(feature_name__in=feature_name)
        qs_annotated = qs.values("feature_name").annotate(total_usage=Sum("usage_count"))
        return {item["feature_name"]: item["total_usage"] for item in qs_annotated}
