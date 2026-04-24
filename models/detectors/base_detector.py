from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class BaseDetector(ABC):
	@abstractmethod
	def train(self, train_df: pd.DataFrame) -> None:
		pass

	@abstractmethod
	def predict(self, test_df: pd.DataFrame) -> pd.Series:
		pass

