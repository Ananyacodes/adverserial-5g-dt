from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class BaseCollector(ABC):
	"""Common interface for telemetry sources."""

	@abstractmethod
	def collect(self, rows: int) -> pd.DataFrame:
		"""Collect telemetry rows and return a dataframe."""

