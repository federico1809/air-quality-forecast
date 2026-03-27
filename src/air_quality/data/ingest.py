from pathlib import Path
import hashlib
import urllib.request

from air_quality.config import RAW_DATA_DIR

DATA_URL = (
    "https://archive.ics.uci.edu/ml/machine-learning-databases/00501/"
    "PRSA2017_Data_20130301-20170228.zip"
)

OUTPUT_FILE = RAW_DATA_DIR / "beijing_air_quality_raw.zip"

# Expected SHA256 hash (dataset integrity)
EXPECTED_SHA256 = "PLACEHOLDER_HASH"


def download_file(url: str, destination: Path) -> None:
    """Download file if it does not already exist."""
    destination.parent.mkdir(parents=True, exist_ok=True)

    if destination.exists():
        print("File already exists. Skipping download.")
        return

    print("Downloading dataset...")
    urllib.request.urlretrieve(url, destination)
    print("Download completed.")


def compute_sha256(file_path: Path) -> str:
    """Compute SHA256 hash of a file."""
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def verify_hash(file_path: Path, expected_hash: str) -> None:
    """Verify file integrity."""
    print("Verifying file integrity...")
    file_hash = compute_sha256(file_path)

    if file_hash != expected_hash:
        raise ValueError(
            f"Hash mismatch!\nExpected: {expected_hash}\nGot: {file_hash}"
        )

    print("Hash verification passed.")


def main():
    download_file(DATA_URL, OUTPUT_FILE)

    # Temporarily print hash so we can register it
    file_hash = compute_sha256(OUTPUT_FILE)
    print(f"Computed SHA256: {file_hash}")

    # Uncomment after first run
    # verify_hash(OUTPUT_FILE, EXPECTED_SHA256)


if __name__ == "__main__":
    main()