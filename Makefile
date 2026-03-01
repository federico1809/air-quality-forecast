.PHONY: help data

help:
	@echo "Available commands:"
	@echo "  make data    Download and validate raw dataset"

data:
	@echo "[DATA] Starting data acquisition pipeline..."
	python -m src.data.download_dataset