import pandas as pd
from pathlib import Path


def load_data():
    path = Path("data/processed/features.parquet")
    return pd.read_parquet(path)


def temporal_split(df: pd.DataFrame, test_size: float = 0.2):
    df = df.sort_values("datetime")

    split_idx = int(len(df) * (1 - test_size))

    train = df.iloc[:split_idx]
    test = df.iloc[split_idx:]

    return train, test


def main():
    df = load_data()

    train, test = temporal_split(df)

    print("Train shape:", train.shape)
    print("Test shape:", test.shape)

    print("Train period:", train["datetime"].min(), "→", train["datetime"].max())
    print("Test period:", test["datetime"].min(), "→", test["datetime"].max())


if __name__ == "__main__":
    main()