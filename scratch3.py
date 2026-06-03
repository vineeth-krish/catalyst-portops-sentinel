import requests
import json
from config.settings import settings
from core.auth import get_auth_token

def test_interface_put():
    token = get_auth_token()
    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }
    
    dev_url = f"{settings.DNAC_BASE_URL}/dna/intent/api/v1/network-device"
    devices = requests.get(dev_url, headers=headers, verify=False).json().get("response", [])
    device_id = devices[0]["id"]
    
    int_url = f"{settings.DNAC_BASE_URL}/dna/intent/api/v1/interface"
    interfaces = requests.get(int_url, headers=headers, params={"deviceId": device_id}, verify=False).json().get("response", [])
    
    target_int = None
    for i in interfaces:
        if i["portName"] == "GigabitEthernet1/0/1":
            target_int = i
            break
            
    int_id = target_int["id"]
    put_url = f"{settings.DNAC_BASE_URL}/dna/intent/api/v1/interface/{int_id}"
    payload = {
        "adminStatus": "DOWN"
    }
    
    try:
        resp = requests.put(put_url, headers=headers, json=payload, verify=False)
        resp.raise_for_status()
        print("Success:", resp.status_code)
    except requests.exceptions.RequestException as e:
        print("Exception caught!")
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            print("Response text:", e.response.text)
            error_json = e.response.json()
            error_msg = error_json.get("response", {}).get("detail", error_msg)
            print("Extracted error_msg:", error_msg)

test_interface_put()
