from __future__ import annotations

import pandas as pd

from air_quality.data_contract.models import (
    CheckResult,
    CheckSeverity,
    CheckStatus,
)
from air_quality.data_contract.checks.base import OperationalCheck


class RecentPM25CoverageCheck(OperationalCheck):
    """
    Ensures sufficient recent PM2.5 data coverage for reliable forecasting.
    """

    name = "recent_pm25_coverage"
    severity = CheckSeverity.OPERATIONAL
    description = "Checks PM2.5 availability in the last 24 hours"

    def evaluate(self, df: pd.DataFrame) -> CheckResult:
        if "datetime" not in df.columns or "PM2.5" not in df.columns:
            return CheckResult(
                name=self.name,
                severity=self.severity,
                status=CheckStatus.FAIL,
                message="Required columns missing: datetime or PM2.5",
                metrics={},
            )

        df = df.copy()

        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
        df = df.sort_values("datetime")

        latest_time = df["datetime"].max()

        if pd.isna(latest_time):
            return CheckResult(
                name=self.name,
                severity=self.severity,
                status=CheckStatus.FAIL,
                message="Invalid datetime column",
                metrics={},
            )

        window_start = latest_time - pd.Timedelta(hours=24)

        recent_df = df[df["datetime"] > window_start]

        total_expected = 24
        observed = recent_df["PM2.5"].notna().sum()

        coverage = observed / total_expected if total_expected > 0 else 0.0

        if coverage >= 0.75:
            status = CheckStatus.PASS
        elif coverage >= 0.5:
            status = CheckStatus.WARN
        else:
            status = CheckStatus.FAIL

        return CheckResult(
            name=self.name,
            severity=self.severity,
            status=status,
            message=f"PM2.5 coverage last 24h: {coverage:.2%}",
            metrics={
                "coverage_last_24h": coverage,
                "observations": int(observed),
                "expected": total_expected,
            },
        )