from datetime import datetime, timedelta, timezone
import math
import random
from typing import Iterator


def generate_reading(index: int, *, seed: int = 42, start: datetime | None = None) -> dict:
    """Generate one synthetic process reading with occasional demonstration events."""
    rng = random.Random(seed + index)
    start = start or datetime.now(timezone.utc) - timedelta(minutes=5 * 100)
    timestamp = start + timedelta(minutes=5 * index)

    inlet = max(0.0, rng.gauss(42.0 + 2.0 * math.sin(index / 12), 1.8))
    outlet = max(0.0, inlet * rng.uniform(0.94, 1.01))
    level = min(100.0, max(0.0, rng.gauss(65.0 + 5.0 * math.sin(index / 20), 3.0)))
    p_in = max(0.1, rng.gauss(2.8, 0.18))
    p_out = max(0.1, rng.gauss(3.2, 0.2))
    ph = rng.gauss(7.2, 0.18)
    turbidity = max(0.1, rng.gauss(2.2, 0.45))
    pump_running = True
    power = max(0.0, rng.gauss(5.8, 0.35))

    # Clearly artificial events for demonstrating dashboard alarms.
    event = index % 48
    if 12 <= event <= 14:  # turbidity event
        turbidity += 5.5
    elif 26 <= event <= 27:  # pH excursion
        ph = rng.gauss(8.9, 0.08)
    elif event == 36:  # tank level high
        level = rng.uniform(92, 97)
    elif event == 42:  # lower flow with unchanged power
        inlet *= 0.55
        outlet *= 0.52

    return {
        "timestamp": timestamp,
        "plant_id": "demo-plant",
        "inlet_flow_m3_h": round(inlet, 3),
        "outlet_flow_m3_h": round(outlet, 3),
        "tank_level_pct": round(level, 2),
        "inlet_pressure_bar": round(p_in, 3),
        "outlet_pressure_bar": round(p_out, 3),
        "ph": round(ph, 3),
        "turbidity_ntu": round(turbidity, 3),
        "pump_running": pump_running,
        "pump_power_kw": round(power, 3),
    }


def generate_readings(count: int = 200, *, seed: int = 42) -> Iterator[dict]:
    if count < 1:
        raise ValueError("count must be at least 1")
    start = datetime.now(timezone.utc) - timedelta(minutes=5 * count)
    for i in range(count):
        yield generate_reading(i, seed=seed, start=start)
