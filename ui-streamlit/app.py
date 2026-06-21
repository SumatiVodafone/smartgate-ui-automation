import streamlit as st
import pandas as pd
import subprocess
from pathlib import Path
import base64

# ---------- CONFIG ----------
JAVA_PROJECT = r"C:\projects\smartgate-ui-automation"
BASE_CSV_FOLDER = Path(r"C:\projects\smartgate-downloads")

def get_base64_image(image_path):
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode()
    

MASTER_DEVICES = {
    "X101-GER-PORT1-AVSB-FUT_EMMC_RAYSON-DE_PROD-DVBC",
    "X101-GER-PORT2-AVSB-MP-DE_PROD-DVBC",
    "X101-GER-PORT3-AVSB-FUT_EMMC_RAYSON-DE_PROD-OTT",
    "X101-GER-PORT4-GEN3-FUT-DE_PROD-DVBC",
    "X102-GER-PORT1-GEN3-MP-DE_PROD-DVBC",
    "X102-GER-PORT2-GEN3-MP-DE_PROD-DVBC",
    "X102-GER-PORT3-AVSB-FUT_EMMC_WESTERN-DE_PROD-OTT",
    "X102-GER-PORT4-GEN3-FUT_LPDDR_RAY&FORE-DE_PROD-DVBC",
    "X104-GER-PORT1-GEN4_SGM-FUT_LPDDR4GB-DE_PROD-DVBC",
    "X104-GER-PORT2-GEN4_SGM-FUT_LPDDR4GB-DE_PROD-DVBC",
    "X104-GER-PORT3-AVSB-FUT-DE_PROD-DVBC",
    "X104-GER-PORT4-AVSB-FUT_EMMC_WESTERN-DE_PROD-DVBC",
    "X105-GER-PORT1-AVSB-MP-DE_PROD-OTT",
    "X105-GER-PORT2-AVSB-MP-DE_PROD-DVBC",
    "X105-GER-PORT3-GEN3-FUT_LPDDR_RAY&FORE-DE_PROD-OTT",
    "X105-GER-PORT4-GEN3-FUT-DE_PROD-OTT",
    "X106-IE-PORT1-AVSB-FUT-IE_PROD-MCAST",
    "X106-IE-PORT2-GEN3-FUT-IE_PROD-MCAST",
    "X106-IE-PORT3-GEN3-FUT-IE_PROD-MCAST",
    "X106-IE-PORT4-AVSB-FUT-IE_PROD-MCAST",
    "X107-POR-PORT1-AVSB-FUT-PT_PROD-MCAST",
    "X107-POR-PORT2-AVSB-FUT-PT_PROD-MCAST",
    "X107-POR-PORT3-AVSB-FUT-PT_PROD-MCAST",
    "X107-POR-PORT4-GEN3-FUT-PT_PROD-MCAST",
    "X108-POR-PORT1-GEN3-FUT-PT_PROD-MCAST",
    "X108-POR-PORT2-GEN3-FUT-PT_PROD-MCAST",
    "X108-POR-PORT3-GEN3-FUT-PT_PROD-MCAST",
    "X108-POR-PORT4-GEN3-FUT-PT_PROD-MCAST",
    "X109-CZ-PORT1-GEN3-FUT-CZ_PROD-DVBC",
    "X109-CZ-PORT2-GEN3-FUT-CZ_PROD-DVBC",
    "X109-CZ-PORT3-GEN3-FUT-CZ_PROD-DVBC",
    "X109-CZ-PORT4-GEN3-FUT-CZ_PROD-DVBC",
    "X111-GRE-PORT1-GEN3-FUT-GR_PROD-MCAST_DTT",
    "X111-GRE-PORT2-GEN3-FUT-GR_PROD-MCAST_DTT",
    "X111-GRE-PORT3-GEN3-FUT-GR_PROD-MCAST_DTT",
    "X111-GRE-PORT4-GEN3-FUT-GR_PROD-MCAST_DTT",
    "X112-ES-PORT1-GEN3-FUT-ES_PROD-HFC",
    "X112-ES-PORT2-GEN3-FUT-ES_PROD-HFC",
    "X112-ES-PORT3-GEN3-FUT-ES_PROD-FTTH",
    "X112-ES-PORT4-GEN3-FUT-ES_PROD-NEBA",
    "X113-ES-PORT1-GEN3-FUT-ES_PROD-NEBA",
    "X113-ES-PORT2-GEN3-FUT-ES_PROD-FTTH",
    "X113-ES-PORT3-GEN3-FUT-ES_PROD-FTTH",
    "X113-ES-PORT4-GEN3-FUT-ES_PROD-FTTH",
    "X114-GER-PORT1-GEN4_SGM-FUT-DE_PROD-DVBC",
    "X114-GER-PORT2-GEN4_SGM-FUT-DE_PROD-DVBC",
    "X114-GER-PORT3-GEN4_SGM-FUT-DE_PROD-DVBC",
    "X114-GER-PORT4-GEN4_SGM-FUT-DE_PROD-DVBC",
    "X115-GRE-PORT1-GEN4_SGM-FUT-GR_PROD-MCAST",
    "X115-GRE-PORT2-GEN4_SGM-FUT-GR_PROD-MCAST",
    "X115-GRE-PORT3-GEN4_SGM-FUT_LPDDR4GB-GR_PROD-MCAST",
    "X115-GRE-PORT4-GEN4_SGM-FUT_LPDDR4GB-GR_PROD-MCAST",
    "X116-GER-PORT1-GEN3-MP-DE_PROD-OTT",
    "X116-GER-PORT2-GEN4_SGM-FUT-DE_PROD-OTT",
    "X116-GER-PORT3-GEN4_SGM-FUT_LPDDR4GB-DE_PROD-OTT",
    "X116-GER-PORT4-GEN4_SGM-FUT_LPDDR4GB-DE_PROD-DVBC",
    "X117-AL-PORT1-GEN4_SGM-FUT-AL_PROD-DVBC",
    "X117-AL-PORT2-GEN3-MP-AL_PROD-DVBC",
    "X117-AL-PORT3-GEN4_SGM-FUT-AL_PROD-DVBC",
    "X117-AL-PORT4-GEN3-MP-AL_PROD-DVBC",
    "X118-CZ-PORT1-AVSB-FUT-CZ_PROD-DVBC",
    "X118-CZ-PORT2-AVSB-FUT-CZ_PROD-DVBC",
    "X118-CZ-PORT3-AVSB-FUT-CZ_PROD-DVBC",
    "X118-CZ-PORT4-AVSB-FUT-CZ_PROD-DVBC",
    "X119-GER-PORT1-GEN3-FUT-DE_PROD-DVBC",
    "X119-GER-PORT2-AVSB-FUT-DE_PROD-DVBC",
    "X119-GER-PORT3-GEN3-FUT_EMMC-DE_PROD-DVBC",
    "X119-GER-PORT4-GEN3-FUT_EMMC-DE_PROD-OTT",
    "X120-POR-PORT1-GEN4_SGM-FUT-PT_PROD-MCAST",
    "X120-POR-PORT2-GEN4_SGM-FUT_LPDDR4GB-PT_PROD-MCAST",
    "X120-POR-PORT3-GEN4_SGM-FUT-PT_PROD-MCAST",
    "X120-POR-PORT4-GEN4_SGM-FUT_LPDDR4GB-PT_PROD-MCAST",
    "X121-IE-PORT1-GEN3-ALPHA-IE_PROD-MCAST",
    "X121-IE-PORT2-AVSB-FUT-IE_PROD-MCAST",
    "X121-IE-PORT3-GEN3-ALPHA-IE_PROD-MCAST",
    "X121-IE-PORT4-AVSB-FUT-IE_PROD-MCAST"
}


