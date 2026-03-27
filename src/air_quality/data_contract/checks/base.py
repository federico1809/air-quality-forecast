from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar, List, Type

import pandas as pd

from air_quality.data_contract.models import CheckResult, CheckSeverity


class OperationalCheck(ABC):
    """
    Base class for all data contract checks.

    Implements automatic registration for plugin-style discovery.
    """

    registry: ClassVar[List[Type["OperationalCheck"]]] = []

    name: ClassVar[str]
    severity: ClassVar[CheckSeverity]
    description: ClassVar[str]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if not hasattr(cls, "name"):
            raise TypeError(f"{cls.__name__} must define a 'name' attribute")

        OperationalCheck.registry.append(cls)

    @abstractmethod
    def evaluate(self, df: pd.DataFrame) -> CheckResult:
        """
        Evaluate the check against the provided dataset.

        Must return a CheckResult.
        """
        pass