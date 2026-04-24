from telemetry.collectors.mock_collector import MockCollector
from attacks.label_flipping.label_flipper import LabelFlipper


def test_label_flipping_changes_labels():
	df = MockCollector(seed=7).collect(200)
	before = int(df["label"].sum())
	attacked = LabelFlipper(flip_fraction=0.2, seed=7).apply(df)
	after = int(attacked["label"].sum())
	assert before != after

