# dashboard/app.py
import sys
from pathlib import Path

# 1. Dynamically find the root project folder and add it to Python's path
root_path = Path(__file__).resolve().parent.parent
sys.path.append(str(root_path))

import streamlit as st
import pandas as pd
from core.inventory import get_network_devices, get_device_interfaces
from core.port_manager import change_port_state

# --- UI Configuration ---
st.set_page_config(page_title="PortOps Sentinel", page_icon="🛡️", layout="wide")

st.title("🛡️ Catalyst PortOps Sentinel")
st.markdown("Enterprise automated port management and zero-trust isolation platform.")

# --- STATE MANAGEMENT (The Fix) ---
# We now store both the isolated ports AND the incident ticket in memory
if "isolated_ports" not in st.session_state:
    st.session_state.isolated_ports = []
if "incident_ticket" not in st.session_state:
    st.session_state.incident_ticket = None

# --- Sidebar: Device Selection ---
st.sidebar.header("Network Topology")

with st.spinner("Fetching Network Devices from Catalyst Center..."):
    devices = get_network_devices()

if not devices:
    st.error("Failed to fetch devices. Check your controller connection.")
    st.stop()

device_dict = {
    dev.get("hostname", "Unknown"): {
        "uuid": dev.get("id"),
        "ip": dev.get("managementIpAddress")
    } 
    for dev in devices
}

selected_hostname = st.sidebar.selectbox("Select Target Switch", list(device_dict.keys()))
selected_device_uuid = device_dict[selected_hostname]["uuid"]
selected_device_ip = device_dict[selected_hostname]["ip"]

st.sidebar.success(f"**IP:** {selected_device_ip}")

# --- Main Area: Interface Metrics ---
st.subheader(f"Interface Status: {selected_hostname}")

with st.spinner(f"Querying interface telemetry for {selected_hostname}..."):
    interfaces = get_device_interfaces(selected_device_uuid)

if interfaces:
    port_data = []
    for interface in interfaces:
        name = interface.get("portName", "")
        
        if "Vlan" not in name and "Loopback" not in name:
            
            # --- Optimistic UI Override ---
            current_admin_status = interface.get("adminStatus")
            current_op_status = interface.get("status")
            
            # If the port is in our memory, force it to DOWN
            if name in st.session_state.isolated_ports:
                current_admin_status = "DOWN"
                current_op_status = "down"
            # --------------------------------------------

            port_data.append({
                "Port Name": name,
                "Admin Status": current_admin_status,
                "Operational Status": current_op_status,
                "MAC Address": interface.get("macAddress")
            })
    
    df = pd.DataFrame(port_data)
    st.dataframe(df, width="stretch")
else:
    st.warning("No interface data found for this device.")

# --- Action Panel: Automation Execution ---
st.divider()
st.subheader("⚡ Automated Port Control (Zero-Trust Response)")

col1, col2, col3 = st.columns(3)

with col1:
    port_names = [p["Port Name"] for p in port_data] if interfaces else []
    target_port = st.selectbox("Target Interface", port_names)

with col2:
    action = st.radio("Desired State", ["shutdown", "no shutdown"], horizontal=True)

with col3:
    st.write("") 
    st.write("") 
    if st.button("🚀 Execute Configuration", type="primary"):
        with st.spinner(f"Initiating zero-trust workflow for {selected_hostname}..."):
            
            success, alert_data = change_port_state(selected_device_ip, target_port, state=action)
            
            if success:
                # 1. Update the isolated ports memory
                if action == "shutdown" and target_port not in st.session_state.isolated_ports:
                    st.session_state.isolated_ports.append(target_port)
                elif action == "no shutdown" and target_port in st.session_state.isolated_ports:
                    st.session_state.isolated_ports.remove(target_port)
                
                # 2. Save the ticket to memory so it survives the refresh
                st.session_state.incident_ticket = alert_data
                
                # 3. Force the app to instantly reload from top to bottom
                if hasattr(st, 'rerun'):
                    st.rerun()
                else:
                    st.experimental_rerun()
            else:
                st.error("Failed to generate escalation payload.")

# --- Dynamic Ticket Display ---
# Because this is outside the button logic, it will display perfectly after the rerun!
if st.session_state.incident_ticket:
    st.warning("⚠️ Direct execution blocked by RBAC. SecOps Escalation Triggered.")
    st.success(f"Incident Ticket generated for {st.session_state.incident_ticket['target_interface']}.")
    st.json(st.session_state.incident_ticket)