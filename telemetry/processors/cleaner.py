from __future__ import annotations

import pandas as pd


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
	"""Simple cleaner: drop duplicates, coerce numeric columns, fill missing values."""

	out = df.drop_duplicates().copy()
	feature_cols = [c for c in out.columns if c != "label"]
	for col in feature_cols:
		out[col] = pd.to_numeric(out[col], errors="coerce")
	out[feature_cols] = out[feature_cols].fillna(out[feature_cols].median())
	out["label"] = out["label"].fillna(0).astype(int)
	return out

