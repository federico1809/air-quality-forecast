from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict


class SystemState(str, Enum):
    """
    Global operational state of the air quality system.
    """

    DATA_INVALID = "DATA_INVALID"
    DATA_INSUFFICIENT = "DATA_INSUFFICIENT"
    DEGRADED_DATA = "DEGRADED_DATA"
    OPERATIONAL = "OPERATIONAL"


class CheckSeverity(str, Enum):
    """
    Defines how a check impacts system operation.
    """

    STRUCTURAL = "STRUCTURAL"
    ANALYTICAL = "ANALYTICAL"
    OPERATIONAL = "OPERATIONAL"


class CheckStatus(str, Enum):
    """
    Result of an individual contract check.
    """

    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


@dataclass(frozen=True)
class CheckResult:
    """
    Immutable result produced by a single operational check.
    """

    name: str
    severity: CheckSeverity
    status: CheckStatus
    message: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    evaluated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )