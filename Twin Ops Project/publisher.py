"""Backward compatibility wrapper for app.mqtt.publisher."""
from app.mqtt.publisher import run_publisher

if __name__ == "__main__":
    run_publisher()