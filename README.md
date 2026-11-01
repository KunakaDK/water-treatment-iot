# Water Treatment Plant – IoT Process Monitoring & Supervision

**Portfolio project | Simulation-based | Monitoring-only**

A complete, locally runnable demonstration of an IoT monitoring stack for a *simulated* water-treatment process. It generates synthetic sensor telemetry, validates and stores readings, calculates an indicative specific-energy KPI, evaluates configurable demonstration alarms, exposes a FastAPI, and visualises process trends in Streamlit.

> **Important limitation:** this repository uses synthetic data and illustrative thresholds. It is not connected to a real plant, does not implement control of pumps/valves/chemical dosing, and is not validated for operational or regulatory use. Do not use the example alarm thresholds as engineering setpoints.

## Features

- Synthetic flow, pressure, tank-level, pH, turbidity, pump status and power telemetry.
- Input validation using Pydantic.
- SQLite persistence with timestamp indexing.
- FastAPI endpoints for ingestion, history, summary and latest alarms.
- Demo alarm rules for pH, turbidity, tank level, pressure, flow mismatch and pump status.
- Indicative specific energy: `pump_power_kw / outlet_flow_m3_h`, numerically in kWh/m³.
- Streamlit dashboard with trends, KPIs, alarms and recent records.
- Optional MQTT publisher and MQTT-to-SQLite worker.
- Automated unit tests.

## Architecture

```text
Synthetic process simulator
          | (JSON telemetry)
          +--------------------------+
          |                          |
      HTTP POST                  MQTT (optional)
          |                          |
      FastAPI                  MQTT worker
          |                          |
          +-----------+--------------+
                      |
                   SQLite
                      |
             FastAPI read endpoints
                      |
              Streamlit dashboard
```

## Requirements

- Python 3.10 or newer.
- Dependencies listed in `requirements.txt`.
- MQTT is optional; a local Mosquitto broker is needed only for the MQTT demonstration.

## Run locally

From this directory:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Seed 200 synthetic readings:

```bash
python -m water_monitoring.cli seed --count 200 --clear
```

Start the API in terminal 1:

```bash
uvicorn water_monitoring.api:app --reload
```

Open API documentation at `http://127.0.0.1:8000/docs`.

Start the dashboard in terminal 2:

```bash
streamlit run water_monitoring/dashboard.py
```

The dashboard defaults to `http://127.0.0.1:8000`. Set `WATER_API_URL` to change it. Set `WATER_DB_PATH` to change the SQLite location.

## Optional MQTT demonstration

Start a local Mosquitto broker, then run the subscriber in one terminal:

```bash
python -m water_monitoring.mqtt_worker
```

In another terminal, publish 100 synthetic readings:

```bash
python -m water_monitoring.mqtt_publisher
```

Configuration variables: `WATER_MQTT_HOST`, `WATER_MQTT_PORT`, `WATER_MQTT_TOPIC`.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Health and simulation-mode check |
| POST | `/telemetry` | Validate and store one reading |
| GET | `/telemetry?limit=200` | Retrieve recent readings |
| GET | `/summary` | Summary KPIs |
| GET | `/alarms/latest` | Alarms for latest stored reading |

Example POST payload:

```json
{
  "timestamp": "2026-01-01T12:00:00Z",
  "plant_id": "demo-plant",
  "inlet_flow_m3_h": 42.0,
  "outlet_flow_m3_h": 40.5,
  "tank_level_pct": 65.0,
  "inlet_pressure_bar": 2.8,
  "outlet_pressure_bar": 3.2,
  "ph": 7.2,
  "turbidity_ntu": 2.1,
  "pump_running": true,
  "pump_power_kw": 5.8
}
```

## Tests

```bash
pytest -q
```

## Engineering notes

- All synthetic process ranges and alarm thresholds are illustrative, not normative.
- The energy KPI is an instantaneous ratio and should not be presented as an audited plant efficiency metric.
- The dashboard is read-only. There are no actuator commands or control loops.
- A real deployment would require process-engineering review, calibrated instruments, cybersecurity review, OT network segmentation, safety analysis and site approval.

A small synthetic SQLite demo database is included in the downloadable archive so the dashboard can show sample trends immediately. To regenerate it, run the seed command above. The database is ignored by Git by default; seed it after cloning.
