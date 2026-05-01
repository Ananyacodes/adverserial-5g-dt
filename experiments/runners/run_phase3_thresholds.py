from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import yaml

from attacks.metric_poisoning.rsrp_poison import RSRPPoisonAttack
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


def _prepare_data(cfg: dict):
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
    detector, clean_test_df = _prepare_data(cfg)

    output_dir = Path("experiments/results/phase3")
    output_dir.mkdir(parents=True, exist_ok=True)

    clean_pred = detector.predict(clean_test_df)
    clean_metrics = compute_metrics(clean_test_df["label"], clean_pred)

    strengths = [1, 2, 3, 5, 7, 10, 12, 15, 20]
    attack = RSRPPoisonAttack()

    rows = []
    threshold_strength = None

    for strength in strengths:
        attack.strength_db = strength
        poisoned_df = attack.apply(clean_test_df)
        poisoned_pred = detector.predict(poisoned_df)

        metrics = compute_metrics(clean_test_df["label"], poisoned_pred)
        flip_rate = float((poisoned_pred != clean_pred).mean())
        anomaly_rate = float(poisoned_pred.mean())

        row = {
            "poison_strength_db": float(strength),
            "flip_rate": flip_rate,
            "anomaly_rate": anomaly_rate,
            "accuracy": metrics["accuracy"],
            "precision": metrics["precision"],
            "recall": metrics["recall"],
            "f1": metrics["f1"],
        }
        rows.append(row)

        if threshold_strength is None and flip_rate >= 0.5:
            threshold_strength = float(strength)

    results_df = pd.DataFrame(rows)
    results_csv = output_dir / "rsrp_thresholds.csv"
    results_df.to_csv(results_csv, index=False)

    summary = {
        "clean_metrics": clean_metrics,
        "threshold_strength_db": threshold_strength,
        "results_csv": str(results_csv),
        "strengths_tested": strengths,
        "results": rows,
    }
    _write_json(output_dir / "rsrp_threshold_summary.json", summary)

    print("Phase 3 threshold summary:")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()