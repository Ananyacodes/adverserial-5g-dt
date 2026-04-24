import pandas as pd

from defenses.sanitization.clipping import ClippingDefense


def test_clipping_defense_bounds_values():
	df = pd.DataFrame({"metric_0": [-10.0, 0.0, 10.0], "label": [0, 0, 1]})
	out = ClippingDefense(min_value=-2.0, max_value=2.0).apply(df)
	assert out["metric_0"].min() >= -2.0
	assert out["metric_0"].max() <= 2.0

