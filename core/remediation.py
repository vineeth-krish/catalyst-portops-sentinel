# core/port_manager.py
import json
import time
import requests
import re
from datetime import datetime
from config.settings import settings
from core.auth import get_auth_token

def get_or_create_template(headers):
    """
    Ensures a Template Project and Template exist for port manipulation.
    Returns the committed Template ID.
    """
    # 1. Get/Create Project
    proj_url = f"{settings.DNAC_BASE_URL}/dna/intent/api/v1/template-programmer/project"
    projects = requests.get(proj_url, headers=headers, verify=False).json()
    proj_id = next((p["id"] for p in projects if p["name"] == "PortOps_Automation"), None)
    
    if not proj_id:
        requests.post(proj_url, headers=headers, json={"name": "PortOps_Automation"}, verify=False)
        time.sleep(2)  # Wait for creation
        projects = requests.get(proj_url, headers=headers, verify=False).json()
        proj_id = next((p["id"] for p in projects if p["name"] == "PortOps_Automation"), None)

    # 2. Get/Create Template
    temp_url = f"{settings.DNAC_BASE_URL}/dna/intent/api/v1/template-programmer/template"
    templates = requests.get(temp_url, headers=headers, verify=False).json()
    temp_id = next((t["templateId"] for t in templates if t.get("projectName") == "PortOps_Automation" and t.get("name") == "Port_State_Change"), None)
    
    if not temp_id:
        # Create Template
        create_url = f"{settings.DNAC_BASE_URL}/dna/intent/api/v1/template-programmer/project/{proj_id}/template"
        temp_payload = {
            "name": "Port_State_Change",
            "deviceTypes": [{"productFamily": "Switches and Hubs"}],
            "softwareType": "IOS-XE",
            "templateContent": "interface $interface_name\n $desired_state\n",
            "templateParams": [
                {"parameterName": "interface_name", "dataType": "STRING"},
                {"parameterName": "desired_state", "dataType": "STRING"}
            ]
        }
        resp = requests.post(create_url, headers=headers, json=temp_payload, verify=False)
        
        if resp.status_code == 202:
            task_id = resp.json().get("response", {}).get("taskId")
            task_url = f"{settings.DNAC_BASE_URL}/dna/intent/api/v1/task/{task_id}"
            for _ in range(10):
                time.sleep(2)
                task_resp = requests.get(task_url, headers=headers, verify=False).json()
                if task_resp.get("response", {}).get("endTime"):
                    # Extract template ID from data
                    temp_id = task_resp.get("response", {}).get("data")
                    break

        if temp_id:
            # Commit the template
            commit_url = f"{settings.DNAC_BASE_URL}/dna/intent/api/v1/template-programmer/template/version"
            requests.post(commit_url, headers=headers, json={"comments": "Initial commit", "templateId": temp_id}, verify=False)
            time.sleep(2)
            
    return temp_id

def change_port_state(device_uuid, device_ip, interface_name, state="shutdown"):
    """
    Executes a configuration change on a target interface using Catalyst Center Template Programmer API.
    """
    token = get_auth_token()
    if not token:
        return False, {"error": "Failed to get auth token"}

    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }

    try:
        # Ensure Template exists
        temp_id = get_or_create_template(headers)
        if not temp_id:
            # Fallback to the one we successfully tested in scratch.py if dynamic fetch fails
            temp_id = "24aadf39-86b0-4150-a6a9-c38c1c87d1a2"

        # Deploy Template
        deploy_url = f"{settings.DNAC_BASE_URL}/dna/intent/api/v1/template-programmer/template/deploy"
        deploy_payload = {
            "forcePushTemplate": True,
            "isComposite": False,
            "templateId": temp_id,
            "targetInfo": [
                {
                    "id": device_uuid,
                    "type": "MANAGED_DEVICE_UUID",
                    "params": {
                        "interface_name": interface_name,
                        "desired_state": "shutdown" if state == "shutdown" else "no shutdown"
                    }
                }
            ]
        }
        
        resp = requests.post(deploy_url, headers=headers, json=deploy_payload, verify=False, timeout=15)
        resp.raise_for_status()
        
        # Fire and forget for speed, dashboard will optimistically update.
        alert_package = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "severity": "CRITICAL" if state == "shutdown" else "INFO",
            "device_ip": device_ip,
            "target_interface": interface_name,
            "action_required": state.upper(),
            "status": "Template deployment initiated successfully via Catalyst Center"
        }
        print(f"[INFO] Successfully initiated template deploy for {interface_name}.")
        return True, alert_package

    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_json = e.response.json()
                error_msg = error_json.get("response", {}).get("message", error_msg)
            except ValueError:
                pass
        print(f"[ERROR] Failed to deploy template: {error_msg}")
        return False, {"error": error_msg}