"""Backward compatibility wrapper for dashboard/dashboard.py."""
import sys
import os
import runpy

root_dir = os.path.dirname(os.path.abspath(__file__))
dashboard_dir = os.path.join(root_dir, "dashboard")

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if dashboard_dir not in sys.path:
    sys.path.insert(0, dashboard_dir)

# Remove single file 'dashboard' from sys.modules so directory imports work
if "dashboard" in sys.modules and not hasattr(sys.modules["dashboard"], "__path__"):
    del sys.modules["dashboard"]

target_file = os.path.join(dashboard_dir, "dashboard.py")
runpy.run_path(target_file, run_name="__main__")