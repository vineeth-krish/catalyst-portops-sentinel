import requests
import json
from config.settings import settings
from core.auth import get_auth_token

def test():
    token = get_auth_token()
    headers = {"X-Auth-Token": token, "Content-Type": "application/json"}
    
    temp_url = f"{settings.DNAC_BASE_URL}/dna/intent/api/v1/template-programmer/template"
    templates = requests.get(temp_url, headers=headers, verify=False).json()
    print("Total templates:", len(templates))
    
    portops_templates = [t for t in templates if t.get("projectName") == "PortOps_Automation"]
    print("PortOps templates:", len(portops_templates))
    for t in portops_templates:
        print(f"Name: {t['name']}, ID: {t['templateId']}, Version: {t.get('version')}")

test()