# ---------- EXPECTED SCENARIOS ----------
EXPECTED_SCENARIOS = {
    "CZ": {
        "CT": {
            "Catchup", "Disney", "Guide_Navigation", "HBO",
            "MiniPI To ExtendedPI", "Pause_Resume", "Random_Zapping",
            "Rewind_Playback", "StartOver", "TLM Launch Via Hotkey",
            "TLM_Navigation", "TVGuide Loadtime", "Tune Live TV Via TVGuide",
            "VOD", "Wakeup From Standby", "Youtube", "nPVR", "Amazon"
        },
        "LongPlayback": {
            "Live", "Catchup", "Disney", "HBO", "VOD",
            "Youtube", "nPVR", "Amazon"
        },
        "Environmental": {
            "BT Validation", "Device Health Status",
            "Network Validation", "Technical & System Integration"
        }
    },
    "IE": {
        "CT": {
            "Catchup", "Disney", "Guide_Navigation",
            "MiniPI To ExtendedPI", "Netflix", "Pause_Resume",
            "Random_Zapping", "Rewind_Playback", "StartOver",
            "TLM Launch Via Hotkey", "TLM_Navigation",
            "TVGuide Loadtime", "Tune Live TV Via TVGuide",
            "Wakeup From Standby", "Youtube", "nPVR", "Amazon"
        },
        "LongPlayback": {
            "Live", "Catchup", "Disney", "Netflix",
            "Youtube", "nPVR", "Amazon"
        },
        "Environmental": {
            "BT Validation", "Device Health Status",
            "Network Validation", "Technical & System Integration"
        }
    },
    "ES": {
        "CT": {
            "Catchup", "Disney", "Guide_Navigation", "HBO",
            "MiniPI To ExtendedPI", "Netflix", "Pause_Resume",
            "Random_Zapping", "Rewind_Playback", "StartOver",
            "TLM Launch Via Hotkey", "TLM_Navigation",
            "TVGuide Loadtime", "Tune Live TV Via TVGuide",
            "VOD", "Wakeup From Standby", "Youtube", "nPVR", "Amazon"
        },
        "LongPlayback": {
            "Live", "Catchup", "Disney", "HBO", "Netflix",
            "VOD", "Youtube", "nPVR", "Amazon"
        },
        "Environmental": {
            "BT Validation", "Device Health Status",
            "Network Validation", "Technical & System Integration"
        }
    },
    "DE": {
        "CT": {
            "DAZN", "Disney", "Guide_Navigation", "Media Library",
            "MiniPI To ExtendedPI", "Netflix", "Pause_Resume",
            "Random_Zapping", "Rewind_Playback", "StartOver",
            "TLM Launch Via Hotkey", "TLM_Navigation",
            "TVGuide Loadtime", "Tune Live TV Via TVGuide",
            "VOD", "Wakeup From Standby", "Youtube", "nPVR", "Amazon"
        },
        "LongPlayback": {
            "Live", "Disney", "Netflix", "VOD",
            "Youtube", "nPVR", "Amazon"
        },
        "Environmental": {
            "BT Validation", "Device Health Status",
            "Network Validation", "Technical & System Integration"
        }
    },
    "PT": {
        "CT": {
            "Catchup", "Disney", "Guide_Navigation", "HBO",
            "MiniPI To ExtendedPI", "Netflix", "Pause_Resume",
            "Random_Zapping", "Rewind_Playback", "StartOver",
            "TLM Launch Via Hotkey", "TLM_Navigation",
            "TVGuide Loadtime", "Tune Live TV Via TVGuide",
            "VOD", "Wakeup From Standby", "Youtube", "nPVR", "Amazon"
        },
        "LongPlayback": {
            "Live", "Catchup", "Disney", "HBO", "Netflix",
            "VOD", "Youtube", "nPVR", "Amazon"
        },
        "Environmental": {
            "BT Validation", "Device Health Status",
            "Network Validation", "Technical & System Integration"
        }
    },
    "GR": {
        "CT": {
            "Catchup", "Disney", "Guide_Navigation",
            "MiniPI To ExtendedPI", "Netflix", "Pause_Resume",
            "Random_Zapping", "Rewind_Playback", "StartOver",
            "TLM Launch Via Hotkey", "TLM_Navigation",
            "TVGuide Loadtime", "Tune Live TV Via TVGuide",
            "Tune Live TV Via TVGuide_GR_DTT",
            "Tune Live TV Via TVGuide_GR_MCAST_To_DTT",
            "VOD", "Wakeup From Standby", "Youtube", "nPVR", "Amazon"
        },
        "LongPlayback": {
            "Live", "Catchup", "Disney", "Netflix",
            "VOD", "Youtube", "nPVR", "Amazon"
        },
        "Environmental": {
            "BT Validation", "Device Health Status",
            "Network Validation", "Technical & System Integration"
        }
    },
    "AL": {
        "CT": {
            "Catchup", "Disney", "Guide_Navigation",
            "MiniPI To ExtendedPI", "Pause_Resume",
            "Random_Zapping", "Rewind_Playback", "StartOver",
            "TLM Launch Via Hotkey", "TLM_Navigation",
            "TVGuide Loadtime", "Tune Live TV Via TVGuide",
            "VOD", "Wakeup From Standby", "Youtube", "nPVR", "Amazon"
        },
        "LongPlayback": {
            "Live", "Catchup", "Disney", "VOD",
            "Youtube", "nPVR", "Amazon"
        },
        "Environmental": {
            "BT Validation", "Device Health Status",
            "Network Validation", "Technical & System Integration"
        }
    }
}

