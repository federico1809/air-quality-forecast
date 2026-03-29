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
features/
build_features.py
modeling/
train_baseline.py

data/
raw/
interim/
processed/
metrics/

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
* scikit-learn

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

## 🤖 Modeling Approach

The problem is formulated as a **binary classification task**:

* Positive class: **PM2.5 ≥ 35 µg/m³ (unhealthy)**
* Negative class: **PM2.5 < 35 µg/m³**

Model:

* Logistic Regression (baseline)
* StandardScaler for feature normalization

This formulation aligns the model with **operational decision-making**, not just prediction accuracy.

---

## 📊 Model Performance (Baseline)

At default threshold (0.5):

* Accuracy: 0.6598
* Precision: 0.6682
* Recall: 0.9174
* F1 Score: 0.7733
* ROC AUC: 0.6496
* PR AUC: 0.7409

The model significantly outperforms a naive baseline based on lagged PM2.5.

---

## 🚨 Decision Layer (Operational Threshold)

The system uses predicted probabilities to trigger alerts.

### Threshold Selection

Evaluated thresholds:

0.3, 0.4, 0.5, 0.6, 0.7

Final decision:

**Decision threshold = 0.4**

### Rationale

At threshold 0.4:

* Recall: 0.983 → captures ~98% of unhealthy events
* False Negatives: 57 (vs 281 at threshold 0.5)
* Significant reduction in missed hazardous events
* Alert rate: ~95% (high but acceptable for a conservative system)

### Operational Trade-off

The system is intentionally **risk-averse**:

* Prioritizes **minimizing false negatives**
* Accepts a **high number of alerts**
* Designed for **early warning in public health contexts**

### Design Principle

> It is preferable to over-alert than to miss hazardous air quality events.

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
* Binary classification baseline (Logistic Regression)
* Probabilistic calibration (Platt scaling)
* Threshold analysis and decision boundary evaluation

---

## 🧠 Decision Layer (Operational Threshold)

The model outputs calibrated probabilities of unhealthy air quality (PM2.5 ≥ 35 µg/m³).

A decision threshold was selected using a combination of:

* Threshold-based performance metrics (precision, recall, FN, FP)
* Operational trade-off analysis (alert rate vs missed events)
* Structural "jump analysis" of system behavior across thresholds

### Final Decision

Threshold = **0.5**

### Rationale

Threshold 0.5 was selected as the first **operationally meaningful inflection point** in system behavior.

From the jump analysis:

* Transition from 0.4 → 0.5:
  * False negatives increase moderately (+130)
  * Alert rate drops significantly (~5%)
  * First clear shift away from "always alerting"

* Transition from 0.5 → 0.6:
  * False negatives increase drastically (+1113)
  * System begins missing a large number of dangerous events

This indicates that:

* Thresholds below 0.5 result in near-constant alerting (alert_rate ~ 0.99)
* Thresholds above 0.5 degrade system safety significantly

Therefore, 0.5 represents the best trade-off between:

* Maintaining high recall (~0.95)
* Reducing alert saturation
* Preserving operational usability

---

## 📍 Current System Behavior

* High recall (~0.95)
* Moderate precision (~0.64)
* High but controlled alert rate (~0.93)
* Strong bias toward minimizing false negatives

---

Next:

* Cost-sensitive optimization refinement
* Multi-level alert system (future iteration)
* Visualization layer (Tableau / Power BI)

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

* Probability calibration (Platt / isotonic)
* Multi-level alert system (WHO thresholds)
* Multi-station scaling
* Drift detection and retraining
* Inference pipeline

---

## 👤 Author

Federico Ceballos Torres

Data Scientist