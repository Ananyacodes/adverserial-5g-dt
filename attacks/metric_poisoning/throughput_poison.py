from __future__ import annotations

import pandas as pd


class ThroughputPoisonAttack:
	def __init__(self, drop_mbps: float = 10.0):
		self.drop_mbps = drop_mbps

	def apply(self, telemetry_df: pd.DataFrame) -> pd.DataFrame:
		"""Decrease throughput by a fixed amount, bounded at zero."""
		poisoned = telemetry_df.copy()
		poisoned["throughput"] = (poisoned["throughput"] - self.drop_mbps).clip(lower=0)
		return poisoned
