def specific_energy_kwh_m3(power_kw: float, flow_m3_h: float) -> float | None:
    """Return instantaneous specific energy (kW / m3/h = kWh/m3).

    This is an indicative monitoring calculation, not an audited energy KPI.
    """
    if power_kw < 0 or flow_m3_h < 0:
        raise ValueError("Power and flow must be non-negative")
    if flow_m3_h == 0:
        return None
    return power_kw / flow_m3_h
