from __future__ import annotations

import pandas as pd

from defenses.base_defense import BaseDefense


class ClippingDefense(BaseDefense):
	def __init__(self, min_value: float = -5.0, max_value: float = 5.0):
		self.min_value = min_value
		self.max_value = max_value

	def apply(self, df: pd.DataFrame) -> pd.DataFrame:
		out = df.copy()
		feature_cols = [c for c in out.columns if c != "label"]
		out[feature_cols] = out[feature_cols].clip(self.min_value, self.max_value)
		return out

