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

class MaxMissingStreakCheck(OperationalCheck):
    """
    Ensures temporal continuity by limiting missing data streaks
    in the recent time window.
    """

    name = "max_missing_streak"
    severity = CheckSeverity.OPERATIONAL
    description = "Checks maximum missing PM2.5 streak in last 7 days"

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

        # Window: last 7 days
        window_start = latest_time - pd.Timedelta(days=7)
        df_window = df[df["datetime"] > window_start]

        if df_window.empty:
            return CheckResult(
                name=self.name,
                severity=self.severity,
                status=CheckStatus.FAIL,
                message="No data in evaluation window",
                metrics={},
            )

        # Compute missing streaks
        is_missing = df_window["PM2.5"].isna().astype(int)

        streak_id = (is_missing.diff() != 0).cumsum()

        streaks = (
            df_window.assign(is_missing=is_missing, streak_id=streak_id)
            .groupby("streak_id")
            .agg(
                is_missing=("is_missing", "first"),
                length=("is_missing", "size"),
            )
        )

        missing_streaks = streaks[streaks["is_missing"] == 1]

        if missing_streaks.empty:
            max_streak = 0
        else:
            max_streak = int(missing_streaks["length"].max())

        threshold = 12  # hours

        if max_streak <= threshold:
            status = CheckStatus.PASS
        else:
            status = CheckStatus.FAIL

        return CheckResult(
            name=self.name,
            severity=self.severity,
            status=status,
            message=f"Max missing streak last 7d: {max_streak}h (threshold={threshold}h)",
            metrics={
                "max_missing_streak_hours": max_streak,
                "threshold_hours": threshold,
            },
        )