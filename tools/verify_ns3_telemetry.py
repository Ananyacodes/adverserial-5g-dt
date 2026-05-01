from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify ns-3 telemetry and emit proof metadata.")
    parser.add_argument("csv", help="Path to the telemetry CSV file")
    parser.add_argument(
        "--provenance",
        help="Optional provenance JSON path to validate or create",
        default=None,
    )
    parser.add_argument(
        "--output",
        help="Optional proof JSON path to write (defaults to <csv>.proof.json)",
        default=None,
    )
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        raise FileNotFoundError(f"Telemetry CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)
    expected_columns = ["timestamp", "ue_id", "rsrp", "latency", "throughput", "label"]
    missing_columns = [column for column in expected_columns if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing expected telemetry columns: {missing_columns}")

    proof = {
        "telemetry_csv": str(csv_path),
        "telemetry_csv_sha256": sha256_file(csv_path),
        "row_count": int(len(df)),
        "label_counts": {str(key): int(value) for key, value in df["label"].value_counts().sort_index().items()},
        "timestamp_min": float(df["timestamp"].min()),
        "timestamp_max": float(df["timestamp"].max()),
        "source": "ns-3 generated telemetry",
    }

    if args.provenance:
        provenance_path = Path(args.provenance)
        if provenance_path.exists():
            proof["provenance_json"] = str(provenance_path)
            with provenance_path.open("r", encoding="utf-8") as handle:
                proof["provenance_json_contents"] = json.load(handle)

    output_path = Path(args.output) if args.output else csv_path.with_suffix(".proof.json")
    output_path.write_text(json.dumps(proof, indent=2), encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())