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
    
    temp_url = f"{settings.DNAC_BASE_URL}/dna/intent/api/v1/template-programmer/template"
    # Actually, the endpoint to get templates might be different or projectName is needed
    templates = requests.get(f"{temp_url}?projectId={proj_id}", headers=headers, verify=False).json()
    print("Templates:", json.dumps(templates, indent=2)[:500])

test()
