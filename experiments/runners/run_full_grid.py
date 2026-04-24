from __future__ import annotations

from experiments.runners.run_phase1_build import main as run_phase1


def main() -> None:
	# MVP orchestration: expand to phase2/3/4 as implementations are added.
	run_phase1()


if __name__ == "__main__":
	main()

