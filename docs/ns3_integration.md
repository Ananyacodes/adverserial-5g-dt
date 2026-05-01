# NS-3 Simulation & Telemetry Integration

This document describes how ns-3 5G simulations are integrated into the adversarial framework.

## Overview

The simulation layer uses ns-3 (Network Simulator 3) to generate realistic 5G UE telemetry with controllable scenarios (benign, attacked, defended).

Outputs from ns-3 simulations are ingested by the telemetry pipeline via CSV files or live TCP sockets.

## Quick Start

### Without NS-3 Installed (Recommended for MVP)

Use the pre-generated sample telemetry:

```bash
python -m experiments.runners.run_phase1_build
```

This uses `simulation/ns3/scratch/sample_telemetry_output.csv` by default, which contains:
- **Benign period** (t=0-1s): 3 UEs with stable RSRP, latency, throughput
- **Anomaly period** (t=1-1.5s): All UEs show signal degradation, high latency, low throughput

### With NS-3 Installed

1. **Install ns-3 in a separate checkout** (Ubuntu/Linux example):
   ```bash
   cd ~/ns-3
   git clone https://gitlab.com/nsnam/ns-3-dev.git .
   ./waf configure --build-profile=optimized
   ./waf build
   ```

2. **Copy the baseline simulation script into ns-3**:
   ```bash
   cp /path/to/adversarial-5g-dt/simulation/ns3/scratch/5g_baseline.cc scratch/
   ```

3. **Run simulation and generate telemetry**:
   ```bash
   ./ns3 run "scratch/5g_baseline"
   ```
   Output: `scratch/5g_baseline_telemetry.csv`

4. **Generate proof metadata for the CSV**:
   ```bash
   python3 /path/to/adversarial-5g-dt/tools/verify_ns3_telemetry.py \
     /path/to/ns-3/scratch/5g_baseline_telemetry.csv \
     --provenance /path/to/ns-3/scratch/5g_baseline_telemetry.provenance.json
   ```
   Output: `/path/to/ns-3/scratch/5g_baseline_telemetry.proof.json`

5. **Update config.yaml** to use the generated file:
   ```yaml
   collector:
     type: "ns3_file"
     ns3_log_file: "/path/to/ns-3/scratch/5g_baseline_telemetry.csv"
   ```

6. **Run baseline with real 5G telemetry**:
   ```bash
   python -m experiments.runners.run_phase1_build
   ```

## Telemetry CSV Format

Expected columns (order matters):

| Column | Description | Range | Units |
|--------|-------------|-------|-------|
| `timestamp` | Simulation time | 0-2.0 | seconds |
| `ue_id` | User Equipment ID | 1-3 | integer |
| `rsrp` | Reference Signal Received Power | -140 to -44 | dBm |
| `latency` | RTT | 10-100 | milliseconds |
| `throughput` | Data rate | 10-100 | Mbps |
| `label` | 0=benign, 1=anomaly | 0 or 1 | integer |

Optional columns (will be preserved):
- `jitter`, `packet_loss`, `handover_count`, `interference_level`, etc.

## Simulation Scripts

### 5g_baseline.cc
- 3 UEs, 1 gNB
- Benign behavior: normal RSRP, latency, throughput
- Anomaly period: signal degradation, congestion
- Default output path: `scratch/5g_baseline_telemetry.csv` in the ns-3 checkout

### 5g_with_mobility.cc (planned)
- UE handovers between cells
- Mobility-induced telemetry shifts

### 5g_with_attack.cc (planned)
- Integrated attack scenarios (jamming, spoofing, etc.)
- Attack injection at simulation level

## Extending the Simulation

To add new scenarios:

1. Create a new `.cc` file in `simulation/ns3/scratch/`
2. Implement telemetry collection in CSV format
3. Output to `simulation/ns3/scratch/{scenario}_telemetry.csv`
4. Update `config.yaml` with the new log file path
5. Tests and pipeline will automatically work with the new data

## Collector Classes

### NS3Collector
Reads static CSV files exported by ns-3. Best for reproducible experiments.

```python
from telemetry.collectors.ns3_collector import NS3Collector
collector = NS3Collector("simulation/ns3/scratch/5g_baseline_telemetry.csv")
df = collector.collect(rows=500)
```

### NS3SocketCollector (Experimental)
Connects to a live ns-3 simulation via TCP socket for real-time telemetry streaming.

```python
from telemetry.collectors.ns3_collector import NS3SocketCollector
collector = NS3SocketCollector(host='localhost', port=5555)
df = collector.collect(rows=1000)
```

## Validation

Verify telemetry format and compatibility:

```bash
python -c "
from telemetry.collectors.ns3_collector import NS3Collector
df = NS3Collector('simulation/ns3/scratch/sample_telemetry_output.csv').collect()
print(f'Rows: {len(df)}, Columns: {list(df.columns)}')
print(df.describe())
"
```

To attach proof for a real run, include the provenance JSON and proof JSON produced by `tools/verify_ns3_telemetry.py` alongside the CSV.

## Phase 3 Threshold Run

Run the RSRP threshold sweep after the phase 1 baseline:

```bash
python -m experiments.runners.run_phase3_thresholds
```

Outputs:
- `experiments/results/phase3/rsrp_thresholds.csv`
- `experiments/results/phase3/rsrp_threshold_summary.json`

## Phase 4 Defense Stack Run

Run the defense stacking sweep after the phase 3 threshold run:

```bash
python -m experiments.runners.run_phase4_defenses
```

Outputs:
- `experiments/results/phase4/defense_stack_results.csv`
- `experiments/results/phase4/phase4_summary.json`
If you are documenting the result, add the Ubuntu terminal screenshot showing the phase 1 metrics output and mention that the run was performed in Ubuntu (WSL Ubuntu).

## Common Issues

**FileNotFoundError**: Ensure telemetry CSV path is correct in `config.yaml`

**ConnectionRefusedError** (socket): ns-3 simulation not running on specified host/port

**CSV parsing error**: Verify column order and delimiter (comma-separated, no spaces)

**Missing 'label' column**: Collector will auto-populate with 0 (benign) if missing

## References

- ns-3 Documentation: https://www.nsnam.org/
- 5G-LENA Extension: https://5g-lena.cttc.es/
- CSV Telemetry Schema: See `telemetry/collectors/ns3_collector.py`
