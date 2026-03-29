import pandas as pd
import numpy as np

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    precision_score,
    recall_score,
    f1_score,
    accuracy_score,
    roc_auc_score,
    average_precision_score,
)
from sklearn.preprocessing import StandardScaler

import os
os.makedirs("data/metrics", exist_ok=True)


TARGET_THRESHOLD = 35.0
DECISION_THRESHOLD = 0.4


def main():
    # -------------------------
    # Load data
    # -------------------------
    df = pd.read_parquet("data/processed/features.parquet")
    df["datetime"] = pd.to_datetime(df["datetime"])

    # -------------------------
    # Define target
    # -------------------------
    # Positive class: unhealthy air quality (PM2.5 >= 35 µg/m³)
    y = (df["target"] >= TARGET_THRESHOLD).astype(int)

    # -------------------------
    # Define features
    # -------------------------
    # Keep PM2.5 because it is a valid observed feature at time t.
    EXCLUDED_COLUMNS = [
        "No",
        "year",
        "month",
        "day",
        "datetime",
        "station",
        "target",
        "wd",
    ]

    X = df.drop(columns=EXCLUDED_COLUMNS)

    # -------------------------
    # Temporal split
    # -------------------------
    cutoff = pd.Timestamp("2016-05-22 14:00:00")

    train_mask = df["datetime"] <= cutoff
    test_mask = df["datetime"] > cutoff

    X_train = X.loc[train_mask]
    X_test = X.loc[test_mask]

    y_train = y.loc[train_mask]
    y_test = y.loc[test_mask]

    # -------------------------
    # Scaling
    # -------------------------
    scaler = StandardScaler()

    X_train_scaled = pd.DataFrame(
        scaler.fit_transform(X_train),
        columns=X_train.columns,
        index=X_train.index,
    )

    X_test_scaled = pd.DataFrame(
        scaler.transform(X_test),
        columns=X_test.columns,
        index=X_test.index,
    )

    # -------------------------
    # Train model
    # -------------------------
    model = LogisticRegression(max_iter=2000)
    model.fit(X_train_scaled, y_train)

    # -------------------------
    # Predictions
    # -------------------------
    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
    # -------------------------
    # Threshold analysis
    # -------------------------
    thresholds = [0.3, 0.4, 0.5, 0.6, 0.7]

    results = []

    for t in thresholds:
        y_pred_t = (y_pred_proba >= t).astype(int)

        tn, fp, fn, tp = confusion_matrix(y_test, y_pred_t).ravel()

        precision = precision_score(y_test, y_pred_t, zero_division=0)
        recall = recall_score(y_test, y_pred_t, zero_division=0)
        f1 = f1_score(y_test, y_pred_t, zero_division=0)
        accuracy = accuracy_score(y_test, y_pred_t)

        alert_rate = y_pred_t.mean()

        results.append({
            "threshold": t,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "false_negatives": fn,
            "false_positives": fp,
            "true_positives": tp,
            "true_negatives": tn,
            "alert_rate": alert_rate,
        })

    results_df = pd.DataFrame(results)

    output_path = "data/metrics/threshold_analysis.csv"
    results_df.to_csv(output_path, index=False)

    print("\n=== THRESHOLD ANALYSIS ===")
    print(results_df)
    print(f"\nSaved to: {output_path}")

    y_pred = (y_pred_proba >= DECISION_THRESHOLD).astype(int)

    # -------------------------
    # Evaluation
    # -------------------------
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    pr_auc = average_precision_score(y_test, y_pred_proba)

    print("=== BINARY BASELINE RESULTS ===")
    print(f"Threshold for positive class: PM2.5 >= {TARGET_THRESHOLD:.0f}")
    print(f"Decision threshold: {DECISION_THRESHOLD:.2f}")
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1:        {f1:.4f}")
    print(f"ROC AUC:   {roc_auc:.4f}")
    print(f"PR AUC:    {pr_auc:.4f}")

    # -------------------------
    # Confusion matrix
    # -------------------------
    labels = ["not_unhealthy", "unhealthy"]
    cm = confusion_matrix(y_test, y_pred)

    print("\n=== CONFUSION MATRIX ===")
    print(pd.DataFrame(cm, index=labels, columns=labels))

    print("\n=== CLASSIFICATION REPORT ===")
    print(classification_report(
        y_test,
        y_pred,
        target_names=labels,
        zero_division=0,
    ))

    # -------------------------
    # Feature importance (coefficients)
    # -------------------------
    coefficients = pd.Series(model.coef_[0], index=X_train.columns)
    coefficients = coefficients.sort_values(key=abs, ascending=False)

    print("\n=== TOP 10 FEATURES (by absolute coefficient) ===")
    print(coefficients.head(10))

    # -------------------------
    # Target distribution (context)
    # -------------------------
    print("\n=== TARGET DISTRIBUTION (TEST) ===")
    print(f"Positive rate (unhealthy): {y_test.mean():.4f}")
    print(f"Negative rate (not_unhealthy): {(1 - y_test.mean()):.4f}")

    # -------------------------
    # Naive baseline
    # -------------------------
    # Predict unhealthy if PM2.5 observed 24h ago was already unhealthy.
    naive_pred = (df.loc[test_mask, "lag_24"] >= TARGET_THRESHOLD).astype(int)

    naive_accuracy = accuracy_score(y_test, naive_pred)
    naive_precision = precision_score(y_test, naive_pred, zero_division=0)
    naive_recall = recall_score(y_test, naive_pred, zero_division=0)
    naive_f1 = f1_score(y_test, naive_pred, zero_division=0)

    print("\n=== NAIVE BASELINE (lag_24 >= threshold) ===")
    print(f"Accuracy:  {naive_accuracy:.4f}")
    print(f"Precision: {naive_precision:.4f}")
    print(f"Recall:    {naive_recall:.4f}")
    print(f"F1:        {naive_f1:.4f}")


if __name__ == "__main__":
    main()