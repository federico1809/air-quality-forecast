# Air Quality Forecasting & Early Warning System

End-to-end Machine Learning system for **PM2.5 forecasting** and **operational air quality alerting**, designed with production-oriented architecture and decision-driven modeling.

---

## 🎯 Project Objective

Build a system that:

- Forecasts **PM2.5 levels 24 hours ahead**
- Produces **probabilistic predictions**
- Converts predictions into **operational alerts**
- Simulates a **decision-support tool for public health authorities**
- Prioritizes **decision usefulness over raw model accuracy**

---

## 🧠 Modeling Philosophy

- Classical ML First  
- Strong feature engineering  
- Interpretable models  
- Decision-driven evaluation  
- Validation before prediction  

---

## 🏗️ System Architecture

Data → Validation → Features → Modeling → Decision Layer  

---

## 📦 Dataset

- Source: UCI Beijing Air Quality Dataset  
- Station: **Aotizhongxin**  
- ~35k hourly records  

---

## 🛡️ Data Contract

Operational checks ensure data reliability before prediction:

- Recent PM2.5 coverage (last 24h)  
- Missing streak continuity (last 7 days)  

System states:

- OPERATIONAL  
- DEGRADED_DATA  
- DATA_INSUFFICIENT  
- DATA_INVALID  

---

## ⚠️ Engineering Insight

A critical bug was identified:

The validation registry remained empty due to missing module import.

Fix:

    import air_quality.data_contract.checks.operational

Lesson:

- Dynamic systems can fail silently  
- Plugin architectures require explicit imports  
- System state can be misleading without executed checks  

---

## ⚙️ Feature Engineering

- Lags: 1–72 hours  
- Rolling statistics (shifted to prevent leakage)  
- Temporal features  

Target:

**PM2.5 (t + 24h)**

---

## 🔀 Train/Test Strategy

Temporal split:

- Train: 2013–2016  
- Test: 2016–2017  

---

## 🤖 Modeling

Baseline:

- Logistic Regression  
- StandardScaler  

Binary formulation:

**PM2.5 ≥ 35 µg/m³ → unhealthy**

---

## 📈 Calibration

Methods evaluated:

- Platt scaling (sigmoid)  
- Isotonic regression  

Selected:

**Platt scaling** (better stability + similar performance)

---

## 🧠 Decision Layer

Instead of binary classification, the system outputs **risk levels**:

| Probability | Risk Level |
|------------|-----------|
| ≥ 0.7 | high |
| 0.5 – 0.7 | medium |
| 0.3 – 0.5 | low |
| < 0.3 | safe |

---

## 🎯 Threshold Selection

Operational threshold: **0.5**

Selected using:

- Precision / recall trade-off  
- False negative cost analysis (FN >> FP)  
- Threshold jump analysis  

Key insight:

**0.5 is the first meaningful operational inflection point** where false negatives begin to increase significantly.

---

## 📊 System Behavior

Observed risk distribution:

- medium: ~86%  
- high: ~8%  
- low: ~6%  
- safe: ~0.2%  

Interpretation:

- System is conservative  
- Strong bias toward minimizing false negatives  
- Reflects real-world pollution patterns  

---

## 🚀 Outputs

Generated artifacts:

- data/metrics/calibration_results.csv  
- data/metrics/threshold_analysis_calibrated.csv  
- data/metrics/predictions_with_risk_levels.csv  

---

## 💡 Key Design Principles

- Reproducibility first  
- Explicit over implicit  
- Separation of concerns  
- Decision-driven ML  
- Production-oriented design  

---

## 🔮 Future Work

- Cost-sensitive optimization  
- Multi-level alert policies  
- Visualization layer (Tableau / Power BI)  
- Multi-station scaling  
- Drift detection  

---

## 👤 Author

Federico Ceballos Torres  
Data Scientist  