from __future__ import annotations

from typing import List

import pandas as pd

from models.detectors.base_detector import BaseDetector


class EnsembleDetector(BaseDetector):
	def __init__(self, detectors: List[BaseDetector], threshold: float = 0.5):
		self.detectors = detectors
		self.threshold = threshold

	def train(self, train_df: pd.DataFrame) -> None:
		for detector in self.detectors:
			detector.train(train_df)

	def predict(self, test_df: pd.DataFrame) -> pd.Series:
		if not self.detectors:
			raise ValueError("Ensemble must include at least one detector")
		preds = pd.concat([d.predict(test_df) for d in self.detectors], axis=1)
		score = preds.mean(axis=1)
		return (score >= self.threshold).astype(int)