EXPECTED_ZAPPING = {
    "PT_Zap_CH_Number", "PT_Zap_CH_Plus", "PT_MCAST_Zap_CH_Number", "PT_MCAST_Zap_CH_Plus",
    "DE_Zap_CH_Number", "DE_Zap_CH_Plus", "DE_OTT_Zap_CH_Number", "DE_OTT_Zap_CH_Plus",
    "DE_DVBC_Zap_CH_Number", "DE_DVBC_Zap_CH_Plus", "DE_Radio_Channel_Zap_CH_Number",
    "DE_Fast_Channel_Zap_CH_Number", "DE_Fast_Channel_Zap_CH_Plus_CT", "CZ_DVBC_Zap_CH_Number",
    "CZ_DVBC_Zap_CH_Plus", "CZ_Radio_Channel_Zap_CH_Number", "CZ_Fast_Channel_Zap_CH_Number",
    "ES_OTT_NEBA_Zap_CH_Number", "ES_OTT_NEBA_Zap_CH_Plus", "ES_OTT_NEBA_Fast_Channel_Zap_CH_Plus_CT",
    "ES_NEBA_Fast_Channel_Zap_CH_Number", "ES_DVBC_HFC_Zap_CH_Number", "ES_DVBC_HFC_Zap_CH_Plus",
    "ES_DVBC_HFC_Fast_Channel_Zap_CH_Plus_CT", "ES_HFC_Fast_Channel_Zap_CH_Number",
    "ES_MCAST_FTTH_Zap_CH_Number", "ES_MCAST_FTTH_Zap_CH_Plus", "ES_MCAST_FTTH_Fast_Channel_Zap_CH_Plus_CT",
    "ES_FTTH_Fast_Channel_Zap_CH_Number", "AL_DVBC_Zap_CH_Number", "AL_DVBC_Zap_CH_Plus",
    "IE_MCAST_Zap_CH_Number", "IE_MCAST_Zap_CH_Plus_CT", "GR_DTT_Zap_CH_Number",
    "GR_DTT_Zap_CH_Plus", "GR_MCAST_Zap_CH_Number", "GR_MCAST_Zap_CH_Plus_CT"
}


