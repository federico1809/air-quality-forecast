import pandas as pd
from pathlib import Path


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df.sort_values("datetime")

    # --- Target ---
    df["target"] = df["PM2.5"].shift(-24)

    # --- Lags ---
    lags = [1, 2, 3, 6, 12, 24, 48, 72]
    for lag in lags:
        df[f"lag_{lag}"] = df["PM2.5"].shift(lag)

    # --- Rolling ---
    windows = [6, 12, 24]
    for w in windows:
        df[f"rolling_mean_{w}"] = df["PM2.5"].shift(1).rolling(w).mean()
        df[f"rolling_std_{w}"] = df["PM2.5"].shift(1).rolling(w).std()

    # --- Time features ---
    df["hour"] = pd.to_datetime(df["datetime"]).dt.hour
    df["day_of_week"] = pd.to_datetime(df["datetime"]).dt.dayofweek
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)

    # --- Drop NaNs ---
    df = df.dropna()

    return df


def main():
    input_path = Path("data/interim/station_hourly.parquet")
    output_path = Path("data/processed/features.parquet")

    df = pd.read_parquet(input_path)

    features_df = build_features(df)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    features_df.to_parquet(output_path, index=False)

    print(f"Features saved to: {output_path}")
    print(f"Shape: {features_df.shape}")


if __name__ == "__main__":
    main()