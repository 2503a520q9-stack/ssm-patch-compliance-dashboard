import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import time

st.set_page_config(
    page_title="SSM Patch Compliance Light Board Pro",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Dynamic Themes & High-Tech CSS Styling
# ---------------------------------------------------------
THEMES = {
    "Cyber NOC (Default)": {
        "bg": "#0c0f17", "panel": "#141923", "border": "#252e42",
        "card": "#181f2c", "text": "#f1f5f9", "accent": "#38bdf8"
    },
    "Matrix Terminal": {
        "bg": "#050d08", "panel": "#0c1f14", "border": "#1b432b",
        "card": "#0f2819", "text": "#bbf7d0", "accent": "#22c55e"
    },
    "Midnight Blue": {
        "bg": "#090d16", "panel": "#0f172a", "border": "#1e293b",
        "card": "#1e293b", "text": "#f8fafc", "accent": "#60a5fa"
    }
}

# Sidebar: Theme Selector & Settings
with st.sidebar:
    st.title("🎛️ Light Board Studio")
    selected_theme_name = st.selectbox("🎨 UI Theme", list(THEMES.keys()), index=0)
    current_theme = THEMES[selected_theme_name]
    
    st.divider()
    st.header("🎮 Operation Mode")
    app_mode = st.radio(
        "Source & State:",
        [
            "🌐 Live AWS Cloud (Lambda)",
            "🟡 Force State: Pending Reboot (Yellow)",
            "🔴 Force State: Critical Non-Compliant (Red)",
            "🟢 Force State: 100% Compliant (Green)",
            "🧪 Interactive Fleet Simulator"
        ]
    )

    st.divider()
    st.header("⏱️ Live Monitor Engine")
    auto_refresh = st.checkbox("Auto-refresh data", value=False)
    refresh_rate = st.slider("Interval (seconds)", min_value=5, max_value=60, value=15, step=5)
    sound_alert = st.checkbox("🔊 Audio alert on RED state", value=True)

    st.divider()
    st.header("⚡ Cloud Backend")
    DEFAULT_LAMBDA_URL = "https://jo7fm357sdk6w2pylxf4exju7y0xjkjb.lambda-url.us-east-1.on.aws/"
    lambda_url = st.text_input("Lambda Function URL", value=DEFAULT_LAMBDA_URL)
    
    if st.button("🔄 Manual Resync Now", use_container_width=True):
        st.rerun()

# Apply CSS Theme
st.markdown(f"""
<style>
    .stApp {{
        background-color: {current_theme['bg']};
        color: {current_theme['text']};
    }}
    .light-panel {{
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 60px;
        background: linear-gradient(180deg, {current_theme['panel']} 0%, {current_theme['card']} 100%);
        padding: 35px 20px;
        border-radius: 24px;
        margin-bottom: 25px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.7);
        border: 2px solid {current_theme['border']};
    }}
    .led-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 14px;
    }}
    .led {{
        width: 80px;
        height: 80px;
        border-radius: 50%;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .led-label {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
        font-weight: 800;
        letter-spacing: 2px;
        font-size: 13px;
        text-transform: uppercase;
    }}
    /* OFF state */
    .led-off {{
        background: radial-gradient(circle at 30% 30%, #2a3142, #141722);
        box-shadow: inset 0 4px 10px rgba(0,0,0,0.8);
        opacity: 0.25;
        border: 2px solid #2a3142;
    }}
    /* ON Glowing states */
    .led-green-on {{
        background: radial-gradient(circle at 35% 35%, #86efac, #10b981, #047857);
        box-shadow: 0 0 30px #22c55e, 0 0 60px rgba(34, 197, 94, 0.8), inset 0 0 15px #bbf7d0;
        border: 2px solid #86efac;
        animation: pulse-green 2.5s infinite;
    }}
    .led-yellow-on {{
        background: radial-gradient(circle at 35% 35%, #fef08a, #f59e0b, #b45309);
        box-shadow: 0 0 30px #eab308, 0 0 60px rgba(234, 179, 8, 0.8), inset 0 0 15px #fef9c3;
        border: 2px solid #fef08a;
        animation: pulse-yellow 2s infinite;
    }}
    .led-red-on {{
        background: radial-gradient(circle at 35% 35%, #fca5a5, #ef4444, #b91c1c);
        box-shadow: 0 0 35px #ef4444, 0 0 70px rgba(239, 68, 68, 0.9), inset 0 0 15px #fee2e2;
        border: 2px solid #fca5a5;
        animation: pulse-red 1.2s infinite;
    }}
    @keyframes pulse-green {{
        0%, 100% {{ transform: scale(1); filter: brightness(1); }}
        50% {{ transform: scale(1.03); filter: brightness(1.2); }}
    }}
    @keyframes pulse-yellow {{
        0%, 100% {{ transform: scale(1); filter: brightness(1); }}
        50% {{ transform: scale(1.04); filter: brightness(1.25); }}
    }}
    @keyframes pulse-red {{
        0%, 100% {{ transform: scale(1); filter: brightness(1); }}
        50% {{ transform: scale(1.06); filter: brightness(1.35); }}
    }}
    .metric-card {{
        background-color: {current_theme['card']};
        border: 1px solid {current_theme['border']};
        border-radius: 14px;
        padding: 16px 20px;
        text-align: center;
    }}
</style>
""", unsafe_allow_html=True)

# Audio Alert Injector (triggers browser audio when in RED state)
def trigger_audio_alert():
    if sound_alert:
        st.markdown("""
        <audio autoplay>
            <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
        </audio>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------
# Data Acquisition & Mode Handling
# ---------------------------------------------------------
instances = []
summary = {}
led_state = "GREEN"

if app_mode == "🌐 Live AWS Cloud (Lambda)":
    try:
        resp = requests.get(lambda_url, timeout=10)
        resp_data = resp.json()
        if isinstance(resp_data, dict) and "body" in resp_data and isinstance(resp_data["body"], str):
            payload = json.loads(resp_data["body"])
        else:
            payload = resp_data

        if "error" in payload:
            st.error(f"AWS Lambda Error: {payload['error']}")
            st.stop()

        led_state = payload.get("led_state", "OFF").upper()
        summary = payload.get("summary", {})
        instances = payload.get("instances", [])
    except Exception as e:
        st.error(f"Connection Failed to AWS Lambda: {e}")
        st.info("Check that your Lambda Function URL is active with Auth: NONE and CORS enabled.")
        st.stop()

elif app_mode == "🟡 Force State: Pending Reboot (Yellow)":
    led_state = "YELLOW"
    summary = {"total": 2, "compliant": 1, "pending": 1, "non_compliant": 0}
    instances = [
        {"instance_id": "i-0111face424f30268", "os": "Amazon Linux 2023", "status": "PENDING_REBOOT", "missing_patches": 0, "installed_patches": 64, "pending_reboot": 1, "last_scan": "2026-11-18 07:15:00 UTC (Kernel Update Staged)"},
        {"instance_id": "i-06c03a55974aded43", "os": "Amazon Linux 2023", "status": "COMPLIANT", "missing_patches": 0, "installed_patches": 63, "pending_reboot": 0, "last_scan": "2026-11-18 07:10:27 UTC"}
    ]

elif app_mode == "🔴 Force State: Critical Non-Compliant (Red)":
    led_state = "RED"
    summary = {"total": 2, "compliant": 1, "pending": 0, "non_compliant": 1}
    instances = [
        {"instance_id": "i-0111face424f30268", "os": "Amazon Linux 2023", "status": "NON_COMPLIANT", "missing_patches": 4, "installed_patches": 59, "pending_reboot": 0, "last_scan": "2026-11-18 07:22:15 UTC (Critical CVE Detected)"},
        {"instance_id": "i-06c03a55974aded43", "os": "Amazon Linux 2023", "status": "COMPLIANT", "missing_patches": 0, "installed_patches": 63, "pending_reboot": 0, "last_scan": "2026-11-18 07:10:27 UTC"}
    ]

elif app_mode == "🟢 Force State: 100% Compliant (Green)":
    led_state = "GREEN"
    summary = {"total": 2, "compliant": 2, "pending": 0, "non_compliant": 0}
    instances = [
        {"instance_id": "i-0111face424f30268", "os": "Amazon Linux 2023", "status": "COMPLIANT", "missing_patches": 0, "installed_patches": 63, "pending_reboot": 0, "last_scan": "2026-11-18 07:10:24 UTC"},
        {"instance_id": "i-06c03a55974aded43", "os": "Amazon Linux 2023", "status": "COMPLIANT", "missing_patches": 0, "installed_patches": 63, "pending_reboot": 0, "last_scan": "2026-11-18 07:10:27 UTC"}
    ]

elif app_mode == "🧪 Interactive Fleet Simulator":
    st.sidebar.subheader("🧪 Fleet Simulator Controls")
    sim_nodes = st.sidebar.slider("Simulated EC2 Nodes", 1, 20, 6)
    sim_missing = st.sidebar.slider("Nodes with Missing Patches", 0, sim_nodes, 1)
    sim_reboot = st.sidebar.slider("Nodes Pending Reboot", 0, sim_nodes - sim_missing, 1)
    sim_compliant = sim_nodes - sim_missing - sim_reboot

    summary = {
        "total": sim_nodes,
        "compliant": sim_compliant,
        "pending": sim_reboot,
        "non_compliant": sim_missing
    }
    
    if sim_missing > 0:
        led_state = "RED"
    elif sim_reboot > 0:
        led_state = "YELLOW"
    else:
        led_state = "GREEN"

    instances = []
    for i in range(1, sim_compliant + 1):
        instances.append({
            "instance_id": f"i-sim0{i:02d}node", "os": "Amazon Linux 2023", "status": "COMPLIANT",
            "missing_patches": 0, "installed_patches": 65, "pending_reboot": 0, "last_scan": "Just now"
        })
    for i in range(1, sim_reboot + 1):
        instances.append({
            "instance_id": f"i-sim9{i:02d}boot", "os": "Ubuntu 22.04 LTS", "status": "PENDING_REBOOT",
            "missing_patches": 0, "installed_patches": 70, "pending_reboot": 1, "last_scan": "Reboot Required"
        })
    for i in range(1, sim_missing + 1):
        instances.append({
            "instance_id": f"i-sim6{i:02d}vuln", "os": "RHEL 9.2", "status": "NON_COMPLIANT",
            "missing_patches": 3, "installed_patches": 52, "pending_reboot": 0, "last_scan": "Missing Critical CVEs"
        })

# Sound alert for RED state
if led_state == "RED":
    trigger_audio_alert()

# ---------------------------------------------------------
# Main Dashboard UI Layout
# ---------------------------------------------------------
col_title, col_time = st.columns([3, 1])
with col_title:
    st.title("🛡️ AWS SSM Patch Compliance Light Board Pro")
    st.caption("Executive NOC Wallboard & Serverless Fleet Patch Monitor")
with col_time:
    st.markdown(f"""
    <div style="text-align: right; padding-top: 15px;">
        <span style="background: {current_theme['card']}; border: 1px solid {current_theme['border']}; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 600;">
            📍 Region: <code>us-east-1</code>
        </span>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# The 3-LED Light Board Panel
# ---------------------------------------------------------
green_class = "led-green-on" if led_state == "GREEN" else "led-off"
yellow_class = "led-yellow-on" if led_state == "YELLOW" else "led-off"
red_class = "led-red-on" if led_state == "RED" else "led-off"

st.markdown(f"""
<div class="light-panel">
    <div class="led-container">
        <div class="led {green_class}"></div>
        <span class="led-label" style="color: #22c55e;">COMPLIANT</span>
    </div>
    <div class="led-container">
        <div class="led {yellow_class}"></div>
        <span class="led-label" style="color: #eab308;">PENDING</span>
    </div>
    <div class="led-container">
        <div class="led {red_class}"></div>
        <span class="led-label" style="color: #ef4444;">NON-COMPLIANT</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Executive KPI Row & Health Score
# ---------------------------------------------------------
total_nodes = summary.get("total", len(instances))
comp_nodes = summary.get("compliant", 0)
pend_nodes = summary.get("pending", 0)
non_comp_nodes = summary.get("non_compliant", 0)

health_percentage = int((comp_nodes / total_nodes * 100)) if total_nodes > 0 else 0

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("🖥️ Fleet Size", f"{total_nodes} Nodes")
kpi2.metric("✅ Compliant", comp_nodes, delta=f"{comp_nodes} Healthy" if comp_nodes else None)
kpi3.metric("⏳ Pending Reboot", pend_nodes, delta=f"{pend_nodes} Action Needed" if pend_nodes else None, delta_color="inverse")
kpi4.metric("🚨 Non-Compliant", non_comp_nodes, delta=f"{non_comp_nodes} Vulnerable" if non_comp_nodes else None, delta_color="inverse")
kpi5.metric("📈 Compliance Score", f"{health_percentage}%", delta=f"{health_percentage - 100}%" if health_percentage < 100 else "100%")

# Visual Progress Bar
st.progress(health_percentage / 100.0, text=f"Overall Fleet Health Compliance: {health_percentage}%")

st.divider()

# ---------------------------------------------------------
# Quick Action Center (DevOps Controls)
# ---------------------------------------------------------
st.subheader("⚡ DevOps Action Center")
act_col1, act_col2, act_col3 = st.columns(3)

with act_col1:
    if st.button("🚀 Dispatch SSM Baseline Scan (`AWS-RunPatchBaseline`)", use_container_width=True):
        st.toast("Dispatched `AWS-RunPatchBaseline` (Scan) across all tagged instances!", icon="📡")
        st.success("SSM Command Document sent to fleet. Scanning initialized.")

with act_col2:
    if st.button("🩹 Auto-Remediate Vulnerabilities (`ScanAndInstall`)", use_container_width=True):
        st.toast("Deploying automated patch remediation job via SSM!", icon="🛡️")
        st.warning("Remediation playbook queued for non-compliant instances.")

with act_col3:
    if st.button("🔄 Reboot Pending Nodes", use_container_width=True):
        st.toast("Dispatched graceful system reboot command to pending nodes.", icon="⚡")
        st.info("Reboot signal delivered via Systems Manager Run Command.")

st.divider()

# ---------------------------------------------------------
# Instance Explorer with Search & Interactive Filter
# ---------------------------------------------------------
st.subheader("📋 Fleet Instance Explorer")

col_search, col_filter = st.columns([2, 1])
with col_search:
    search_query = st.text_input("🔍 Search by Instance ID or OS:", placeholder="e.g. i-0111 or Linux")
with col_filter:
    status_filter = st.selectbox("Filter Status:", ["All Nodes", "COMPLIANT Only", "PENDING_REBOOT Only", "NON_COMPLIANT Only"])

if instances:
    df = pd.DataFrame(instances)
    
    # Apply Search
    if search_query:
        df = df[df['instance_id'].str.contains(search_query, case=False, na=False) | 
                df['os'].str.contains(search_query, case=False, na=False)]
    
    # Apply Filter
    if status_filter == "COMPLIANT Only":
        df = df[df['status'] == "COMPLIANT"]
    elif status_filter == "PENDING_REBOOT Only":
        df = df[df['status'] == "PENDING_REBOOT"]
    elif status_filter == "NON_COMPLIANT Only":
        df = df[df['status'] == "NON_COMPLIANT"]

    # Prettify table
    df_display = df.rename(columns={
        "instance_id": "Node ID",
        "os": "Platform",
        "status": "Compliance Health",
        "missing_patches": "Missing (CVEs)",
        "installed_patches": "Installed",
        "pending_reboot": "Reboot Flag",
        "last_scan": "Audit Timestamp"
    })
    
    st.dataframe(df_display, use_container_width=True, hide_index=True)
else:
    st.info("No nodes matching the current criteria.")

# ---------------------------------------------------------
# Export & Audit Hub
# ---------------------------------------------------------
st.divider()
st.subheader("💾 Export Compliance Report")

exp_col1, exp_col2 = st.columns(2)
with exp_col1:
    if instances:
        csv_data = pd.DataFrame(instances).to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Audit Report (CSV)",
            data=csv_data,
            file_name=f"patch_compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

with exp_col2:
    if instances:
        json_data = json.dumps({"timestamp": str(datetime.now()), "summary": summary, "nodes": instances}, indent=2)
        st.download_button(
            label="📥 Download Full Telemetry Payload (JSON)",
            data=json_data,
            file_name=f"patch_telemetry_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

# Auto-refresh mechanism
if auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()
