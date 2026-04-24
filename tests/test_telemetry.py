from telemetry.collectors.mock_collector import MockCollector
from telemetry.processors.cleaner import clean_dataframe
from telemetry.processors.feature_extractor import window_features


def test_mock_collect_and_process():
	collector = MockCollector(seed=1, feature_count=4, anomaly_ratio=0.2)
	df = collector.collect(100)
	assert len(df) == 100
	assert "label" in df.columns

	clean = clean_dataframe(df)
	features = window_features(clean, window_size=5)
	assert len(features) == len(clean)

