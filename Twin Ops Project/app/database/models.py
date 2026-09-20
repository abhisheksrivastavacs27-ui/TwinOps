from dataclasses import dataclass
from typing import Optional


@dataclass
class TelemetryRecord:
    machine_id: str
    timestamp: str
    temperature: float
    vibration: float
    pressure: float
    id: Optional[int] = None


@dataclass
class AlertRecord:
    machine_id: str
    timestamp: str
    severity: str
    parameter: str
    message: str
    value: float
    status: str = "ACTIVE"
    id: Optional[int] = None


@dataclass
class MachineStatusRecord:
    machine_id: str
    last_seen: str
    status: str
    health_score: float
