import json
import os
import random
from datetime import datetime
from typing import Dict, Any
from app.config import MACHINE_ID, SIMULATION_MODE_FILE


class PumpSimulator:
    """Simulates physical telemetry for an industrial water pump with realistic operating modes."""

    def __init__(self, machine_id: str = MACHINE_ID, mode: str = "NORMAL"):
        self.machine_id = machine_id
        self.mode = mode.upper()
        # Stateful baseline values for smooth physical transitions
        self._curr_temp = 55.0
        self._curr_vib = 2.5
        self._curr_press = 14.0

    def set_mode(self, mode: str):
        valid_modes = ["NORMAL", "WARNING", "FAILURE", "RANDOM"]
        mode_upper = mode.upper()
        if mode_upper in valid_modes:
            self.mode = mode_upper

    def _read_external_mode(self):
        """Reads mode override from SIMULATION_MODE_FILE if available."""
        if os.path.exists(SIMULATION_MODE_FILE):
            try:
                with open(SIMULATION_MODE_FILE, "r") as f:
                    data = json.load(f)
                    mode = data.get("mode")
                    if mode:
                        self.set_mode(mode)
            except Exception:
                pass

    def generate_sensor_data(self) -> Dict[str, Any]:
        """Generates realistic pump telemetry payload based on current simulation mode."""
        self._read_external_mode()

        if self.mode == "NORMAL":
            target_temp = random.uniform(48.0, 72.0)
            target_vib = random.uniform(1.5, 4.5)
            target_press = random.uniform(11.0, 17.0)
        elif self.mode == "WARNING":
            target_temp = random.uniform(76.0, 84.0)
            target_vib = random.uniform(5.1, 6.9)
            target_press = random.uniform(8.1, 9.9)
        elif self.mode == "FAILURE":
            target_temp = random.uniform(86.0, 96.0)
            target_vib = random.uniform(7.2, 10.5)
            target_press = random.uniform(4.5, 7.8)
        else:  # RANDOM
            target_temp = random.uniform(40.0, 95.0)
            target_vib = random.uniform(1.0, 10.0)
            target_press = random.uniform(5.0, 20.0)

        # Smooth drift towards target value (simulating thermal & physical inertia)
        self._curr_temp += (target_temp - self._curr_temp) * 0.3 + random.uniform(-0.5, 0.5)
        self._curr_vib += (target_vib - self._curr_vib) * 0.3 + random.uniform(-0.1, 0.1)
        self._curr_press += (target_press - self._curr_press) * 0.3 + random.uniform(-0.2, 0.2)

        return {
            "machine_id": self.machine_id,
            "timestamp": datetime.now().isoformat(),
            "temperature": round(float(self._curr_temp), 2),
            "vibration": round(float(self._curr_vib), 2),
            "pressure": round(float(self._curr_press), 2)
        }


# Standalone function for backward compatibility
_default_simulator = PumpSimulator()


def generate_sensor_data(mode: str = "NORMAL") -> Dict[str, Any]:
    if mode != "NORMAL":
        _default_simulator.set_mode(mode)
    return _default_simulator.generate_sensor_data()
