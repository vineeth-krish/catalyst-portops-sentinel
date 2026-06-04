# tests/test_run.py
import sys
from pathlib import Path

# Dynamically find the root project folder and add it to Python's path
root_path = Path(__file__).resolve().parent.parent
sys.path.append(str(root_path))

from core.auth import get_auth_token
from core.telemetry import get_network_devices, get_device_interfaces
from core.remediation import change_port_state

def main():
    print("--- Starting Catalyst PortOps Sentinel Core Test ---")
    
    # 1. Test Auth Token Extraction
    print("\n[Step 1] Attempting Authentication...")
    token = get_auth_token()
    if token:
        print(f"[SUCCESS] Token Acquired! (Truncated): {token[:15]}...")
    else:
        print("[FAIL] Could not authenticate. Check your .env file credentials.")
        return

    # 2. Test Fetching Devices
    print("\n[Step 2] Retrieving Managed Network Devices...")
    devices = get_network_devices()
    print(f"Found {len(devices)} device(s) in sandbox inventory.")
    
    if not devices:
        print("[INFO] No devices found or sandbox is blank. Ending test early.")
        return

    # Grab the first device to inspect its properties
    target_device = devices[0]
    device_name = target_device.get("hostname", "Unknown")
    device_ip = target_device.get("managementIpAddress")
    device_uuid = target_device.get("id")
    
    print(f"Targeting Device: {device_name} | IP: {device_ip} | UUID: {device_uuid}")

    # 3. Test Fetching Interfaces for that device
    print(f"\n[Step 3] Fetching Interfaces for {device_name}...")
    interfaces = get_device_interfaces(device_uuid)
    print(f"Retrieved {len(interfaces)} interface metrics.")

    # 4. Optional: Dry Run a port configuration change
    # Pick an interface name from your sandbox (e.g., "GigabitEthernet1/0/1")
    # change_port_state(device_ip, "GigabitEthernet1/0/1", state="shutdown")

if __name__ == "__main__":
    main()