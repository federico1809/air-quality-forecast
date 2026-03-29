import os
import pandas as pd
import numpy as np

from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)
from sklearn.preprocessing import StandardScaler


TARGET_THRESHOLD = 35.0


# -------------------------
# Risk level assignment (Decision Layer)
# -------------------------
def assign_risk_level(proba):
    if proba >= 0.7:
        return "high"
    elif proba >= 0.5:
        return "medium"
    elif proba >= 0.3:
        return "low"
    else:
        return "safe"


# -------------------------
# Threshold evaluation
# -------------------------
def evaluate_thresholds(y_true, y_proba, thresholds):
    results = []

    for t in thresholds:
        y_pred = (y_proba >= t).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

        results.append({
            "threshold": t,
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred, zero_division=0),
            "recall": recall_score(y_true, y_pred, zero_division=0),
            "f1": f1_score(y_true, y_pred, zero_division=0),
            "false_negatives": fn,
            "false_positives": fp,
            "true_positives": tp,
            "true_negatives": tn,
            "alert_rate": y_pred.mean(),
        })

    return pd.DataFrame(results)


# -------------------------
# Jump analysis
# -------------------------
def analyze_threshold_jumps(df):
    df = df.sort_values("threshold").copy()

    df["delta_fn"] = df["false_negatives"].diff()
    df["delta_fp"] = df["false_positives"].diff()
    df["delta_alert_rate"] = df["alert_rate"].diff()

    df["jump_score"] = (
        df["delta_fn"].abs() * 20 +
        df["delta_alert_rate"].abs() * 1000
    )

    return df


def main():
    # -------------------------
    # Load data
    # -------------------------
    df = pd.read_parquet("data/processed/features.parquet")
    df["datetime"] = pd.to_datetime(df["datetime"])

    # -------------------------
    # Target
    # -------------------------
    y = (df["target"] >= TARGET_THRESHOLD).astype(int)

    # -------------------------
    # Features
    # -------------------------
    EXCLUDED_COLUMNS = [
        "No", "year", "month", "day",
        "datetime", "station", "target", "wd",
    ]

    X = df.drop(columns=EXCLUDED_COLUMNS)

    # -------------------------
    # Temporal split
    # -------------------------
    cutoff = pd.Timestamp("2016-05-22 14:00:00")

    train_mask = df["datetime"] <= cutoff
    test_mask = df["datetime"] > cutoff

    X_train_full = X.loc[train_mask]
    y_train_full = y.loc[train_mask]

    X_test = X.loc[test_mask]
    y_test = y.loc[test_mask]

    # -------------------------
    # Train / Calibration split
    # -------------------------
    split_index = int(len(X_train_full) * 0.8)

    X_train = X_train_full.iloc[:split_index]
    y_train = y_train_full.iloc[:split_index]

    X_calib = X_train_full.iloc[split_index:]
    y_calib = y_train_full.iloc[split_index:]

    # -------------------------
    # Scaling
    # -------------------------
    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(X_train)
    X_calib_scaled = scaler.transform(X_calib)
    X_test_scaled = scaler.transform(X_test)

    print("Train size:", X_train.shape)
    print("Calibration size:", X_calib.shape)
    print("Test size:", X_test.shape)

    # -------------------------
    # Base model
    # -------------------------
    base_model = LogisticRegression(max_iter=2000)
    base_model.fit(X_train_scaled, y_train)

    frozen_model = FrozenEstimator(base_model)

    # -------------------------
    # Calibration
    # -------------------------
    platt_model = CalibratedClassifierCV(
        estimator=frozen_model,
        method="sigmoid",
        cv=None
    )
    platt_model.fit(X_calib_scaled, y_calib)

    isotonic_model = CalibratedClassifierCV(
        estimator=frozen_model,
        method="isotonic",
        cv=None
    )
    isotonic_model.fit(X_calib_scaled, y_calib)

    # -------------------------
    # Probabilities
    # -------------------------
    y_proba_base = base_model.predict_proba(X_test_scaled)[:, 1]
    y_proba_platt = platt_model.predict_proba(X_test_scaled)[:, 1]
    y_proba_isotonic = isotonic_model.predict_proba(X_test_scaled)[:, 1]

    # -------------------------
    # Decision Layer (multi-threshold)
    # -------------------------
    risk_levels = pd.Series(y_proba_platt).apply(assign_risk_level)

    # -------------------------
    # Save predictions
    # -------------------------
    os.makedirs("data/metrics", exist_ok=True)

    predictions_df = pd.DataFrame({
        "datetime": df.loc[test_mask, "datetime"].values,
        "y_true": y_test.values,
        "y_proba": y_proba_platt,
        "risk_level": risk_levels.values
    })

    predictions_df.to_csv("data/metrics/predictions_with_risk_levels.csv", index=False)

    print("\nSaved:")
    print("- data/metrics/predictions_with_risk_levels.csv")

    # -------------------------
    # Calibration evaluation
    # -------------------------
    results = []

    models = {
        "baseline": y_proba_base,
        "platt": y_proba_platt,
        "isotonic": y_proba_isotonic,
    }

    for name, proba in models.items():
        results.append({
            "model": name,
            "roc_auc": roc_auc_score(y_test, proba),
            "pr_auc": average_precision_score(y_test, proba),
            "brier_score": brier_score_loss(y_test, proba),
        })

    results_df = pd.DataFrame(results)

    print("\n=== CALIBRATION RESULTS ===")
    print(results_df)

    # -------------------------
    # Threshold analysis (PLATT)
    # -------------------------
    thresholds = [0.3, 0.4, 0.5, 0.6, 0.7]

    threshold_df = evaluate_thresholds(y_test, y_proba_platt, thresholds)
    jump_df = analyze_threshold_jumps(threshold_df)

    print("\n=== THRESHOLD JUMP ANALYSIS ===")
    print(jump_df)

    print("\n=== THRESHOLD ANALYSIS (PLATT) ===")
    print(threshold_df)

    # -------------------------
    # Save metrics
    # -------------------------
    results_df.to_csv("data/metrics/calibration_results.csv", index=False)
    threshold_df.to_csv("data/metrics/threshold_analysis_calibrated.csv", index=False)

    print("\nSaved:")
    print("- data/metrics/calibration_results.csv")
    print("- data/metrics/threshold_analysis_calibrated.csv")


if __name__ == "__main__":
    main()