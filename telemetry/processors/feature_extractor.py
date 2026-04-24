from __future__ import annotations

import pandas as pd


def window_features(df: pd.DataFrame, window_size: int = 8) -> pd.DataFrame:
	"""Aggregate telemetry into rolling-window means to smooth bursts/noise."""

	if window_size < 1:
		raise ValueError("window_size must be >= 1")

	feature_cols = [c for c in df.columns if c != "label"]
	rolled = df[feature_cols].rolling(window=window_size, min_periods=1).mean()
	out = rolled.copy()
	out["label"] = df["label"].rolling(window=window_size, min_periods=1).max().astype(int)
	return out

