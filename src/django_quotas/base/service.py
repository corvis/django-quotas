#
#  Copyright 2025 by Dmitry Berezovsky, MIT License
#
import abc
from collections import defaultdict
import uuid

from asgiref.sync import sync_to_async

from django_quotas.base.dto import Quota, QuotaBucket, QuotaStats, QuotaUseForBucket, ValuePerBucket

__all__ = [
    "QuotaExceededError",
    "QuotaService",
]


class QuotaExceededError(Exception):
    """Exception raised when a quota is exceeded for an account and feature(s).

    :param account_name: The account UUID.
    :param exceeded_features: Mapping of feature names to exceeded bucket stats.
    """

    def __init__(self, account_name: uuid.UUID, exceeded_features: dict[str, list[QuotaUseForBucket]]):
        self.account_id = account_name
        self._exceeded_features_stats = exceeded_features
        super().__init__(self.__generate_detailed_message())

    def get_exceeded_features(self) -> set[str]:
        """Get the set of feature names for which quotas are exceeded.

        :return: Set of feature names.
        """
        return set(self._exceeded_features_stats.keys())

    def get_stats_per_feature(self) -> dict[str, list[QuotaUseForBucket]]:
        """Get the exceeded stats per feature.

        :return: Mapping of feature names to list of QuotaUseForBucket.
        """
        return self._exceeded_features_stats

    def __generate_detailed_message(self) -> str:
        msg = self.__generate_msg() + "\nDetails:"
        for feature, stats in self._exceeded_features_stats.items():
            msg += f"\n{feature}: "
            buckets = []
            for stat in stats:
                buckets.append(f"{stat.bucket_name}({stat.current_usage}/{stat.limit})")
            msg += ", ".join(buckets)
        return msg

    def __generate_msg(self) -> str:
        return f"Quota exceeded for account {self.account_id}. Exceeded features: {self.get_exceeded_features()}"


class QuotaService(metaclass=abc.ABCMeta):
    """Abstract base class for quota service implementations."""

    def ensure_quota_or_raise(
        self, account_id: uuid.UUID, feature_name: str | set[str], potential_increase: int = 1
    ) -> None:
        """
        Ensure that the quota for the given account and feature is not exceeded.

        If the quota is exceeded, raise a QuotaExceededError.
        :param account_id: The account ID.
        :param feature_name: The feature name or set of feature names.
        :param potential_increase: The potential increase in usage.\
            Current utilization + potential increase must be less than the quota.
        :raise QuotaExceededError: If the quota is exceeded.
        """
        feature_names: set[str] = {feature_name} if isinstance(feature_name, str) else feature_name
        utilization = self.get_quotas_utilization(account_id, feature_name)
        exceeded_features: dict[str, list[QuotaUseForBucket]] = defaultdict(list)
        for feature in feature_names:
            if feature not in utilization.feature_stats:
                continue  # this means we have no quota for this specific feature
            status = utilization.feature_stats[feature]
            quota_buckets = [
                (QuotaBucket.HOURLY, status.usage.hourly or 0, status.limits.hourly),
                (QuotaBucket.DAILY, status.usage.daily or 0, status.limits.daily),
                (QuotaBucket.MONTHLY, status.usage.monthly or 0, status.limits.monthly),
                (QuotaBucket.TOTAL, status.usage.total or 0, status.limits.total),
            ]

            for bucket_name, current_usage, limit in quota_buckets:
                if limit is not None and current_usage + potential_increase > limit:
                    exceeded_features[feature].append(
                        QuotaUseForBucket(
                            bucket_name=bucket_name,
                            current_usage=current_usage,
                            limit=limit,
                            quota_id=status.quota_id,
                        )
                    )
        if exceeded_features:
            raise QuotaExceededError(account_id, exceeded_features)

    async def aensure_quota_or_raise(
        self, account_id: uuid.UUID, feature_name: str | set[str], potential_increase: int = 1
    ) -> None:
        """
        Ensure that the quota for the given account and feature is not exceeded.

        If the quota is exceeded, raise a QuotaExceededError.
        :param account_id: The account ID.
        :param feature_name: The feature name.
        :param potential_increase: The potential increase in usage.\
            Current utilization + potential_increase must be less than the quota.
        """
        return await sync_to_async(self.ensure_quota_or_raise)(account_id, feature_name, potential_increase)

    @abc.abstractmethod
    def register_usage(self, account_id: uuid.UUID, feature_name: str, increment: int = 1) -> None:
        """
        Register usage for the given account and feature.

        :param account_id: The account ID.
        :param feature_name: The feature name.
        :param increment: The value to be added to quota usage.
        """
        pass

    @abc.abstractmethod
    async def aregister_usage(self, account_id: uuid.UUID, feature_name: str | set[str], increment: int = 1) -> None:
        """
        Register usage for the given account and feature.

        :param account_id: The account ID.
        :param feature_name: The feature name.
        :param increment: The value to be added to quota usage.
        """
        pass

    @abc.abstractmethod
    def get_quotas_utilization(self, account_id: uuid.UUID, feature_name: str | set[str] | None) -> QuotaStats:
        """
        Get the quota utilization for the given account and features.

        :param account_id: The account ID.
        :param feature_name: Name of the feature or a list of feature names. None means all features having quotas.
        """
        pass

    @abc.abstractmethod
    async def aget_quotas_utilization(self, account_id: uuid.UUID, feature_name: str | set[str] | None) -> QuotaStats:
        """
        Get the quota utilization for the given account and features.

        :param account_id: The account ID.
        :param feature_name: Name of the feature or a list of feature names. None means all features having quotas.
        """
        pass

    @abc.abstractmethod
    def set_quota(
        self, account_id: uuid.UUID, feature_name: str, limits: ValuePerBucket, owner_tag: str | None = None
    ) -> Quota:
        """
        Set the quota for the given account and feature.

        :param account_id: The account ID.
        :param feature_name: The feature name.
        :param limits: Limits for each bucket.
        :param owner_tag: Optional owner tag.
        :return: The created or updated quota.
        """
        pass

    @abc.abstractmethod
    async def aset_quota(
        self, account_id: uuid.UUID, feature_name: str, limits: ValuePerBucket, owner_tag: str | None = None
    ) -> Quota:
        """
        Set the quota for the given account and feature.

        :param account_id: The account ID.
        :param feature_name: The feature name.
        :param limits: Limits for each bucket.
        :param owner_tag: Optional owner tag.
        :return: The created or updated quota.
        """
        pass
