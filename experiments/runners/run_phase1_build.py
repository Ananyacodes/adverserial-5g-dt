from __future__ import annotations

import json
from pathlib import Path

import yaml

from models.detectors.isolation_forest import IsolationForestDetector
from models.evaluation.metrics import compute_metrics
from telemetry.collectors.mock_collector import MockCollector
from telemetry.collectors.ns3_collector import NS3Collector
from telemetry.processors.cleaner import clean_dataframe
from telemetry.processors.feature_extractor import window_features
from telemetry.processors.normalizer import normalize_train_test


def _load_config() -> dict:
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _get_collector(cfg: dict):
    """Select collector based on config type."""
    collector_type = cfg.get("collector", {}).get("type", "mock")
    
    if collector_type == "ns3_file":
        log_file = cfg.get("collector", {}).get("ns3_log_file", "simulation/ns3/scratch/sample_telemetry_output.csv")
        return NS3Collector(log_file)
    else:  # default to mock
        seed = int(cfg["seed"])
        feature_count = int(cfg["data"]["feature_count"])
        anomaly_ratio = float(cfg["data"]["anomaly_ratio"])
        return MockCollector(seed=seed, feature_count=feature_count, anomaly_ratio=anomaly_ratio)


def main() -> None:
    cfg = _load_config()
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
    pred = detector.predict(test_df)
    metrics = compute_metrics(test_df["label"], pred)

    output_path = Path(cfg["paths"]["baseline_metrics"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print("Phase 1 baseline metrics:")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()


