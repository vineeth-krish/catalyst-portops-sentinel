# utils/discovery.py
import requests
import urllib3
from requests.auth import HTTPBasicAuth

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def discover_credentials(target_ip):
    # The standard credential pairs used in almost all Cisco DevNet Sandboxes
    credential_pairs = [
        ("admin", "Cisco1234!"),      # Matches the DNAC controller
        ("developer", "C1sco12345"),  # Standard DevNet edge switch
        ("admin", "C1sco12345"),      # Hybrid combo
        ("cisco", "cisco"),           # Legacy default
        ("cisco", "cisco123"),        # Legacy alternate
        ("admin", "admin")
    ]

    url = f"https://{target_ip}/restconf/data/ietf-interfaces:interfaces"
    headers = {
        "Accept": "application/yang-data+json"
    }

    print(f"\n[*] Starting RESTCONF Credential Discovery on {target_ip}...")

    for user, password in credential_pairs:
        print(f"[-] Attempting -> User: '{user}' | Pass: '{password}'")
        try:
            response = requests.get(
                url,
                auth=HTTPBasicAuth(user, password),
                headers=headers,
                verify=False,
                timeout=5
            )
            
            # HTTP 200 means we successfully authenticated and pulled data!
            if response.status_code == 200:
                print(f"\n[SUCCESS] 🎯 Master Credentials Found!")
                print("="*40)
                print(f"Update your .env file with:")
                print(f"SWITCH_USER={user}")
                print(f"SWITCH_PASSWORD={password}")
                print("="*40)
                return True
                
        except requests.exceptions.RequestException as e:
            # If the connection fails entirely, RESTCONF might be disabled
            pass 

    print("\n[FAILED] None of the standard DevNet credentials worked.")
    print("If this fails, RESTCONF might be administratively disabled on the sandbox switches.")
    return False

if __name__ == "__main__":
    # Testing against sw1
    discover_credentials("10.10.20.175")