# core/escalation.py
import requests
from config.settings import settings

def escalate_incident(alert_package):
    """
    Escalates a port shutdown incident to external ITSM / ChatOps (e.g. Webex webhook).
    """
    target_interface = alert_package.get("target_interface")
    device_ip = alert_package.get("device_ip")
    print(f"[INFO] Escalating incident for interface {target_interface} on device {device_ip}")
    
    # Check if Webex Webhook URL is configured
    webhook_url = settings.WEBEX_WEBHOOK_URL
    if not webhook_url:
        print("[INFO] Webex webhook URL not configured. Skipping external ChatOps notification.")
        return False
        
    # Format the markdown message for Webex
    message = (
        f"🚨 **Catalyst PortOps Sentinel - Zero-Trust Remediation Alert** 🚨\n\n"
        f"- **Timestamp:** {alert_package.get('timestamp')}\n"
        f"- **Severity:** {alert_package.get('severity')}\n"
        f"- **Device IP:** {device_ip}\n"
        f"- **Interface:** {target_interface}\n"
        f"- **Action Executed:** {alert_package.get('action_required')}\n"
        f"- **Status:** {alert_package.get('status')}"
    )
    
    try:
        response = requests.post(webhook_url, json={"text": message}, timeout=10)
        response.raise_for_status()
        print("[SUCCESS] Incident escalation notification sent to Webex Teams.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to send Webex escalation alert: {e}")
        return False
