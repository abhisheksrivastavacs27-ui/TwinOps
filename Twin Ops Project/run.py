import argparse
import os
import sys
import subprocess

def main():
    parser = argparse.ArgumentParser(description="Twin Ops — Main Command Launcher")
    parser.add_argument("--publisher", action="store_true", help="Run MQTT Publisher")
    parser.add_argument("--subscriber", action="store_true", help="Run MQTT Subscriber")
    parser.add_argument("--dashboard", action="store_true", help="Launch Streamlit Dashboard")
    parser.add_argument("--view-db", action="store_true", help="Inspect Database state")
    parser.add_argument("--test", action="store_true", help="Run Pytest Test Suite")

    args = parser.parse_args()

    python_bin = sys.executable

    if args.publisher:
        print("Starting MQTT Telemetry Publisher...")
        subprocess.run([python_bin, "-m", "app.mqtt.publisher"])
    elif args.subscriber:
        print("Starting MQTT Ingestion Subscriber...")
        subprocess.run([python_bin, "-m", "app.mqtt.subscriber"])
    elif args.dashboard:
        print("Launching Streamlit Industrial Dashboard...")
        subprocess.run(["streamlit", "run", "dashboard/dashboard.py"])
    elif args.view_db:
        subprocess.run([python_bin, "scripts/view_database.py"])
    elif args.test:
        subprocess.run([python_bin, "-m", "pytest", "tests/"])
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