def detect_country(env_name):
    env_upper = str(env_name).upper()
    for country in EXPECTED_SCENARIOS.keys():
        if country in env_upper:
            return country
    return None


def find_maven_cmd():
    candidates = [
        r"C:\Program Files\Apache\apache-maven-3.9.12\bin\mvn.cmd",
        "mvn.cmd",
        "mvn",
        str(Path(JAVA_PROJECT) / "mvnw.cmd"),
    ]

    for cmd in candidates:
        try:
            subprocess.run([cmd, "-v"], capture_output=True, timeout=5)
            return cmd
        except:
            continue

    return None


MAVEN_CMD = find_maven_cmd()
st.set_page_config(page_title="Smartgate Dashboard", layout="wide")

st.markdown("""
<style>

/* Labels like Dashboard Type / Select Time Range */
label, .stSelectbox label {
    font-size: 20px !important;
    font-weight: 600 !important;
    color: #111827 !important;
}

/* Dropdown box */
div[data-baseweb="select"] > div {
    border: 2px solid #c7d2fe !important;
    border-radius: 12px !important;
    min-height: 56px !important;
    font-size: 22px !important;
    font-weight: 500 !important;
    background-color: white !important;
    box-shadow: none !important;
}

/* Selected dropdown text */
div[data-baseweb="select"] span {
    font-size: 22px !important;
    font-weight: 500 !important;
    color: #111827 !important;
}

/* Time Filter heading */
h2 {
    font-size: 20px !important;
    font-weight: 500 !important;
    color: #0f172a !important;
}

/* Info caption */
.stCaption {
    font-size: 18px !important;
    color: #6b7280 !important;
}

/* Button styling */
.stButton > button {
    border: 2px solid #2563eb !important;
    border-radius: 12px !important;
    padding: 12px 28px !important;
    font-size: 22px !important;
    font-weight: 600 !important;
    color: #2563eb !important;
    background-color: white !important;
}

/* Page spacing */
.block-container {
    padding-top: 2rem !important;
    padding-left: 3rem !important;
    padding-right: 3rem !important;
}

</style>
""", unsafe_allow_html=True)


