from __future__ import annotations

from typing import List

from air_quality.data_contract.models import (
    CheckResult,
    CheckSeverity,
    CheckStatus,
    SystemState,
)


def resolve_system_state(results: List[CheckResult]) -> SystemState:
    """
    Aggregate individual check results into a global system state.
    """

    has_structural_fail = any(
        r.severity == CheckSeverity.STRUCTURAL and r.status == CheckStatus.FAIL
        for r in results
    )

    if has_structural_fail:
        return SystemState.DATA_INVALID

    has_operational_fail = any(
        r.severity == CheckSeverity.OPERATIONAL and r.status == CheckStatus.FAIL
        for r in results
    )

    if has_operational_fail:
        return SystemState.DATA_INSUFFICIENT

    has_warnings = any(r.status == CheckStatus.WARN for r in results)

    if has_warnings:
        return SystemState.DEGRADED_DATA

    return SystemState.OPERATIONAL