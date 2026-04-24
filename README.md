# Adversarial 5G Digital Twin (MVP)

This repository hosts a layered research framework for:

- 5G simulation and telemetry generation
- telemetry cleaning and feature extraction
- anomaly detection models
- adversarial attack emulation
- defense evaluation

The current implementation provides a runnable MVP baseline so the full structure can be developed incrementally.

## Quick Start

1. Create a Python virtual environment.
2. Install dependencies.
3. Run baseline tests.
4. Run phase 1 baseline pipeline.

Commands:

- `python -m venv .venv`
- `.venv\\Scripts\\Activate.ps1`
- `pip install -r requirements.txt`
- `pytest -q`
- `python -m experiments.runners.run_phase1_build`

## What Works Now

- Synthetic telemetry generation via mock collector
- Cleaning, normalization, and window feature extraction
- Isolation Forest and One-Class SVM detector wrappers
- Label flipping attack utility
- Clipping and outlier defense utilities
- Phase 1 baseline runner writing metrics JSON

## Next Build Steps

- Replace mock telemetry with ns-3 ingestion
- Add attack/defense experiment runners for all phases
- Add richer model benchmarking and plotting
- Populate notebooks and paper artifact generation