def download_latest_csv(dashboard_type):
    if not MAVEN_CMD:
        st.error("❌ Maven not found")
        return

    build = subprocess.run(
        [MAVEN_CMD, "clean", "dependency:copy-dependencies", "compile"],
        cwd=JAVA_PROJECT,
        capture_output=True,
        text=True,
        timeout=300
    )

    if build.returncode != 0:
        st.error("❌ Build failed")
        st.text(build.stderr)
        return

    java_arg = "ZAPPING" if dashboard_type == "Zapping" else dashboard_type

    run = subprocess.run(
        [
            "java",
            "-cp",
            "target/classes;target/dependency/*",
            "com.smartgate.automation.App",
            java_arg
        ],
        cwd=JAVA_PROJECT,
        capture_output=True,
        text=True
    )

    if run.returncode != 0:
        st.error("❌ Java failed")
        st.text(run.stderr)


def get_csv_folder(dashboard_type):
    if dashboard_type == "Zapping":
        return BASE_CSV_FOLDER / "Zapping"

    elif dashboard_type in ["Environmental", "Devices Without Test Execution"]:
        return BASE_CSV_FOLDER / "Environmental-DeviceNoExecution"

    else:
        return BASE_CSV_FOLDER / "CT-LongPlayback"


def load_latest_csv(dashboard_type):
    csv_folder = get_csv_folder(dashboard_type)

    if not csv_folder.exists():
        return None

    files = list(csv_folder.glob("*.csv"))

    if not files:
        return None

    latest = max(files, key=lambda x: x.stat().st_mtime)
    return pd.read_csv(latest)

def normalize_device_name(name):
    return str(name).strip().upper()

def check_environmental_execution(df):
    if "devicename" not in df.columns:
        st.error("deviceName column not found in CSV")
        st.stop()

    if "scenarioname" not in df.columns:
        st.error("scenarioName column not found in CSV")
        st.stop()

    df = df.copy()

    df["devicename"] = df["devicename"].astype(str).str.strip().str.upper()
    df["scenarioname"] = df["scenarioname"].astype(str).str.strip().str.upper()

    scenario_df = df[
        df["scenarioname"] == "CHECK_MAINTENANCE_DATA_IN_SETTINGS"
    ]

    missing_devices = []

    for device in MASTER_DEVICES:
        if device not in set(scenario_df["devicename"]):
            missing_devices.append(device)

    return sorted(missing_devices)


def check_missing_category_execution(df):
    if "devicename" not in df.columns:
        st.error("deviceName column not found in CSV")
        st.stop()

    if "category" not in df.columns:
        st.error("category column not found in CSV")
        st.stop()

    df = df.copy()

    df["devicename"] = df["devicename"].apply(normalize_device_name)
    df["category"] = df["category"].astype(str).str.strip()

    required_categories = {"CT", "Environmental", "LongPlayback"}

    results = {}

    for device in MASTER_DEVICES:
        device_categories = set(
            df[df["devicename"] == device]["category"].unique()
        )

        missing = required_categories - device_categories

        if missing:
            results[device] = sorted(missing)

    return results


