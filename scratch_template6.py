import requests
import json
import time
from config.settings import settings
from core.auth import get_auth_token

def test():
    token = get_auth_token()
    headers = {"X-Auth-Token": token, "Content-Type": "application/json"}
    
    # 1. Commit template
    temp_id = "24aadf39-86b0-4150-a6a9-c38c1c87d1a2"
    commit_url = f"{settings.DNAC_BASE_URL}/dna/intent/api/v1/template-programmer/template/version"
    commit_payload = {
        "comments": "Initial commit",
        "templateId": temp_id
    }
    resp = requests.post(commit_url, headers=headers, json=commit_payload, verify=False)
    print("Commit status:", resp.status_code)
    print("Commit resp:", resp.text)
    
    # 2. Get device
    dev_url = f"{settings.DNAC_BASE_URL}/dna/intent/api/v1/network-device"
    devices = requests.get(dev_url, headers=headers, verify=False).json().get("response", [])
    device_id = devices[0]["id"]
    
    # 3. Deploy Template
    deploy_url = f"{settings.DNAC_BASE_URL}/dna/intent/api/v1/template-programmer/template/deploy"
    deploy_payload = {
        "forcePushTemplate": True,
        "isComposite": False,
        "mainTemplateId": temp_id,
        "memberTemplateDeploymentInfo": [],
        "targetInfo": [
            {
                "id": device_id,
                "type": "MANAGED_DEVICE_UUID",
                "params": {
                    "interface_name": "GigabitEthernet0/0",
                    "desired_state": "DOWN"  # let's be careful, but it's a test
                }
            }
        ]
    }
    resp = requests.post(deploy_url, headers=headers, json=deploy_payload, verify=False)
    print("Deploy status:", resp.status_code)
    print("Deploy resp:", resp.text)
    
    if resp.status_code == 202:
        task_id = resp.json().get("response", {}).get("taskId")
        # Poll
        task_url = f"{settings.DNAC_BASE_URL}/dna/intent/api/v1/task/{task_id}"
        for _ in range(15):
            time.sleep(2)
            task_resp = requests.get(task_url, headers=headers, verify=False).json()
            if task_resp.get("response", {}).get("endTime"):
                print("Task End:", task_resp.get("response", {}).get("progress"))
                break

test()
