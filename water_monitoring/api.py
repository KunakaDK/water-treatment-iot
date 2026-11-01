import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from .schemas import WaterTelemetry, TelemetryOut, SummaryOut
from .storage import WaterStore
from .service import WaterService
from .alarms import evaluate_alarms
from .energy import specific_energy_kwh_m3


def create_app(db_path: str | None = None) -> FastAPI:
    store = WaterStore(db_path or os.getenv("WATER_DB_PATH", "./data/water_plant.db"))
    service = WaterService(store)
    app = FastAPI(title="Water Treatment IoT Monitoring API", version="1.0.0",
                  description="Simulation-based monitoring API. Not for operational plant control.")
    app.state.store = store
    app.state.service = service

    @app.get("/health")
    def health():
        return {"status": "ok", "mode": "simulation-only"}

    @app.post("/telemetry")
    def ingest(reading: WaterTelemetry):
        return service.ingest(reading.model_dump())

    @app.get("/telemetry", response_model=list[TelemetryOut])
    def list_telemetry(limit: int = Query(default=200, ge=1, le=5000)):
        return store.list(limit)

    @app.get("/summary", response_model=SummaryOut)
    def summary():
        s = store.summary()
        return {
            "records": s["records"],
            "latest_timestamp": s["latest_timestamp"],
            "average_inlet_flow_m3_h": s["avg_inlet"],
            "average_outlet_flow_m3_h": s["avg_outlet"],
            "average_ph": s["avg_ph"],
            "average_turbidity_ntu": s["avg_turbidity"],
            "average_specific_energy_kwh_m3": s["average_specific_energy_kwh_m3"],
        }

    @app.get("/alarms/latest")
    def latest_alarms():
        readings = store.list(1)
        if not readings:
            return {"timestamp": None, "alarms": []}
        latest = readings[0]
        alarms = [a.__dict__ for a in evaluate_alarms(latest)]
        energy = specific_energy_kwh_m3(latest["pump_power_kw"], latest["outlet_flow_m3_h"])
        return {"timestamp": latest["timestamp"], "alarms": alarms, "specific_energy_kwh_m3": energy}

    return app


app = create_app()
