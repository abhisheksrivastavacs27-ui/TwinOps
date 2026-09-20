import pytest
from app.simulator.sensor_simulator import PumpSimulator, generate_sensor_data


def test_pump_simulator_normal_mode():
    sim = PumpSimulator(mode="NORMAL")
    data = sim.generate_sensor_data()

    assert data["machine_id"] == "PUMP_001"
    assert "timestamp" in data
    assert isinstance(data["temperature"], float)
    assert isinstance(data["vibration"], float)
    assert isinstance(data["pressure"], float)


def test_pump_simulator_modes():
    for mode in ["NORMAL", "WARNING", "FAILURE", "RANDOM"]:
        sim = PumpSimulator(mode=mode)
        data = sim.generate_sensor_data()
        assert "temperature" in data
        assert "vibration" in data
        assert "pressure" in data


def test_standalone_generate_sensor_data():
    data = generate_sensor_data("WARNING")
    assert data["machine_id"] == "PUMP_001"
