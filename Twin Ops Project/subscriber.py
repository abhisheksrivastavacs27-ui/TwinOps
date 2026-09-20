"""Backward compatibility wrapper for app.mqtt.subscriber."""
from app.mqtt.subscriber import run_subscriber

if __name__ == "__main__":
    run_subscriber()