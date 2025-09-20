#
#  Copyright 2025 by Dmitry Berezovsky, MIT License
#
import abc
import dataclasses
import datetime
from enum import StrEnum
import uuid


class QuotaBucket(StrEnum):
    HOURLY = "hourly"
    DAILY = "daily"
    MONTHLY = "monthly"
    TOTAL = "total"


@dataclasses.dataclass(kw_only=True)
class ValuePerBucket:
    hourly: int | None = None
    daily: int | None = None
    monthly: int | None = None
    total: int | None = None


@dataclasses.dataclass(kw_only=True)
class QuotaStatus:
    quota_id: uuid.UUID
    limits: ValuePerBucket
    usage: ValuePerBucket

    def is_exceeded(self) -> bool:
        """Check if any quota limit is exceeded."""
        if self.limits.daily is not None and self.usage.daily is not None and self.usage.daily >= self.limits.daily:
            return True
        if (
            self.limits.monthly is not None
            and self.usage.monthly is not None
            and self.usage.monthly >= self.limits.monthly
        ):
            return True
        if self.limits.total is not None and self.usage.total is not None and self.usage.total >= self.limits.total:
            return True
        return False


@dataclasses.dataclass(kw_only=True)
class QuotaStats:
    account_id: uuid.UUID
    feature_stats: dict[str, QuotaStatus]

    def has_exceeded_quotas(self) -> bool:
        """Check if any feature has exceeded quotas."""
        return any(status.is_exceeded() for status in self.feature_stats.values())


@dataclasses.dataclass(kw_only=True)
class QuotaUseForBucket:
    bucket_name: QuotaBucket
    current_usage: int
    limit: int | None
    quota_id: uuid.UUID

    @property
    def overuse(self) -> int | None:
        if self.limit is None:
            return None
        return self.current_usage - self.limit


class Quota(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def id(self) -> uuid.UUID:
        pass

    @property
    @abc.abstractmethod
    def account_id(self) -> uuid.UUID:
        pass

    @property
    @abc.abstractmethod
    def feature_name(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def get_limits(self) -> ValuePerBucket:
        pass


class QuotaUsage(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def account_id(self) -> uuid.UUID:
        pass

    @property
    @abc.abstractmethod
    def feature_name(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def point_in_time(self) -> datetime.datetime:
        pass

    @property
    @abc.abstractmethod
    def usage_count(self) -> int:
        pass
