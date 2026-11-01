import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

COLUMNS = [
    "timestamp", "plant_id", "inlet_flow_m3_h", "outlet_flow_m3_h", "tank_level_pct",
    "inlet_pressure_bar", "outlet_pressure_bar", "ph", "turbidity_ntu", "pump_running", "pump_power_kw"
]


class WaterStore:
    def __init__(self, db_path: str | Path = "./data/water_plant.db"):
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize(self):
        with self.connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS telemetry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    plant_id TEXT NOT NULL,
                    inlet_flow_m3_h REAL NOT NULL,
                    outlet_flow_m3_h REAL NOT NULL,
                    tank_level_pct REAL NOT NULL,
                    inlet_pressure_bar REAL NOT NULL,
                    outlet_pressure_bar REAL NOT NULL,
                    ph REAL NOT NULL,
                    turbidity_ntu REAL NOT NULL,
                    pump_running INTEGER NOT NULL,
                    pump_power_kw REAL NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_timestamp ON telemetry(timestamp)")

    def insert(self, reading: dict[str, Any]) -> int:
        payload = dict(reading)
        ts = payload["timestamp"]
        if isinstance(ts, datetime):
            payload["timestamp"] = ts.isoformat()
        elif not isinstance(ts, str):
            raise ValueError("timestamp must be datetime or ISO string")
        payload["pump_running"] = int(bool(payload["pump_running"]))
        values = [payload[c] for c in COLUMNS]
        placeholders = ",".join("?" for _ in COLUMNS)
        with self.connect() as conn:
            cur = conn.execute(f"INSERT INTO telemetry ({','.join(COLUMNS)}) VALUES ({placeholders})", values)
            return int(cur.lastrowid)

    def list(self, limit: int = 200) -> list[dict[str, Any]]:
        limit = max(1, min(int(limit), 5000))
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM telemetry ORDER BY timestamp DESC, id DESC LIMIT ?", (limit,)).fetchall()
        result = [dict(row) for row in rows]
        for row in result:
            row["pump_running"] = bool(row["pump_running"])
        return result

    def summary(self) -> dict[str, Any]:
        with self.connect() as conn:
            row = conn.execute("""
                SELECT COUNT(*) AS records, MAX(timestamp) AS latest_timestamp,
                       AVG(inlet_flow_m3_h) AS avg_inlet, AVG(outlet_flow_m3_h) AS avg_outlet,
                       AVG(ph) AS avg_ph, AVG(turbidity_ntu) AS avg_turbidity
                FROM telemetry
            """).fetchone()
        result = dict(row)
        records = result["records"]
        result["average_specific_energy_kwh_m3"] = None
        if records:
            readings = self.list(limit=min(records, 5000))
            ratios = [r["pump_power_kw"] / r["outlet_flow_m3_h"] for r in readings if r["outlet_flow_m3_h"] > 0]
            result["average_specific_energy_kwh_m3"] = sum(ratios) / len(ratios) if ratios else None
        return result

    def clear(self):
        with self.connect() as conn:
            conn.execute("DELETE FROM telemetry")
