from pathlib import Path

from experiments.runners.run_phase1_build import main


def test_phase1_runner_writes_metrics_file():
	main()
	assert Path("experiments/results/phase1/baseline_metrics.json").exists()

