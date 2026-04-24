from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class BaseDefense(ABC):
	@abstractmethod
	def apply(self, df: pd.DataFrame) -> pd.DataFrame:
		pass

