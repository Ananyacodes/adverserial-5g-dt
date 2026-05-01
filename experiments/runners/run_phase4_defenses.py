from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import yaml

from attacks.label_flipping.label_flipper import LabelFlipper
from attacks.metric_poisoning.latency_poison import LatencyPoisonAttack
from attacks.metric_poisoning.rsrp_poison import RSRPPoisonAttack
from attacks.metric_poisoning.throughput_poison import ThroughputPoisonAttack
from defenses.sanitization.clipping import ClippingDefense
from defenses.sanitization.median_filter import MedianFilterDefense
from defenses.sanitization.outlier_removal import ZScoreOutlierDefense
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


def _apply_defense(defense_name: str, df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    if defense_name == "none":
        defended = df.copy()
    elif defense_name == "clipping":
        defended = ClippingDefense(min_value=-5.0, max_value=5.0).apply(df)
    elif defense_name == "outlier_removal":
        defended = ZScoreOutlierDefense(threshold=3.5).apply(df)
    elif defense_name == "median_filter":
        defended = MedianFilterDefense(window_size=5).apply(df)
    elif defense_name == "clip_then_outlier":
        defended = ZScoreOutlierDefense(threshold=3.5).apply(
            ClippingDefense(min_value=-5.0, max_value=5.0).apply(df)
        )
    elif defense_name == "clip_then_median":
        defended = MedianFilterDefense(window_size=5).apply(
            ClippingDefense(min_value=-5.0, max_value=5.0).apply(df)
        )
    else:
        raise ValueError(f"Unknown defense: {defense_name}")

    retained_fraction = float(len(defended) / max(len(df), 1))
    defense_cost = 1.0 - retained_fraction
    summary = {
        "rows_before": int(len(df)),
        "rows_after": int(len(defended)),
        "retained_fraction": retained_fraction,
        "defense_cost": defense_cost,
    }
    return defended.reset_index(drop=True), summary


def _attack_variants(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    variants = {
        "clean": df.copy(),
        "label_flipping": LabelFlipper(flip_fraction=0.15, seed=42).apply(df),
        "rsrp_poison": RSRPPoisonAttack(strength_db=8.0).apply(df),
        "latency_poison": LatencyPoisonAttack(offset_ms=8.0).apply(df),
        "throughput_poison": ThroughputPoisonAttack(drop_mbps=12.0).apply(df),
    }
    return variants


def main() -> None:
    cfg = _load_config()
    detector, clean_test_df = _prepare_train_test(cfg)

    output_dir = Path("experiments/results/phase4")
    output_dir.mkdir(parents=True, exist_ok=True)

    attack_variants = _attack_variants(clean_test_df)
    defense_names = [
        "none",
        "clipping",
        "outlier_removal",
        "median_filter",
        "clip_then_outlier",
        "clip_then_median",
    ]

    clean_pred = detector.predict(clean_test_df)
    clean_metrics = compute_metrics(clean_test_df["label"], clean_pred)

    rows = []
    for attack_name, attacked_df in attack_variants.items():
        for defense_name in defense_names:
            defended_df, defense_summary = _apply_defense(defense_name, attacked_df)

            if defended_df.empty:
                metrics = {"accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1": 0.0}
                kept_labels = []
                prediction_count = 0
            else:
                pred = detector.predict(defended_df)
                metrics = compute_metrics(defended_df["label"], pred)
                kept_labels = defended_df["label"].tolist()
                prediction_count = int(len(pred))

            row = {
                "attack": attack_name,
                "defense": defense_name,
                "prediction_count": prediction_count,
                "label_count_0": int(sum(label == 0 for label in kept_labels)),
                "label_count_1": int(sum(label == 1 for label in kept_labels)),
                "accuracy": metrics["accuracy"],
                "precision": metrics["precision"],
                "recall": metrics["recall"],
                "f1": metrics["f1"],
                "accuracy_delta_vs_clean": metrics["accuracy"] - clean_metrics["accuracy"],
                "precision_delta_vs_clean": metrics["precision"] - clean_metrics["precision"],
                "recall_delta_vs_clean": metrics["recall"] - clean_metrics["recall"],
                "f1_delta_vs_clean": metrics["f1"] - clean_metrics["f1"],
                **defense_summary,
            }
            rows.append(row)

    results_df = pd.DataFrame(rows)
    results_csv = output_dir / "defense_stack_results.csv"
    results_df.to_csv(results_csv, index=False)

    best_by_f1 = (
        results_df.sort_values(["f1", "retained_fraction"], ascending=[False, False])
        .head(1)
        .to_dict(orient="records")[0]
    )

    summary = {
        "clean_metrics": clean_metrics,
        "results_csv": str(results_csv),
        "best_by_f1": best_by_f1,
        "results": rows,
    }
    (output_dir / "phase4_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("Phase 4 defense summary:")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()