.PHONY: data clean-data

data:
	python -m src.data.make_dataset

clean-data:
	rm -rf data/interim/*
	rm -rf reports/*
