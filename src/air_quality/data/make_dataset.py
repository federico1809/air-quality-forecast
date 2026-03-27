from __future__ import annotations

from pathlib import Path
import zipfile

import pandas as pd


RAW_PATH = Path("data/raw/beijing_air_quality_raw.zip")
OUTPUT_PATH = Path("data/interim/station_hourly.parquet")


TARGET_FILE = (
    "PRSA_Data_20130301-20170228/"
    "PRSA_Data_Aotizhongxin_20130301-20170228.csv"
)


def load_station_data(zip_path: Path) -> pd.DataFrame:
    with zipfile.ZipFile(zip_path, "r") as z:
        with z.open(TARGET_FILE) as f:
            df = pd.read_csv(f)

    return df


def build_datetime(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["datetime"] = pd.to_datetime(
        df[["year", "month", "day", "hour"]],
        errors="coerce",
    )

    return df


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df.dropna(subset=["datetime"])
    df = df.sort_values("datetime")

    df = df.drop_duplicates(subset=["datetime"])

    return df


def save_dataset(df: pd.DataFrame, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)


def main():
    print("Loading raw data...")
    df = load_station_data(RAW_PATH)

    print("Building datetime...")
    df = build_datetime(df)

    print("Cleaning dataset...")
    df = clean_dataset(df)

    print("Saving interim dataset...")
    save_dataset(df, OUTPUT_PATH)

    print(f"Saved to: {OUTPUT_PATH}")
    print(f"Rows: {len(df)}")


if __name__ == "__main__":
    main()