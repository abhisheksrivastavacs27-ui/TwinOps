import random
from datetime import datetime


def generate_sensor_data():

    sensor_data = {

        "machine_id": "PUMP_001",

        "timestamp": datetime.now().isoformat(),

        "temperature": round(
            random.uniform(40, 90), 2
        ),

        "vibration": round(
            random.uniform(1, 10), 2
        ),

        "pressure": round(
            random.uniform(8, 20), 2
        )
    }

    return sensor_data