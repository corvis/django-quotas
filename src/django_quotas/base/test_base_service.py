#
#  Copyright 2025 by Dmitry Berezovsky, MIT License
#
"""
Unit tests for QuotaService (django_quotas.base.service).
"""

from typing import Any, cast
import unittest
from unittest.mock import MagicMock
import uuid

from django_quotas.base.dto import Quota, QuotaBucket, QuotaStats, ValuePerBucket
from django_quotas.base.service import QuotaExceededError, QuotaService

__all__ = ["TestQuotaService"]

ACCOUNT_ID = "11111111-1111-1111-1111-111111111111"
FEATURE_A = "feature_a"
FEATURE_B = "feature_b"


class MockQuotaService(QuotaService):
    """Concrete implementation for testing QuotaService logic."""

    def __init__(self, utilization: QuotaStats) -> None:
        self._utilization = utilization
        self.registered: list[tuple[str, str, int]] = []

    def register_usage(self, account_id: str, feature: str, increment: int = 1) -> None:
        self.registered.append((account_id, feature, increment))

    async def aregister_usage(self, account_id: str, feature: str | set[str], increment: int = 1) -> None:
        self.registered.append((account_id, cast(str, feature), increment))

    def get_quotas_utilization(self, account_id: uuid.UUID, feature: str | set[str] | None) -> QuotaStats:
        return self._utilization

    async def aget_quotas_utilization(self, account_id: uuid.UUID, feature: str | set[str] | None) -> QuotaStats:
        return self._utilization

    def set_quota(
        self, account_id: uuid.UUID, feature: str, limits: ValuePerBucket, owner_tag: str | None = None
    ) -> Quota:
        raise NotImplementedError()

    async def aset_quota(
        self, account_id: uuid.UUID, feature: str, limits: ValuePerBucket, owner_tag: str | None = None
    ) -> Quota:
        raise NotImplementedError()


class TestQuotaService(unittest.TestCase):
    """Unit tests for QuotaService logic."""

    def setUp(self) -> None:
        self.quota_id = uuid.uuid4()
        self.usage = ValuePerBucket(hourly=1, daily=2, monthly=3, total=4)
        self.limits = ValuePerBucket(hourly=10, daily=20, monthly=30, total=40)
        self.status = MagicMock()
        self.status.usage = self.usage
        self.status.limits = self.limits
        self.status.quota_id = self.quota_id

    def make_stats(self, feature_stats: dict[str, Any]) -> QuotaStats:
        stats = MagicMock()
        stats.feature_stats = feature_stats
        return stats

    def test_quota_not_exceeded(self) -> None:
        """Should not raise if usage + potential_increase <= limit for all buckets."""
        stats = self.make_stats({FEATURE_A: self.status})
        service = MockQuotaService(stats)
        try:
            service.ensure_quota_or_raise(ACCOUNT_ID, FEATURE_A, potential_increase=1)
        except QuotaExceededError:
            self.fail("QuotaExceededError should not be raised when under quota.")

    def test_quota_exceeded_single_bucket(self) -> None:
        """Should raise if usage + potential_increase > limit for any bucket."""
        # Set hourly usage to 10, limit to 10, so any increase exceeds
        self.status.usage = ValuePerBucket(hourly=10, daily=2, monthly=3, total=4)
        stats = self.make_stats({FEATURE_A: self.status})
        service = MockQuotaService(stats)
        with self.assertRaises(QuotaExceededError) as cm:
            service.ensure_quota_or_raise(ACCOUNT_ID, FEATURE_A, potential_increase=1)
        err = cm.exception
        self.assertIn(FEATURE_A, err.get_exceeded_features())
        buckets = err.get_stats_per_feature()[FEATURE_A]
        self.assertTrue(any(b.bucket_name == QuotaBucket.HOURLY for b in buckets))

    def test_quota_exceeded_multiple_features(self) -> None:
        """Should raise and report all features that are exceeded."""
        status_a = MagicMock()
        status_a.usage = ValuePerBucket(hourly=10, daily=2, monthly=3, total=4)
        status_a.limits = ValuePerBucket(hourly=10, daily=20, monthly=30, total=40)
        status_a.quota_id = uuid.uuid4()
        status_b = MagicMock()
        status_b.usage = ValuePerBucket(hourly=1, daily=21, monthly=3, total=4)
        status_b.limits = ValuePerBucket(hourly=10, daily=20, monthly=30, total=40)
        status_b.quota_id = uuid.uuid4()
        stats = self.make_stats({FEATURE_A: status_a, FEATURE_B: status_b})
        service = MockQuotaService(stats)
        with self.assertRaises(QuotaExceededError) as cm:
            service.ensure_quota_or_raise(ACCOUNT_ID, {FEATURE_A, FEATURE_B}, potential_increase=1)
        err = cm.exception
        self.assertEqual(err.get_exceeded_features(), {FEATURE_A, FEATURE_B})
        self.assertTrue(any(b.bucket_name == QuotaBucket.HOURLY for b in err.get_stats_per_feature()[FEATURE_A]))
        self.assertTrue(any(b.bucket_name == QuotaBucket.DAILY for b in err.get_stats_per_feature()[FEATURE_B]))

    def test_no_quota_for_feature(self) -> None:
        """Should not raise if feature is not present in stats (no quota for feature)."""
        stats = self.make_stats({})
        service = MockQuotaService(stats)
        try:
            service.ensure_quota_or_raise(ACCOUNT_ID, FEATURE_A, potential_increase=1)
        except QuotaExceededError:
            self.fail("QuotaExceededError should not be raised if feature is not present.")

    def test_none_limit_is_ignored(self) -> None:
        """Should not raise if limit is None (unlimited)."""
        self.status.limits = ValuePerBucket(hourly=None, daily=None, monthly=None, total=None)
        stats = self.make_stats({FEATURE_A: self.status})
        service = MockQuotaService(stats)
        try:
            service.ensure_quota_or_raise(ACCOUNT_ID, FEATURE_A, potential_increase=1000)
        except QuotaExceededError:
            self.fail("QuotaExceededError should not be raised for unlimited quotas.")

    def test_async_quota_not_exceeded(self) -> None:
        """Async version should not raise if under quota."""
        stats = self.make_stats({FEATURE_A: self.status})
        service = MockQuotaService(stats)
        import asyncio

        async def run() -> None:
            await service.aensure_quota_or_raise(ACCOUNT_ID, FEATURE_A, potential_increase=1)

        try:
            asyncio.run(run())
        except QuotaExceededError:
            self.fail("QuotaExceededError should not be raised in async when under quota.")

    def test_async_quota_exceeded(self) -> None:
        """Async version should raise if exceeded."""
        self.status.usage = ValuePerBucket(hourly=10, daily=2, monthly=3, total=4)
        stats = self.make_stats({FEATURE_A: self.status})
        service = MockQuotaService(stats)
        import asyncio

        async def run() -> None:
            await service.aensure_quota_or_raise(ACCOUNT_ID, FEATURE_A, potential_increase=1)

        with self.assertRaises(QuotaExceededError):
            asyncio.run(run())
