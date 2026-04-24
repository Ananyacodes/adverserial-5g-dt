.PHONY: setup test phase1 full

setup:
	pip install -r requirements.txt

test:
	pytest -q

phase1:
	python -m experiments.runners.run_phase1_build

full:
	python -m experiments.runners.run_full_grid

