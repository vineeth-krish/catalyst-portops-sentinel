# core/inventory.py
import requests
from core.auth import get_auth_token
from config.settings import settings

def get_network_devices():
    """
    Fetches all network devices managed by Catalyst Center.
    """
    token = get_auth_token()
    if not token:
        return []

    url = f"{settings.DNAC_BASE_URL}/dna/intent/api/v1/network-device"
    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, verify=False, timeout=15)
        response.raise_for_status()
        
        # The API returns a dictionary with a 'response' key containing the list
        return response.json().get("response", [])
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch device inventory: {e}")
        return []

def get_device_interfaces(device_uuid):
    """
    Fetches all interfaces for a specific device using its UUID.
    """
    token = get_auth_token()
    if not token:
        return []

    url = f"{settings.DNAC_BASE_URL}/dna/intent/api/v1/interface"
    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }
    # Pass the device UUID as a query parameter to filter interfaces
    params = {"deviceId": device_uuid}

    try:
        response = requests.get(url, headers=headers, params=params, verify=False, timeout=15)
        response.raise_for_status()
        return response.json().get("response", [])
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch interfaces for device {device_uuid}: {e}")
        return []