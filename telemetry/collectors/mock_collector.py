from __future__ import annotations

import numpy as np
import pandas as pd

from telemetry.collectors.base_collector import BaseCollector


class MockCollector(BaseCollector):
	"""Generates synthetic telemetry with a configurable anomaly ratio."""

	def __init__(self, seed: int = 42, feature_count: int = 6, anomaly_ratio: float = 0.1):
		self._rng = np.random.default_rng(seed)
		self.feature_count = feature_count
		self.anomaly_ratio = anomaly_ratio

	def collect(self, rows: int) -> pd.DataFrame:
		normal_rows = int(rows * (1.0 - self.anomaly_ratio))
		anomaly_rows = max(1, rows - normal_rows)

		normal = self._rng.normal(loc=0.0, scale=1.0, size=(normal_rows, self.feature_count))
		anomalies = self._rng.normal(loc=4.0, scale=1.5, size=(anomaly_rows, self.feature_count))

		data = np.vstack([normal, anomalies])
		labels = np.concatenate([np.zeros(normal_rows, dtype=int), np.ones(anomaly_rows, dtype=int)])

		perm = self._rng.permutation(rows)
		data = data[perm]
		labels = labels[perm]

		columns = [f"metric_{i}" for i in range(self.feature_count)]
		df = pd.DataFrame(data, columns=columns)
		df["label"] = labels
		return df

