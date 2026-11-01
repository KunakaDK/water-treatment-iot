from .alarms import evaluate_alarms
from .energy import specific_energy_kwh_m3
from .storage import WaterStore


class WaterService:
    def __init__(self, store: WaterStore):
        self.store = store

    def ingest(self, reading: dict) -> dict:
        row_id = self.store.insert(reading)
        alarms = [a.__dict__ for a in evaluate_alarms(reading)]
        return {
            "id": row_id,
            "alarms": alarms,
            "specific_energy_kwh_m3": specific_energy_kwh_m3(
                float(reading["pump_power_kw"]), float(reading["outlet_flow_m3_h"])
            ),
        }
