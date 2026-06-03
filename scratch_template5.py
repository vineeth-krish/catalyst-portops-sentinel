import requests
import json
from config.settings import settings
from core.auth import get_auth_token

def test():
    token = get_auth_token()
    headers = {"X-Auth-Token": token, "Content-Type": "application/json"}
    
    # Let's check the task status of the template creation (from scratch3.py)
    task_id = "019e8d73-cefc-79ec-945d-1cbf76092918"
    task_url = f"{settings.DNAC_BASE_URL}/dna/intent/api/v1/task/{task_id}"
    task_resp = requests.get(task_url, headers=headers, verify=False).json()
    print("Task status:", json.dumps(task_resp, indent=2))

test()
