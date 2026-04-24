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

from sklearn.ensemble import IsolationForest
import joblib

class IsolationForestDetector:
    def __init__(self, contamination=0.05):
        self.model = IsolationForest(contamination=contamination)
    
    def train(self, features_df):
        self.model.fit(features_df)
        return self
    
    def predict(self, features_df):
        predictions = self.model.predict(features_df)
        return (predictions == -1).astype(int)
    
    def save(self, path):
        joblib.dump(self.model, path)
    
    def load(self, path):
        self.model = joblib.load(path)