# core/auth.py
import requests
import urllib3
from requests.auth import HTTPBasicAuth
from config.settings import settings

# Suppress self-signed SSL certificate warnings in lab environment
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_auth_token():
    """
    Authenticates with Catalyst Center and returns a valid JWT Token.
    """
    url = f"{settings.DNAC_BASE_URL}/dna/system/api/v1/auth/token"
    
    try:
        # Send a POST request with HTTP Basic Auth (Username/Password)
        response = requests.post(
            url, 
            auth=HTTPBasicAuth(settings.DNAC_USER, settings.DNAC_PASSWORD),
            verify=False, # Necessary for DevNet sandbox self-signed certs
            timeout=10
        )
        
        # Raise an exception for bad status codes (4xx, 5xx)
        response.raise_for_status()
        
        # Extract token from JSON response
        token = response.json().get("Token")
        return token

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to obtain authentication token: {e}")
        return None