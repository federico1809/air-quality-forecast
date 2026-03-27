# Air Quality Forecasting & Early Warning System

End-to-end Machine Learning system for **PM2.5 forecasting** and **operational air quality alerting**, designed with production-oriented architecture and decision-driven modeling.

---

## 🎯 Project Objective

Build a system that:

* Forecasts **PM2.5 levels 24 hours ahead**
* Produces **probabilistic predictions**
* Converts predictions into **operational alerts**
* Simulates a **decision-support tool for public health authorities**
* Prioritizes **decision usefulness over raw model accuracy**

---

## 🧠 Modeling Philosophy

This project follows a **Classical ML First approach**:

* Strong feature engineering
* Interpretable baselines
* Rigorous validation
* Decision-oriented evaluation

Deep learning models may be introduced later **only if justified**.

---

## 🏗️ System Architecture

The system is intentionally designed as a **hybrid ML system**:

Prediction Layer + Decision Layer

Pipeline:

Raw Data (ZIP)
→ Data Ingestion
→ Data Normalization (Parquet)
→ Data Contract (Validation Layer)
→ Feature Engineering
→ Modeling
→ Decision System (Alerts)

---

## 📦 Repository Structure

src/
air_quality/
config.py
data/
ingest.py
make_dataset.py
data_contract/
models.py
aggregation.py
evaluate.py
checks/
base.py
operational.py

data/
raw/
interim/
processed/

notebooks/
reports/
tests/

---

## 📊 Dataset

Source: UCI Beijing Multi-Site Air Quality Dataset

MVP Scope:

* Single station: **Aotizhongxin**
* Temporal modeling prioritized over spatial scaling

### Station Selection Rationale

This project uses a single monitoring station ("Aotizhongxin") for the MVP phase.

While real-world air quality systems are multi-station and spatially complex, this decision is intentional:

* Focus on **temporal dynamics and forecasting quality**
* Reduce complexity for **data validation and system design**
* Enable **clear interpretability**
* Prioritize **architecture before scaling**

The system is designed to be **easily extensible to multiple stations**.

---

## 🔐 Data Integrity

Dataset is validated using SHA256 checksum:

d1b9261c54132f04c374f762f1e5e512af19f95c95fd6bfa1e8ac7e927e3b0b8

Ensures:

* Reproducibility
* Data consistency across environments

---

## ⚙️ Environment Setup

Create and activate virtual environment:

Windows (PowerShell):
.venv\Scripts\activate

Install project:

pip install -e .

Dependencies managed via pyproject.toml:

* pandas
* numpy
* pyarrow

---

## 🚀 Pipeline Execution

### 1. Data Ingestion

python -m air_quality.data.ingest

Downloads and validates raw dataset.

---

### 2. Data Normalization (raw → interim)

python -m air_quality.data.make_dataset

Output:

data/interim/station_hourly.parquet

* 35,064 rows
* hourly frequency
* cleaned datetime
* deduplicated

---

### 3. Data Contract Execution

python -m air_quality.data_contract.evaluate

Output:

data/interim/operational_status.json

---

## Data Contract System

A **plugin-based validation system** that determines whether the dataset is suitable for forecasting.

### Key Concepts

* CheckResult
* CheckSeverity (STRUCTURAL / OPERATIONAL)
* CheckStatus (PASS / WARN / FAIL)
* SystemState:

  * OPERATIONAL
  * DEGRADED_DATA
  * DATA_INSUFFICIENT
  * DATA_INVALID

---

### Current Check

RecentPM25CoverageCheck:

* Evaluates PM2.5 coverage over last 24 hours
* Coverage = non-null values / 24

Thresholds:

* ≥ 0.75 → PASS
* 0.5–0.75 → WARN
* < 0.5 → FAIL

---

### Example Output

{
"system_state": "OPERATIONAL",
"checks": [
{
"name": "recent_pm25_coverage",
"status": "PASS",
"coverage_last_24h": 1.0
}
]
}

---

## ⚠️ Engineering Challenge Encountered

During development, the system initially returned:

{
"system_state": "OPERATIONAL",
"checks": []
}

### Root Cause

The validation system uses a **plugin registry pattern**.

Checks were not being executed because:

* Python modules are only registered when imported
* The check module was never imported in evaluate.py
* Registry remained empty

### Fix

Explicit import added:

import air_quality.data_contract.checks.operational

### Lesson

This highlights a common issue in Python systems:

* Dynamic registration depends on module loading
* Silent failures can occur without proper imports

This scenario will be expanded into a **technical LinkedIn post** explaining:

* the bug
* its root cause
* debugging process
* production implications

---

## 📍 Current Project Status

Completed:

* Data ingestion
* Data normalization
* Data contract system
* End-to-end execution

Next:

* EDA (decision-oriented)
* Feature engineering
* Modeling
* Decision layer (alerts)

---

## Reproducibility

The project is fully reproducible:

* Defined dependencies
* Deterministic dataset validation
* Modular pipeline
* CLI-based execution

---

## 💡 Key Design Principles

* Reproducibility first
* Separation of concerns
* Decision-driven ML
* Production-oriented thinking
* Explicit over implicit behavior

---

## 🚀 Future Work

* Probabilistic forecasting models
* Feature engineering pipeline
* Alert threshold system (WHO-based)
* Multi-station scaling
* Drift detection and retraining

---

## 👤 Author

Federico

Data Scientist
Background in QA Engineering & Scrum Master
Focus: production-grade ML systems