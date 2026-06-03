import requests
from config.settings import settings
from core.auth import get_auth_token

def deploy_test():
    token = get_auth_token()
    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }
    
    temp_id = "24aadf39-86b0-4150-a6a9-c38c1c87d1a2"
    
    dev_url = f"{settings.DNAC_BASE_URL}/dna/intent/api/v1/network-device"
    devices = requests.get(dev_url, headers=headers, verify=False).json().get("response", [])
    device_id = devices[0]["id"]
    
    deploy_url = f"{settings.DNAC_BASE_URL}/dna/intent/api/v1/template-programmer/template/deploy"
    deploy_payload = {
        "forcePushTemplate": True,
        "isComposite": False,
        "templateId": temp_id,
        "targetInfo": [
            {
                "id": device_id,
                "type": "MANAGED_DEVICE_UUID",
                "params": {
                    "interface_name": "GigabitEthernet0/0",
                    "desired_state": "DOWN"
                }
            }
        ]
    }
    resp = requests.post(deploy_url, headers=headers, json=deploy_payload, verify=False)
    print("Deploy status:", resp.status_code)
    print("Deploy resp:", resp.text)

deploy_test()
