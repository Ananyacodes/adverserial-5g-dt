from __future__ import annotations

import json
from pathlib import Path

import yaml

from attacks.label_flipping.label_flipper import LabelFlipper
from attacks.metric_poisoning.latency_poison import LatencyPoisonAttack
from attacks.metric_poisoning.rsrp_poison import RSRPPoisonAttack
from attacks.metric_poisoning.throughput_poison import ThroughputPoisonAttack
from models.detectors.isolation_forest import IsolationForestDetector
from models.evaluation.metrics import compute_metrics
from telemetry.collectors.mock_collector import MockCollector
from telemetry.collectors.ns3_collector import NS3Collector
from telemetry.processors.cleaner import clean_dataframe
from telemetry.processors.feature_extractor import window_features
from telemetry.processors.normalizer import normalize_train_test


def _load_config() -> dict:
	with open("config.yaml", "r", encoding="utf-8") as handle:
		return yaml.safe_load(handle)


def _get_collector(cfg: dict):
	collector_type = cfg.get("collector", {}).get("type", "mock")
	if collector_type == "ns3_file":
		log_file = cfg.get("collector", {}).get(
			"ns3_log_file", "simulation/ns3/scratch/sample_telemetry_output.csv"
		)
		return NS3Collector(log_file)

	seed = int(cfg["seed"])
	feature_count = int(cfg["data"]["feature_count"])
	anomaly_ratio = float(cfg["data"]["anomaly_ratio"])
	return MockCollector(seed=seed, feature_count=feature_count, anomaly_ratio=anomaly_ratio)


def _prepare_train_test(cfg: dict):
	seed = int(cfg["seed"])
	train_rows = int(cfg["data"]["train_rows"])
	test_rows = int(cfg["data"]["test_rows"])
	window_size = int(cfg["processing"]["window_size"])

	collector = _get_collector(cfg)
	train_df = clean_dataframe(collector.collect(train_rows))
	test_df = clean_dataframe(collector.collect(test_rows))

	train_df = window_features(train_df, window_size=window_size)
	test_df = window_features(test_df, window_size=window_size)
	train_df, test_df, _ = normalize_train_test(train_df, test_df)

	detector = IsolationForestDetector(
		contamination=float(cfg["models"]["isolation_forest"]["contamination"]),
		n_estimators=int(cfg["models"]["isolation_forest"]["n_estimators"]),
		random_state=seed,
	)
	detector.train(train_df)
	return detector, test_df


def _write_json(path: Path, payload: dict) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> None:
	cfg = _load_config()
	detector, clean_test_df = _prepare_train_test(cfg)

	output_dir = Path("experiments/results/phase2")
	output_dir.mkdir(parents=True, exist_ok=True)

	clean_pred = detector.predict(clean_test_df)
	clean_metrics = compute_metrics(clean_test_df["label"], clean_pred)

	attack_results = []

	attack_specs = [
		("label_flipping", LabelFlipper(flip_fraction=0.15, seed=int(cfg["seed"])), True),
		("rsrp_poison", RSRPPoisonAttack(strength_db=8.0), False),
		("latency_poison", LatencyPoisonAttack(offset_ms=8.0), False),
		("throughput_poison", ThroughputPoisonAttack(drop_mbps=12.0), False),
	]

	for attack_name, attack, affects_labels in attack_specs:
		attacked_df = attack.apply(clean_test_df)
		attacked_pred = detector.predict(attacked_df)

		eval_labels = attacked_df["label"] if affects_labels else clean_test_df["label"]
		metrics = compute_metrics(eval_labels, attacked_pred)

		result = {
			"attack": attack_name,
			"row_count": int(len(attacked_df)),
			"label_count_0": int((attacked_df["label"] == 0).sum()),
			"label_count_1": int((attacked_df["label"] == 1).sum()),
			"metrics": metrics,
			"accuracy_delta_vs_clean": metrics["accuracy"] - clean_metrics["accuracy"],
			"precision_delta_vs_clean": metrics["precision"] - clean_metrics["precision"],
			"recall_delta_vs_clean": metrics["recall"] - clean_metrics["recall"],
			"f1_delta_vs_clean": metrics["f1"] - clean_metrics["f1"],
		}
		attack_results.append(result)
		attacked_df.to_csv(output_dir / f"{attack_name}_telemetry.csv", index=False)
		_write_json(output_dir / f"{attack_name}_results.json", result)

	summary = {
		"clean_metrics": clean_metrics,
		"attack_results": attack_results,
	}
	_write_json(output_dir / "phase2_summary.json", summary)

	print("Phase 2 attack summary:")
	print(json.dumps(summary, indent=2))


if __name__ == "__main__":
	main()