logo_path = r"C:\projects\smartgate-ui-automation\ui-streamlit\witbe_logo.png"
logo = get_base64_image(logo_path)

st.markdown(
    f"""
    <div style="
        display:flex;
        align-items:center;
        gap:20px;
        padding-bottom:20px;
        margin-bottom:30px;
        border-bottom:4px solid #1f5eff;
    ">
        <img src="data:image/png;base64,{logo}" width="140">
        <h1 style="
            margin:0;
            font-size:52px;
            font-weight:800;
            color:#0b1020;
        ">
            Smartgate Execution Dashboard
        </h1>
    </div>
    """,
    unsafe_allow_html=True
)

dashboard_type = st.selectbox(
    "Dashboard Type",
    [
        "CT",
        "LongPlayback",
        "Environmental",
        "Devices Without Test Execution",
        "Zapping"
    ]
)
if st.button("🔄 Refresh Data"):
    download_latest_csv(dashboard_type)
    st.rerun()

df = load_latest_csv(dashboard_type)

if df is None:
    st.warning("No CSV found. Click refresh.")
    st.stop()

df.columns = df.columns.str.strip().str.lower()

if "service" in df.columns:
    df.rename(columns={"service": "scenario"}, inplace=True)

if "time" in df.columns:
    df["time"] = pd.to_numeric(df["time"], errors="coerce")
    df["time"] = pd.to_datetime(
        df["time"],
        unit="ms",
        utc=True,
        errors="coerce"
    ).dt.tz_convert("Asia/Kolkata")

st.markdown("## ⏱ Time Filter")
st.caption("ℹ️ Data older than 30 days is not available on this dashboard.")

if dashboard_type in ["Environmental", "Devices Without Test Execution"]:
    time_filter = st.selectbox(
        "Select Time Range",
        ["Last 24 Hours"]
    )
else:
    time_filter = st.selectbox(
        "Select Time Range",
        [
            "Last 24 Hours",
            "Last 2 Days",
            "Last 7 Days",
            "Last 15 Days",
            "Last 30 Days",
            "Custom Range"
        ]
    )

if "time" in df.columns:
    now = pd.Timestamp.now(tz="Asia/Kolkata")

    if time_filter == "Last 24 Hours":
        df = df[df["time"] >= now - pd.Timedelta(hours=24)]
    elif time_filter == "Last 2 Days":
        df = df[df["time"] >= now - pd.Timedelta(days=2)]
    elif time_filter == "Last 7 Days":
        df = df[df["time"] >= now - pd.Timedelta(days=7)]
    elif time_filter == "Last 15 Days":
        df = df[df["time"] >= now - pd.Timedelta(days=15)]
    elif time_filter == "Last 30 Days":
        df = df[df["time"] >= now - pd.Timedelta(days=30)]
    elif time_filter == "Custom Range":
        col1, col2 = st.columns(2)

        with col1:
            start_date = st.date_input("Start Date")
            start_time = st.time_input("Start Time")

        with col2:
            end_date = st.date_input("End Date")
            end_time = st.time_input("End Time")

        start_dt = pd.Timestamp.combine(start_date, start_time).tz_localize("Asia/Kolkata")
        end_dt = pd.Timestamp.combine(end_date, end_time).tz_localize("Asia/Kolkata")

        df = df[(df["time"] >= start_dt) & (df["time"] <= end_dt)]

if dashboard_type == "Devices Without Test Execution":
    st.subheader("Devices Without Test Execution")

    missing_execution = check_missing_category_execution(df)

    if not missing_execution:
        st.success("✅ All devices have execution in CT, Environmental and LongPlayback")
    else:
        st.error("❌ Devices with incomplete execution coverage")

        result_rows = []

        for device, missing_categories in missing_execution.items():
            result_rows.append({
                "Device Name": device,
                "Missing Categories": ", ".join(missing_categories)
            })

        result_df = pd.DataFrame(result_rows)
        st.dataframe(result_df, use_container_width=True)

    st.stop()


