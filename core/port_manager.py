# core/port_manager.py
import json
from datetime import datetime

def change_port_state(device_ip, interface_name, state="shutdown"):
    """
    Generates a remediation payload and simulates an ITSM / Webhook escalation
    due to lab RBAC (Role-Based Access Control) restrictions.
    """
    # 1. Generate the exact CLI payload required to fix the issue
    cli_payload = [
        "configure terminal",
        f"interface {interface_name}",
        state,
        "end",
        "write memory"
    ]

    # 2. Package it into a structured JSON alert
    alert_package = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "severity": "CRITICAL" if state == "shutdown" else "INFO",
        "device_ip": device_ip,
        "target_interface": interface_name,
        "action_required": state.upper(),
        "remediation_cli": cli_payload,
        "status": "Escalated to NOC via Webhook - Awaiting Approval"
    }
    
    print(f"[INFO] RBAC lock detected. Escalating incident for {interface_name} to NOC.")
    return True, alert_package