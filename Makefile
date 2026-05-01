.PHONY: setup test phase1 phase2 phase3 phase4 full

setup:
	pip install -r requirements.txt

test:
	pytest -q

phase1:
	python -m experiments.runners.run_phase1_build

phase2:
	python -m experiments.runners.run_phase2_attacks

phase3:
	python -m experiments.runners.run_phase3_thresholds

phase4:
	python -m experiments.runners.run_phase4_defenses

full:
	python -m experiments.runners.run_full_grid