elif dashboard_type == "Environmental":
    st.subheader("Environmental Execution Check")

    missing_devices = check_environmental_execution(df)

    if not missing_devices:
        st.success("✅ Check_Maintenance_Data_In_Settings has run on all devices")
    else:
        st.error("❌ Devices with no Environmental execution")

        result_df = pd.DataFrame({
            "Device Name": missing_devices
        })

        st.dataframe(result_df, use_container_width=True)

    st.stop()

elif dashboard_type == "Zapping":
    st.subheader("📦 Missing Zapping Scenarios")

    if "experience" not in df.columns:
        st.error("Experience column not found in zapping CSV")
        st.stop()

    ran = set(df["experience"].dropna().astype(str).str.strip().unique())
    missing = sorted(EXPECTED_ZAPPING - ran)

    if missing:
        for scenario in missing:
            st.markdown(f"🔴 {scenario} → ❌ Not Run")
    else:
        st.success("✅ All zapping scenarios executed")

else:
    if "category" not in df.columns:
        st.error("Category column not found")
        st.stop()

    # BEFORE time filtering - check what's available
    df_before_time = df[df["category"] == dashboard_type].copy()
    
    # AFTER time filtering
    df = df[df["category"] == dashboard_type]

    if len(df) == 0:
        st.error(f"❌ No data found for category: {dashboard_type}")
        st.stop()

    st.write(f"🎯 After filtering to {dashboard_type}: {len(df)} rows (time-filtered)")

    groups = df.groupby(["environmentversion", "platform", "releaseversion"])
    group_list = list(groups)
    st.write(f"📍 Found {len(group_list)} environment+platform+release combinations")
    
    # Debug: Find where TVGuide Loadtime and Amazon are
    with st.expander("🔍 Search for missing scenarios (entire dataset check)"):
        st.write("**NOTE: Shows data BEFORE time filtering to identify if scenarios exist elsewhere**")
        
        tvguide_all = df_before_time[df_before_time["scenario"] == "TVGuide Loadtime"]
        tvguide_filtered = df[df["scenario"] == "TVGuide Loadtime"]
        amazon_all = df_before_time[df_before_time["scenario"] == "Amazon"]
        amazon_filtered = df[df["scenario"] == "Amazon"]
        
        st.write(f"**TVGuide Loadtime:**")
        st.write(f"  - In current time filter: **{len(tvguide_filtered)} rows**")
        st.write(f"  - In full dataset (all time): **{len(tvguide_all)} rows**")
        if len(tvguide_all) > len(tvguide_filtered) and len(tvguide_all) > 0:
            st.warning(f"⚠️ TVGuide Loadtime exists but is OUTSIDE your current time range! Expand time filter to see it.")
        
        st.write(f"**Amazon:**")
        st.write(f"  - In current time filter: **{len(amazon_filtered)} rows**")
        st.write(f"  - In full dataset (all time): **{len(amazon_all)} rows**")
        if len(amazon_all) == 0:
            st.error(f"❌ Amazon scenario does NOT exist in the CSV for category '{dashboard_type}'")

    st.subheader(f"📦 Missing Scenario Grid — {dashboard_type}")

    cols_per_row = 3

    for i in range(0, len(group_list), cols_per_row):
        cols = st.columns(cols_per_row)

        for j in range(cols_per_row):
            if i + j >= len(group_list):
                continue

            (env, platform, release), group = group_list[i + j]
            ran = set(group["scenario"].dropna().astype(str).str.strip().unique())
            country = detect_country(env)
            expected = set()

            if country:
                expected = EXPECTED_SCENARIOS.get(country, {}).get(dashboard_type, set())

            missing = sorted(expected - ran)

            with cols[j]:
                with st.container(border=True):
                    st.markdown(f"### {env} + {platform} + {release}")
                    st.divider()

                    if missing:
                        for scenario in missing:
                            st.markdown(f"🔴 {scenario} → ❌ Not Run")
                    else:
                        st.success("✅ All expected scenarios executed")