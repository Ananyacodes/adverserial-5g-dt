from collections import deque
import numpy as np

class MedianFilterDefense:
    def __init__(self, window_size=5):
        self.window_size = window_size
        self.buffers = {}
    
    def apply(self, telemetry_df):
        filtered = telemetry_df.copy()
        for ue_id in telemetry_df['ue_id'].unique():
            ue_data = telemetry_df[telemetry_df['ue_id'] == ue_id]
            buffer = deque(maxlen=self.window_size)
            filtered_rsrp = []
            for rsrp in ue_data['rsrp']:
                buffer.append(rsrp)
                filtered_rsrp.append(np.median(buffer))
            filtered.loc[ue_data.index, 'rsrp'] = filtered_rsrp
        return filtered