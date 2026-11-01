from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Alarm:
    code: str
    severity: str
    message: str
    value: float | None = None


# Demo thresholds only. They are not regulatory limits or plant setpoints.
DEFAULT_THRESHOLDS = {
    "ph_low": 6.5,
    "ph_high": 8.5,
    "turbidity_high_ntu": 5.0,
    "tank_level_high_pct": 90.0,
    "tank_level_low_pct": 15.0,
    "pressure_high_bar": 6.0,
    "flow_mismatch_pct": 25.0,
}


def evaluate_alarms(reading: dict[str, Any], thresholds: dict[str, float] | None = None) -> list[Alarm]:
    t = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
    alarms: list[Alarm] = []
    ph = float(reading["ph"])
    turbidity = float(reading["turbidity_ntu"])
    level = float(reading["tank_level_pct"])
    pressure = max(float(reading["inlet_pressure_bar"]), float(reading["outlet_pressure_bar"]))
    inlet = float(reading["inlet_flow_m3_h"])
    outlet = float(reading["outlet_flow_m3_h"])

    if ph < t["ph_low"]:
        alarms.append(Alarm("PH_LOW", "warning", "pH is below the illustrative demo band.", ph))
    elif ph > t["ph_high"]:
        alarms.append(Alarm("PH_HIGH", "warning", "pH is above the illustrative demo band.", ph))
    if turbidity > t["turbidity_high_ntu"]:
        alarms.append(Alarm("TURBIDITY_HIGH", "warning", "Turbidity exceeds the illustrative demo threshold.", turbidity))
    if level > t["tank_level_high_pct"]:
        alarms.append(Alarm("TANK_LEVEL_HIGH", "warning", "Tank level is high in the simulated scenario.", level))
    if level < t["tank_level_low_pct"]:
        alarms.append(Alarm("TANK_LEVEL_LOW", "warning", "Tank level is low in the simulated scenario.", level))
    if pressure > t["pressure_high_bar"]:
        alarms.append(Alarm("PRESSURE_HIGH", "warning", "Pressure exceeds the illustrative demo threshold.", pressure))
    if inlet > 0:
        mismatch = abs(inlet - outlet) / inlet * 100
        if mismatch > t["flow_mismatch_pct"]:
            alarms.append(Alarm("FLOW_MISMATCH", "info", "Inlet and outlet flow differ beyond the demo tolerance.", mismatch))
    if not bool(reading["pump_running"]) and float(reading["pump_power_kw"]) > 0.2:
        alarms.append(Alarm("PUMP_STATUS_POWER_MISMATCH", "warning", "Pump status is stopped while simulated power remains non-zero.", float(reading["pump_power_kw"])))
    return alarms
