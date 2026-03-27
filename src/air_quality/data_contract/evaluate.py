from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from air_quality.data_contract.aggregation import resolve_system_state
from air_quality.data_contract.checks.base import OperationalCheck

# Force import of all check modules to populate registry
import air_quality.data_contract.checks.operational  # noqa

def load_dataset(path: Path) -> pd.DataFrame:
    """
    Load dataset for contract evaluation.
    """
    return pd.read_parquet(path)


def run_checks(df: pd.DataFrame):
    """
    Execute all registered checks.
    """
    results = []

    for check_cls in OperationalCheck.registry:
        check = check_cls()
        result = check.evaluate(df)
        results.append(result)

    return results


def build_report(results):
    """
    Build structured report for serialization.
    """
    system_state = resolve_system_state(results)

    return {
        "system_state": system_state.value,
        "checks": [
            {
                "name": r.name,
                "severity": r.severity.value,
                "status": r.status.value,
                "message": r.message,
                "metrics": r.metrics,
                "evaluated_at": r.evaluated_at.isoformat(),
            }
            for r in results
        ],
    }


def save_report(report: dict, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)


def main():
    dataset_path = Path("data/interim/station_hourly.parquet")
    output_path = Path("data/interim/operational_status.json")

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {dataset_path}. "
            "You must generate the interim dataset before running the contract."
        )

    df = load_dataset(dataset_path)

    results = run_checks(df)
    report = build_report(results)

    save_report(report, output_path)

    print(f"Operational status saved to: {output_path}")


if __name__ == "__main__":
    main()