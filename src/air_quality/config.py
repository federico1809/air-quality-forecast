from pathlib import Path

# Project root (repo root)
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Reports
REPORTS_DIR = PROJECT_ROOT / "reports"

# Notebooks
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"