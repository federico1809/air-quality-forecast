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

The system is designed as a **production-oriented ML system**:

Data Layer → Validation Layer → Feature Layer → Modeling Layer → Decision Layer

Pipeline:

Raw Data (ZIP)
→ Data Ingestion
→ Data Normalization (Parquet)
→ Data Contract (Validation Layer)
→ Feature Engineering
→ Modeling
→ Decision System (Alerts - future)

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
    features/
      build_features.py
    modeling/
      train_baseline.py

data/
  raw/
  interim/
  processed/

notebooks/
  01_EDA.ipynb

---

## 📊 Dataset

Source: UCI Beijing Multi-Site Air Quality Dataset

MVP Scope:

* Single station: **Aotizhongxin**
* Temporal modeling prioritized over spatial scaling

### Station Selection Rationale

This project uses a single monitoring station ("Aotizhongxin") for the MVP phase.

This is intentional:

* Focus on **temporal dynamics and forecasting quality**
* Reduce complexity for **data validation and system design**
* Enable **clear interpretability**
* Prioritize **architecture before scaling**

The system is designed to be **extensible to multiple stations**.

---

## 🔐 Data Integrity

Dataset is validated using SHA256 checksum:

d1b9261c54132f04c374f762f1e5e512af19f95c95fd6bfa1e8ac7e927e3b0b8

Ensures:

* Reproducibility
* Data consistency across environments

---

## ⚙️ Environment Setup

Activate virtual environment (PowerShell):

.venv\Scripts\activate

Install project:

pip install -e .

Dependencies managed via pyproject.toml:

* pandas
* numpy
* pyarrow
* matplotlib (EDA only)

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

* ~35k rows
* hourly frequency
* clean datetime
* deduplicated

---

### 3. Data Contract Execution

python -m air_quality.data_contract.evaluate

Output:

data/interim/operational_status.json

---

## 🛡️ Data Contract System

A **plugin-based validation system** that determines whether the dataset is suitable for forecasting.

### Key Concepts

* CheckResult
* CheckSeverity (STRUCTURAL / ANALYTICAL / OPERATIONAL)
* CheckStatus (PASS / WARN / FAIL)
* SystemState:
  * OPERATIONAL
  * DEGRADED_DATA
  * DATA_INSUFFICIENT
  * DATA_INVALID

---

### Operational Checks

#### 1. RecentPM25CoverageCheck

* Evaluates PM2.5 coverage over last 24 hours
* Coverage = non-null values / 24

Thresholds:

* ≥ 0.75 → PASS
* 0.5–0.75 → WARN
* < 0.5 → FAIL

#### 2. MaxMissingStreakCheck

* Evaluates continuity of PM2.5 signal over last 7 days
* Measures longest consecutive missing streak

Threshold:

* ≤ 12 hours → PASS
* > 12 hours → FAIL

---

### Design Principle

"No prediction without data validation"

The system **does not assume data is valid**.  
It evaluates whether forecasting is reliable before allowing predictions.

---

## ⚠️ Engineering Challenge Encountered

Initial system output:

{
  "system_state": "OPERATIONAL",
  "checks": []
}

### Root Cause

The validation system uses a **plugin registry pattern**.

Checks were not executed because:

* Python modules are only registered when imported
* The check module was never imported in evaluate.py
* Registry remained empty

### Fix

Explicit import added:

import air_quality.data_contract.checks.operational

### Lesson

* Dynamic systems can fail silently
* Plugin architectures require explicit module loading
* System state can be incorrect without visible errors

---

## 📊 EDA (Decision-Oriented)

The EDA focuses on **system reliability**, not just exploration.

Key findings:

* High overall coverage (~97%)
* Missing data is **not uniformly distributed**
* Historical long gaps exist (up to ~14 days)
* Recent data is stable and reliable

Key decision:

* Validation focuses on **recent window (last 7 days)** instead of full history

---

## ⚙️ Feature Engineering

Implemented in:

src/air_quality/features/build_features.py

### Target

PM2.5(t + 24h)

### Features

#### Lags

1, 2, 3, 6, 12, 24, 48, 72

#### Rolling statistics

* rolling_mean: 6h, 12h, 24h
* rolling_std: 6h, 12h, 24h

#### Time features

* hour
* day_of_week
* is_weekend

### Critical design decision

Rolling features use shift(1) to prevent data leakage.

---

## 📦 Feature Dataset

data/processed/features.parquet

* ~26.9k rows
* 36 columns
* Fully modeling-ready

---

## 🔀 Train/Test Split

Temporal split (no randomization):

* Train: ~80%
* Test: ~20%

Example:

* Train: 2013 → 2016
* Test: 2016 → 2017

This simulates real production usage.

---

## 📍 Current Project Status

Completed:

* Data ingestion
* Data normalization
* Data contract system
* EDA (decision-oriented)
* Feature engineering pipeline
* Modeling dataset generation
* Temporal train/test split

Next:

* Baseline modeling (Linear Regression)
* Model evaluation (RMSE, MAE)
* Decision layer (alerts)
* Probabilistic forecasting

---

## 💡 Key Design Principles

* Reproducibility first
* Separation of concerns
* Decision-driven ML
* Production-oriented design
* Explicit behavior over implicit assumptions
* Validation before prediction

---

## 🚀 Future Work

* Probabilistic forecasting
* Alert system (WHO thresholds)
* Multi-station scaling
* Drift detection and retraining
* Inference pipeline

---

## 👤 Author

Federico Ceballos Torres

Data Scientist  