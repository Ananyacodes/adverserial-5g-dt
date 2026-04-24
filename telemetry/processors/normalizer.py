from __future__ import annotations

from typing import Tuple

import pandas as pd
from sklearn.preprocessing import StandardScaler


def normalize_train_test(
	train_df: pd.DataFrame, test_df: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame, StandardScaler]:
	"""Fit scaler on train, transform train and test feature columns."""

	feature_cols = [c for c in train_df.columns if c != "label"]
	scaler = StandardScaler()
	train_x = scaler.fit_transform(train_df[feature_cols])
	test_x = scaler.transform(test_df[feature_cols])

	train_out = pd.DataFrame(train_x, columns=feature_cols)
	test_out = pd.DataFrame(test_x, columns=feature_cols)
	train_out["label"] = train_df["label"].to_numpy()
	test_out["label"] = test_df["label"].to_numpy()
	return train_out, test_out, scaler

