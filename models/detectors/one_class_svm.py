from __future__ import annotations

import pandas as pd
from sklearn.svm import OneClassSVM

from models.detectors.base_detector import BaseDetector


class OneClassSVMDetector(BaseDetector):
	def __init__(self, nu: float = 0.08, gamma: str = "scale"):
		self.model = OneClassSVM(nu=nu, gamma=gamma)

	def train(self, train_df: pd.DataFrame) -> None:
		x = train_df.drop(columns=["label"])
		self.model.fit(x)

	def predict(self, test_df: pd.DataFrame) -> pd.Series:
		x = test_df.drop(columns=["label"])
		pred = self.model.predict(x)
		return pd.Series((pred == -1).astype(int), index=test_df.index)

