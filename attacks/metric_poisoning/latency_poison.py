from __future__ import annotations

import pandas as pd


class LatencyPoisonAttack:
	def __init__(self, offset_ms: float = 5.0):
		self.offset_ms = offset_ms

	def apply(self, telemetry_df: pd.DataFrame) -> pd.DataFrame:
		"""Increase latency by a fixed offset."""
		poisoned = telemetry_df.copy()
		poisoned["latency"] = poisoned["latency"] + self.offset_ms
		return poisoned
