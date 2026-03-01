# ===== Project name =====
$PROJECT = "air-quality-forecast"
$BASE = "C:\Users\feder\Documents\data_repos\$PROJECT"

Write-Host "Creating project at $BASE"

# ===== Folder structure =====
$folders = @(
"$BASE\data\raw",
"$BASE\data\interim",
"$BASE\data\processed",
"$BASE\reports",
"$BASE\notebooks",
"$BASE\src\data",
"$BASE\tests"
)

foreach ($folder in $folders) {
    New-Item -ItemType Directory -Force -Path $folder | Out-Null
}

# ===== Python init files =====
New-Item "$BASE\src\__init__.py" -ItemType File -Force | Out-Null
New-Item "$BASE\src\data\__init__.py" -ItemType File -Force | Out-Null

# ===== make_dataset placeholder =====
@"
def main():
    print("Dataset pipeline placeholder")

if __name__ == "__main__":
    main()
"@ | Set-Content "$BASE\src\data\make_dataset.py"

# ===== .gitkeep files =====
New-Item "$BASE\data\raw\.gitkeep" -ItemType File -Force | Out-Null
New-Item "$BASE\data\interim\.gitkeep" -ItemType File -Force | Out-Null
New-Item "$BASE\data\processed\.gitkeep" -ItemType File -Force | Out-Null
New-Item "$BASE\reports\.gitkeep" -ItemType File -Force | Out-Null

# ===== .gitignore =====
@"
# Python
__pycache__/
*.pyc
.env
.venv/

# Data
data/raw/*
data/interim/*
data/processed/*

# Keep folders
!data/raw/.gitkeep
!data/interim/.gitkeep
!data/processed/.gitkeep

# Reports
reports/*
!reports/.gitkeep

# Jupyter
.ipynb_checkpoints/

# OS
.DS_Store
Thumbs.db
"@ | Set-Content "$BASE\.gitignore"

# ===== README =====
@"
# Air Quality Forecasting & Early Warning System

End-to-end machine learning project for probabilistic PM2.5 forecasting
and operational air quality alert generation.

Status: Phase B — Data System Development
"@ | Set-Content "$BASE\README.md"

# ===== Makefile =====
@"
.PHONY: data clean-data

data:
	python -m src.data.make_dataset

clean-data:
	rm -rf data/interim/*
	rm -rf reports/*
"@ | Set-Content "$BASE\Makefile"

Write-Host "Project structure created successfully."