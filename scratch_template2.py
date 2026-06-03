import requests
import json
import time
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
        "name": "Port_State_Change",
        "description": "Changes the state of a port",
        "deviceTypes": [{"productFamily": "Switches and Hubs"}],
        "softwareType": "IOS-XE",
        "templateContent": "interface $interface_name\n $desired_state\n",
        "templateParams": [
            {"parameterName": "interface_name", "dataType": "STRING"},
            {"parameterName": "desired_state", "dataType": "STRING"}
        ]
    }
    resp = requests.post(temp_url, headers=headers, json=temp_payload, verify=False)
    task_id = resp.json().get("response", {}).get("taskId")
    print(f"Task ID: {task_id}")
    
    task_url = f"{settings.DNAC_BASE_URL}/dna/intent/api/v1/task/{task_id}"
    while True:
        time.sleep(2)
        task_resp = requests.get(task_url, headers=headers, verify=False).json()
        if task_resp.get("response", {}).get("endTime"):
            print("Task completed:", task_resp.get("response", {}).get("progress"))
            break
            
    templates = requests.get(f"{settings.DNAC_BASE_URL}/dna/intent/api/v1/template-programmer/template?projectId={proj_id}", headers=headers, verify=False).json()
    print("Templates count:", len(templates))
    if templates:
        print("Template ID:", templates[0].get("templateId"))

test()
