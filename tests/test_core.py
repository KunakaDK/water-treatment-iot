from datetime import datetime, timezone
import pytest
from water_monitoring.energy import specific_energy_kwh_m3
from water_monitoring.alarms import evaluate_alarms
from water_monitoring.simulator import generate_reading, generate_readings
from water_monitoring.storage import WaterStore
from water_monitoring.service import WaterService


def test_specific_energy():
    assert specific_energy_kwh_m3(6.0, 30.0) == pytest.approx(0.2)
    assert specific_energy_kwh_m3(6.0, 0.0) is None
    with pytest.raises(ValueError):
        specific_energy_kwh_m3(-1, 2)


def test_simulator_is_reproducible_and_valid():
    fixed_start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    a = generate_reading(1, seed=7, start=fixed_start)
    b = generate_reading(1, seed=7, start=fixed_start)
    assert a == b
    assert 0 <= a["ph"] <= 14
    assert 0 <= a["tank_level_pct"] <= 100


def test_simulator_rejects_zero_count():
    with pytest.raises(ValueError):
        list(generate_readings(0))


def test_alarms_detect_high_turbidity():
    reading = generate_reading(0)
    reading["turbidity_ntu"] = 12
    assert "TURBIDITY_HIGH" in [a.code for a in evaluate_alarms(reading)]


def test_store_and_service(tmp_path):
    store = WaterStore(tmp_path / "water.db")
    service = WaterService(store)
    reading = generate_reading(2)
    result = service.ingest(reading)
    rows = store.list(10)
    assert result["id"] == 1
    assert len(rows) == 1
    assert rows[0]["plant_id"] == "demo-plant"
    assert store.summary()["records"] == 1


def test_api_end_to_end(tmp_path):
    from fastapi.testclient import TestClient
    from water_monitoring.api import create_app

    client = TestClient(create_app(str(tmp_path / "api.db")))
    assert client.get("/health").json()["mode"] == "simulation-only"
    payload = {
        "plant_id": "api-test", "inlet_flow_m3_h": 40, "outlet_flow_m3_h": 39,
        "tank_level_pct": 62, "inlet_pressure_bar": 2.7, "outlet_pressure_bar": 3.1,
        "ph": 7.2, "turbidity_ntu": 2.0, "pump_running": True, "pump_power_kw": 5.5,
    }
    response = client.post("/telemetry", json=payload)
    assert response.status_code == 200
    assert response.json()["specific_energy_kwh_m3"] == pytest.approx(5.5 / 39)
    assert client.get("/telemetry").json()[0]["plant_id"] == "api-test"
    assert client.get("/summary").json()["records"] == 1
    assert client.get("/alarms/latest").status_code == 200
