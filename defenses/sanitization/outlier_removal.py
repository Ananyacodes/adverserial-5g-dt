from __future__ import annotations

import numpy as np
import pandas as pd

from defenses.base_defense import BaseDefense


class ZScoreOutlierDefense(BaseDefense):
	def __init__(self, threshold: float = 3.5):
		self.threshold = threshold

	def apply(self, df: pd.DataFrame) -> pd.DataFrame:
		out = df.copy()
		feature_cols = [c for c in out.columns if c != "label"]
		z = (out[feature_cols] - out[feature_cols].mean()) / (out[feature_cols].std(ddof=0) + 1e-9)
		keep = (np.abs(z) <= self.threshold).all(axis=1)
		return out.loc[keep].reset_index(drop=True)

