from __future__ import annotations

import numpy as np
import pandas as pd

from attacks.base_attack import BaseAttack


class LabelFlipper(BaseAttack):
	def __init__(self, flip_fraction: float = 0.1, seed: int = 42):
		if not 0.0 <= flip_fraction <= 1.0:
			raise ValueError("flip_fraction must be between 0 and 1")
		self.flip_fraction = flip_fraction
		self.rng = np.random.default_rng(seed)

	def apply(self, df: pd.DataFrame) -> pd.DataFrame:
		out = df.copy()
		n = len(out)
		k = int(n * self.flip_fraction)
		if k == 0:
			return out
		idx = self.rng.choice(out.index.to_numpy(), size=k, replace=False)
		out.loc[idx, "label"] = 1 - out.loc[idx, "label"].astype(int)
		return out

