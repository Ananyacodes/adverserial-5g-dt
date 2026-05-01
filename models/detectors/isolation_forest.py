from __future__ import annotations

import pandas as pd
from sklearn.ensemble import IsolationForest

from models.detectors.base_detector import BaseDetector


class IsolationForestDetector(BaseDetector):
    def __init__(self, contamination: float = 0.1, n_estimators: int = 200, random_state: int = 42):
        self.model = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            random_state=random_state,
        )

    def train(self, train_df: pd.DataFrame) -> None:
        x = train_df.drop(columns=["label"])
        self.model.fit(x)

    def predict(self, test_df: pd.DataFrame) -> pd.Series:
        x = test_df.drop(columns=["label"])
        # sklearn: 1 normal, -1 anomaly
        pred = self.model.predict(x)
        return pd.Series((pred == -1).astype(int), index=test_df.index)