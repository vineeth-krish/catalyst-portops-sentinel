import requests
import json
from config.settings import settings
from core.auth import get_auth_token

def test():
    token = get_auth_token()
    headers = {"X-Auth-Token": token, "Content-Type": "application/json"}
    
    proj_url = f"{settings.DNAC_BASE_URL}/dna/intent/api/v1/template-programmer/project"
    projects = requests.get(proj_url, headers=headers, verify=False).json()
    proj_id = next((p["id"] for p in projects if p["name"] == "PortOps_Automation"), None)
    
    temp_url = f"{settings.DNAC_BASE_URL}/dna/intent/api/v1/template-programmer/project/{proj_id}/template"
    temp_payload = {
        "name": "Port_State_Change_v2",
        "deviceTypes": [{"productFamily": "Switches and Hubs"}],
        "softwareType": "IOS-XE",
        "templateContent": "interface $interface_name\n $desired_state\n",
        "templateParams": [
            {"parameterName": "interface_name", "dataType": "STRING"},
            {"parameterName": "desired_state", "dataType": "STRING"}
        ]
    }
    resp = requests.post(temp_url, headers=headers, json=temp_payload, verify=False)
    print("Create status:", resp.status_code)
    print("Response text:", resp.text)

test()
