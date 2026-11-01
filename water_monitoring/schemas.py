from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class WaterTelemetry(BaseModel):
    """Validated monitoring payload; values are illustrative, not plant limits."""
    model_config = ConfigDict(extra="forbid")

    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    plant_id: str = Field(default="demo-plant", min_length=1, max_length=64)
    inlet_flow_m3_h: float = Field(ge=0, le=5000)
    outlet_flow_m3_h: float = Field(ge=0, le=5000)
    tank_level_pct: float = Field(ge=0, le=100)
    inlet_pressure_bar: float = Field(ge=0, le=30)
    outlet_pressure_bar: float = Field(ge=0, le=30)
    ph: float = Field(ge=0, le=14)
    turbidity_ntu: float = Field(ge=0, le=5000)
    pump_running: bool
    pump_power_kw: float = Field(ge=0, le=10000)


class TelemetryOut(WaterTelemetry):
    id: int


class SummaryOut(BaseModel):
    records: int
    latest_timestamp: Optional[datetime] = None
    average_inlet_flow_m3_h: Optional[float] = None
    average_outlet_flow_m3_h: Optional[float] = None
    average_ph: Optional[float] = None
    average_turbidity_ntu: Optional[float] = None
    average_specific_energy_kwh_m3: Optional[float] = None
