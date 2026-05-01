from __future__ import annotations

import socket
import time
from pathlib import Path

import pandas as pd

from telemetry.collectors.base_collector import BaseCollector


class NS3Collector(BaseCollector):
    """
    Ingest telemetry from ns-3 simulation output files (CSV format).
    
    Expected CSV columns: timestamp, ue_id, rsrp, latency, throughput, label
    (Other metrics like jitter, packet_loss can also be included)
    
    Example row:
        0.1,1,-80.5,25.3,45.2,0
    """

    def __init__(self, log_file: str):
        self.log_file = Path(log_file)
        if not self.log_file.exists():
            raise FileNotFoundError(f"ns-3 log file not found: {self.log_file}")

    def collect(self, rows: int | None = None) -> pd.DataFrame:
        """
        Parse ns-3 CSV log into DataFrame.
        If rows is specified, return first rows; else return all.
        """
        df = pd.read_csv(self.log_file)
        
        # Normalize column names to lowercase with underscores
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        # Ensure 'label' column exists; if not, assume benign (0)
        if 'label' not in df.columns:
            df['label'] = 0
        
        if rows is not None:
            df = df.iloc[:rows].reset_index(drop=True)
        
        return df


class NS3SocketCollector(BaseCollector):
    """
    Reads live telemetry from ns-3 simulation via TCP socket.
    Expects ns-3 to output CSV lines (newline-delimited) over socket.
    """

    def __init__(self, host: str = 'localhost', port: int = 5555, timeout: int = 30):
        self.host = host
        self.port = port
        self.timeout = timeout

    def collect(self, rows: int = 100) -> pd.DataFrame:
        """
        Connect to ns-3 socket and collect specified number of telemetry samples.
        Each line from socket should be comma-separated: timestamp,ue_id,rsrp,...
        """
        samples = []
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((self.host, self.port))
            
            while len(samples) < rows:
                try:
                    data = sock.recv(4096).decode('utf-8')
                    if not data:
                        break
                    for line in data.strip().split('\n'):
                        if line:
                            samples.append(self._parse_line(line))
                            if len(samples) >= rows:
                                break
                except socket.timeout:
                    break
            
            sock.close()
        except ConnectionRefusedError:
            raise RuntimeError(
                f"Could not connect to ns-3 telemetry socket at {self.host}:{self.port}. "
                "Ensure ns-3 simulation is running."
            )
        
        if not samples:
            raise RuntimeError("No telemetry samples received from ns-3 socket.")
        
        df = pd.DataFrame(samples)
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        return df

    @staticmethod
    def _parse_line(line: str) -> dict:
        """Parse comma-separated telemetry line into dict."""
        fields = line.split(',')
        # Expected: timestamp, ue_id, rsrp, latency, throughput, label
        return {
            'timestamp': float(fields[0]) if len(fields) > 0 else 0.0,
            'ue_id': int(fields[1]) if len(fields) > 1 else 0,
            'rsrp': float(fields[2]) if len(fields) > 2 else 0.0,
            'latency': float(fields[3]) if len(fields) > 3 else 0.0,
            'throughput': float(fields[4]) if len(fields) > 4 else 0.0,
            'label': int(fields[5]) if len(fields) > 5 else 0,
        }