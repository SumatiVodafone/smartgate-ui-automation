import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import subprocess
import base64
import re
import requests
import time
from refresh_utils import build_project, download_latest_csv, download_all_dashboards

# ---------- CONFIG ----------
JAVA_PROJECT = PROJECT_ROOT
BASE_CSV_FOLDER = PROJECT_ROOT.parent / "smartgate-downloads"


def white_card(
    title,
    body="",
    card_type="normal"
):

    border = {
        "normal": "#E5E7EB",
        "success": "#22C55E",
        "error": "#EF4444",
        "warning": "#F59E0B"
    }.get(card_type, "#E5E7EB")

    st.markdown(
        f"""
        <div style="
            background:white;
            border:1px solid #E5E7EB;
            border-left:5px solid {border};
            border-radius:14px;
            padding:16px;
            margin-bottom:16px;
            box-shadow:0 4px 12px rgba(0,0,0,.08);
            font-size:13px;
            line-height:1.7;
        ">

        <b>{title}</b><br>

        {body}

        </div>
        """,
        unsafe_allow_html=True
    )


def everything_executed_banner(selected_opco):

    country = COUNTRY_NAME.get(selected_opco, selected_opco)
    flag = COUNTRY_FLAG.get(selected_opco, "🌍")

    st.markdown(
        f"""
<div style="
background:#FFFFFF;
border:1px solid #D1FAE5;
border-left:8px solid #16A34A;
border-radius:14px;
padding:28px 36px;
margin-bottom:24px;
box-shadow:0 2px 12px rgba(0,0,0,.08);
">

<div style="
display:flex;
align-items:center;
justify-content:center;
gap:14px;
margin-bottom:8px;
">


<div>

<div style="
text-align:center;
font-size:40px;
font-weight:700;
color:#15803D;
line-height:1.2;
">
All Executions Completed ✅
</div>

<div style="
font-size:40px;
text-align:center;
font-weight:500;
color:#64748B;
margin-top:4px;
">
<span style="font-size:80px;">{flag}</span> {country}
</div>

</div>

</div>

<div style="
text-align:center;
font-size:20px;
color:#475569;
margin-top:18px;
margin-bottom:28px;
">
<b>🔥🚒 No fires to put out today...</b>

</div>

<hr style="
border:none;
border-top:1px solid #E5E7EB;
margin-bottom:24px;
">

<div style="
font-size:20px;
font-weight:600;
color:#0F172A;
margin-bottom:18px;
">

Completed Checks

</div>

<div style="
display:grid;
grid-template-columns:repeat(3,1fr);
gap:16px;
">

<div style="
padding:14px;
background:#F8FAFC;
border-radius:10px;
text-align:center;
font-weight:600;
color:#15803D;
">
✅ Device Execution
</div>

<div style="
padding:14px;
background:#F8FAFC;
border-radius:10px;
text-align:center;
font-weight:600;
color:#15803D;
">
✅ Environmental
</div>

<div style="
padding:14px;
background:#F8FAFC;
border-radius:10px;
text-align:center;
font-weight:600;
color:#15803D;
">
✅ Zapping
</div>

<div style="
padding:14px;
background:#F8FAFC;
border-radius:10px;
text-align:center;
font-weight:600;
color:#15803D;
">
✅ CT Dashboard
</div>

<div style="
padding:14px;
background:#F8FAFC;
border-radius:10px;
text-align:center;
font-weight:600;
color:#15803D;
">
✅ Long Playback
</div>

</div>

</div>
""",
        unsafe_allow_html=True,
    )

def get_base64_image(image_path):
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode()
    

DEVICE_INFORMATION_URL = (
    "https://raw.githubusercontent.com/"
    "VFTV-Testing/Configs/Main/"
    "AVSB_GEN3_Configs/deviceInformation.json"
)

SCENARIO_CONFIG_URL = (
    "https://raw.githubusercontent.com/"
    "VFTV-Testing/Configs/Main/"
    "AVSB_GEN3_Configs/Expected%26BlockedScenario"
)

@st.cache_data(ttl=21600)


def load_device_information():
    try:
        response = requests.get(DEVICE_INFORMATION_URL, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        white_card(
            f"Unable to load device information from GitHub: {e}",
            "",
            "error"
        )
        return {}

@st.cache_data(ttl=300)
def load_scenario_configuration():

    try:

        response = requests.get(
            SCENARIO_CONFIG_URL,
            timeout=15
        )

        response.raise_for_status()

        return response.json()

    except Exception as e:

        white_card(
            f"Unable to load scenario configuration: {e}",
            "",
            "error"
        )

        return {}

DEVICE_INFORMATION = load_device_information()
SCENARIO_CONFIGURATION = load_scenario_configuration()

MASTER_DEVICES = {
    device.strip().upper()
    for device in DEVICE_INFORMATION.keys()
}


def build_expected_environment_platforms(device_information):
    """
    Builds the expected hardware platforms for each environment
    from the GitHub device inventory.

    Example:
    {
        "DE_DVBC": {"AVSB", "GEN3", "GEN4_SGM"},
        "PT_MCAST": {"AVSB", "GEN3", "GEN4_SGM"}
    }
    """

    expected = {}

    for device_name, info in device_information.items():

        environment = (
            str(info.get("Country", ""))
            .strip()
            .upper()
        )

        hardware = (
            str(info.get("Hardware", ""))
            .strip()
            .upper()
        )

        if not environment or not hardware:
            continue

        expected.setdefault(environment, set()).add(hardware)

    return expected


def build_expected_environment_platform_releases(device_information):
    """
    Builds expected Hardware_Sprint combinations.

    Example:

    {
        "DE_DVBC": {
            "AVSB_45.17+2.2405.170",
            "GEN3_62.01+2.2405.170",
            "GEN4_SGM_62.01+432604.046.00120"
        }
    }
    """

    expected = {}

    for _, info in device_information.items():

        environment = (
            str(info.get("Country", ""))
            .strip()
            .upper()
        )

        hardware = (
            str(info.get("Hardware", ""))
            .strip()
            .upper()
        )

        sprint = (
            str(info.get("sprintNo", ""))
            .strip()
        )

        if not environment or not hardware or not sprint:
            continue

        platform = f"{hardware}_{sprint}"

        expected.setdefault(environment, set()).add(platform)

    return expected

def get_available_opcos(device_information):
    """
    Returns unique OPCOs.

    Example:
        AL
        CZ
        DE
        ES
        GR
        IE
        PT
    """

    opcos = set()

    for info in device_information.values():

        environment = (
            str(info.get("Country", ""))
            .strip()
            .upper()
        )

        if not environment:
            continue

        opco = environment.split("_")[0]

        opcos.add(opco)

    return sorted(opcos)

def get_devices_for_opco(selected_opco):
    return {
        device.strip().upper()
        for device, info in DEVICE_INFORMATION.items()
        if str(info.get("Country", "")).upper().startswith(selected_opco + "_")
    }


def get_environments_for_opco(selected_opco):
    return {
        str(info.get("Country", "")).strip().upper()
        for info in DEVICE_INFORMATION.values()
        if str(info.get("Country", "")).upper().startswith(selected_opco + "_")
    }
EXPECTED_SCENARIOS = {
    country: {
        dashboard: set(scenarios)
        for dashboard, scenarios in dashboards.items()
    }
    for country, dashboards in
    SCENARIO_CONFIGURATION.get(
        "ExpectedScenarios",
        {}
    ).items()
}

BLOCKED_SCENARIOS = {
    country: {
        dashboard: set(scenarios)
        for dashboard, scenarios in dashboards.items()
    }
    for country, dashboards in
    SCENARIO_CONFIGURATION.get(
        "BlockedScenarios",
        {}
    ).items()
}

EXPECTED_ZAPPING = {
    environment: set(scenarios)
    for environment, scenarios in
    SCENARIO_CONFIGURATION.get(
        "Zapping",
        {}
    ).items()
}
# Used by Zapping dashboard only
EXPECTED_ENVIRONMENT_PLATFORMS = build_expected_environment_platforms(
    DEVICE_INFORMATION
)

EXPECTED_ENVIRONMENT_PLATFORM_RELEASES = (
    build_expected_environment_platform_releases(
        DEVICE_INFORMATION
    )
)

def build_expected_inventory(device_information):
    """
    Builds the expected execution inventory from GitHub.

    Returns:

    {
        ("DE_DVBC", "GEN3", "58.01"): {
            "devices": {
                "X101-GER-PORT1-GEN3-...",
                "X102-GER-PORT2-GEN3-..."
            }
        },

        ("PT_MCAST", "GEN4_SGM", "58.01"): {
            "devices": {
                "X120-POR-PORT1-GEN4_SGM..."
            }
        }
    }
    """

    inventory = {}

    for device_name, info in device_information.items():

        environment = (
            str(info.get("Country", ""))
            .strip()
            .upper()
        )

        hardware = (
            str(info.get("Hardware", ""))
            .strip()
            .upper()
        )

        release = (
            str(info.get("sprintNo", ""))
            .strip()
        )

        if not environment or not hardware or not release:
            continue

        key = (
            environment,
            hardware,
            release
        )

        inventory.setdefault(key, set())
        inventory[key].add(device_name.strip().upper())

    return inventory

def build_actual_inventory(df):
    """
    Builds the actual execution inventory from the CSV.

    Returns:

    {
        ("DE_DVBC", "GEN3", "58.01"),
        ("PT_MCAST", "GEN4_SGM", "58.02"),
        ...
    }
    """

    if df is None or df.empty:
        return set()

    required_columns = {
        "environmentversion",
        "platform",
        "releaseversion"
    }

    if not required_columns.issubset(df.columns):
        return set()

    inventory = set()

    for _, row in df.iterrows():

        environment = (
            str(row["environmentversion"])
            .strip()
            .upper()
        )

        platform = (
            str(row["platform"])
            .strip()
            .upper()
        )

        release = (
            str(row["releaseversion"])
            .strip()
        )

        if not environment or not platform or not release:
            continue

        # Hardware is always the prefix of the platform
        hardware = (
            str(row["platform"])
            .strip()
            .upper()
        )

        inventory.add(
            (
                environment,
                hardware,
                release
            )
        )

    return inventory

EXPECTED_INVENTORY = build_expected_inventory(
    DEVICE_INFORMATION
)
AVAILABLE_OPCOS = get_available_opcos(
    DEVICE_INFORMATION
)

# ==========================================================
# OPCO Theme Colors
# ==========================================================

OPCO_THEME = {
    "DE": {
        "background": "#EAF4FF",
        "heading": "#1565C0"
    },
    "ES": {
        "background": "#FFF2E8",
        "heading": "#EF6C00"
    },
    "CZ": {
        "background": "#F3ECFF",
        "heading": "#6A1B9A"
    },
    "PT": {
        "background": "#EAFBF0",
        "heading": "#2E7D32"
    },
    "IE": {
        "background": "#E8FAF8",
        "heading": "#00897B"
    },
    "GR": {
        "background": "#EEF2FF",
        "heading": "#3949AB"
    },
    "AL": {
        "background": "#FFF0F2",
        "heading": "#C62828"
    }
}

OPCO_DISPLAY_NAME = {
    "AL": '<img src="https://flagcdn.com/24x18/al.png" width="40"> Albania',
    "CZ": '<img src="https://flagcdn.com/24x18/cz.png" width="40"> Czech Republic',
    "DE": '<img src="https://flagcdn.com/24x18/de.png" width="40"> Germany',
    "ES": '<img src="https://flagcdn.com/24x18/es.png" width="40"> Spain',
    "GR": '<img src="https://flagcdn.com/24x18/gr.png" width="40"> Greece',
    "IE": '<img src="https://flagcdn.com/24x18/ie.png" width="40"> Ireland',
    "PT": '<img src="https://flagcdn.com/24x18/pt.png" width="40"> Portugal',
}

COUNTRY_NAME = {
    "AL": "Albania",
    "CZ": "Czech Republic",
    "DE": "Germany",
    "ES": "Spain",
    "GR": "Greece",
    "IE": "Ireland",
    "PT": "Portugal",
}

COUNTRY_FLAG = {
    "AL": '<img src="https://flagcdn.com/24x18/al.png" width="40">',
    "CZ": '<img src="https://flagcdn.com/24x18/cz.png" width="40">',
    "DE": '<img src="https://flagcdn.com/24x18/de.png" width="40">',
    "ES": '<img src="https://flagcdn.com/24x18/es.png" width="40">',
    "GR": '<img src="https://flagcdn.com/24x18/gr.png" width="40">',
    "IE": '<img src="https://flagcdn.com/24x18/ie.png" width="40">',
    "PT": '<img src="https://flagcdn.com/24x18/pt.png" width="40">',
}

# ==========================================================
# Monitoring Mode State
# ==========================================================

if "current_opco_index" not in st.session_state:
    st.session_state.current_opco_index = 0

if "refresh_in_progress" not in st.session_state:
    st.session_state.refresh_in_progress = False

TECH_PATTERN = re.compile(
    r"-(DVBC|OTT|FTTH|HFC|NEBA|MCAST)$",
    re.IGNORECASE
)

def get_environment(device_name, opco):
    """
    Returns values like:
    DE_DVBC
    DE_OTT
    CZ_DVBC
    ES_HFC
    """

    if pd.isna(device_name) or pd.isna(opco):
        return None

    match = TECH_PATTERN.search(str(device_name).strip())

    if not match:
        return None

    hw_type = match.group(1).upper()

    return f"{opco}_{hw_type}"



def find_no_execution_platforms(df, selected_opco):

    no_run_cards = []

    environments = get_environments_for_opco(selected_opco)

    for environment, expected_platforms in (
        EXPECTED_ENVIRONMENT_PLATFORM_RELEASES.items()
    ):

        if environment not in environments:
            continue

        csv_platforms = set(
            df.loc[
                df["environment"] == environment,
                "platform"
            ]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        missing_platforms = sorted(
            expected_platforms - csv_platforms
        )

        for platform in missing_platforms:

            no_run_cards.append(
                (
                    environment,
                    platform
                )
            )

    return no_run_cards

CITY_TO_OPCO = {
    "Albania": "AL",
    "Dublin": "IE",
    "Lisbon": "PT",
    "Madrid": "ES",
    "Munich": "DE",
    "Unterföhring": "DE",
    "Prague": "CZ",
    "Elefsína": "GR",
}

# ==========================================================
# ALL AVAILABLE SCENARIOS (Used in Blocked Scenarios filter)
# ==========================================================

# ==========================================================
# ALL AVAILABLE SCENARIOS (CT + LongPlayback + Environmental + Zapping)
# ==========================================================

all_expected_scenarios = {
    scenario
    for country in EXPECTED_SCENARIOS.values()
    for dashboard in country.values()
    for scenario in dashboard
}
all_expected_scenarios.update(*EXPECTED_ZAPPING.values())

ALL_SCENARIOS = sorted(all_expected_scenarios)

# ==========================================================
# EMPTY PANEL PLACEHOLDER
# ==========================================================

def create_empty_panel(height):

    st.markdown(
        f"""
        <div style="
            height:{height}px;
            border-radius:10px;
            background-color:#fafafa;
            border:1px dashed #d9d9d9;
        ">
        </div>
        """,
        unsafe_allow_html=True
    )

def detect_country(env_name):
    env_upper = str(env_name).upper()
    for country in EXPECTED_SCENARIOS.keys():
        if country in env_upper:
            return country
    return None

def white_card(
    title,
    body="",
    card_type="normal"
):

    border = {
        "normal": "#E5E7EB",
        "success": "#22C55E",
        "error": "#EF4444",
        "warning": "#F59E0B"
    }.get(card_type, "#E5E7EB")

    st.markdown(
        f"""
        <div style="
            background:white;
            border:1px solid #E5E7EB;
            border-left:5px solid {border};
            border-radius:14px;
            padding:16px;
            margin-bottom:16px;
            box-shadow:0 4px 12px rgba(0,0,0,.08);
            font-size:13px;
            line-height:1.7;
        ">

        <b>{title}</b><br>

        {body}

        </div>
        """,
        unsafe_allow_html=True
    )

# ==========================================================
# RENDER DASHBOARD CARDS
# ==========================================================
def render_missing_scenario_cards(group_list, dashboard_type, cols_per_row=3, scenario_column="scenario", expected_scenarios=None):

    # ---------------------------------------------------------
    # First filter only environments having missing scenarios
    # ---------------------------------------------------------
    filtered_group_list = []

    for (env, platform, release), group in group_list:

        ran = set(
            group[scenario_column]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
        )

        country = detect_country(env)

        if expected_scenarios is not None:

            expected = expected_scenarios

        else:

            expected = set()

            if country:
                expected = EXPECTED_SCENARIOS.get(
                    country,
                    {}
                ).get(
                    dashboard_type,
                    set()
                )

        missing = sorted(
        scenario
        for scenario in (expected - ran)
        if scenario not in blocked_scenarios
        )

        # Only keep environments with missing scenarios
        if missing:
            filtered_group_list.append(
                (
                    (env, platform, release),
                    missing
                )
            )


    # ---------------------------------------------------------
    # Render cards
    # ---------------------------------------------------------
    for i in range(0, len(filtered_group_list), cols_per_row):

        cols = st.columns(cols_per_row)

        for j in range(cols_per_row):

            if i + j >= len(filtered_group_list):
                continue

            (env, platform, release), missing = filtered_group_list[i + j]

            with cols[j]:

                white_card(
                    f"{env} | {platform} | {release}",
                    ", ".join(missing)
                )

def build_dashboard(df, dashboard_name, cols_per_row):

    if df is None or df.empty:

        no_run_cards = find_ct_lpb_no_execution(
            pd.DataFrame(),   # empty dataframe
            selected_opco
        )

        if no_run_cards:

            st.markdown("##### 🚫 No Execution Found")

            for i in range(0, len(no_run_cards), cols_per_row):

                cols = st.columns(cols_per_row)

                for j in range(cols_per_row):

                    if i + j >= len(no_run_cards):
                        continue

                    environment, hardware, release = no_run_cards[i + j]

                    with cols[j]:
                        white_card(
                            f"{environment} | {hardware} | {release}",
                            "⚠ No execution found",
                            "warning"
                        )

        return

    required_columns = {
        "environmentversion",
        "platform",
        "releaseversion",
        "scenario",
    }

    missing_columns = sorted(required_columns - set(df.columns))

    if missing_columns:
        white_card(
            f"{dashboard_name} data is missing columns",
            ", ".join(missing_columns),
            "error"
        )
        return

    df = df.copy()

    groups = df.groupby(
        [
            "environmentversion",
            "platform",
            "releaseversion"
        ]
    )

    group_list = list(groups)

    no_run_cards = find_ct_lpb_no_execution(
    df,
    selected_opco
    )

    if no_run_cards:

        st.markdown("##### 🚫 No Execution Found")

        for i in range(0, len(no_run_cards), cols_per_row):

            cols = st.columns(cols_per_row)

            for j in range(cols_per_row):

                if i + j >= len(no_run_cards):
                    continue

                environment, hardware, release = no_run_cards[i + j]

                with cols[j]:

                    white_card(
                        f"{environment} | {hardware} | {release}",
                        "⚠ No execution found",
                        "warning"
                    )

    # Check if any missing scenarios exist
    has_missing = False

    for (env, platform, release), group in group_list:

        ran = set(
            group["scenario"]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
        )

        country = detect_country(env)

        expected = EXPECTED_SCENARIOS.get(
            country,
            {}
        ).get(
            dashboard_name,
            set()
        )

        missing = [
            scenario
            for scenario in (expected - ran)
            if scenario not in blocked_scenarios
        ]

        if missing:
            has_missing = True
            break

    if not has_missing and not no_run_cards:

        white_card(
            "✅ All Scenarios executed",
            "",
            "success"
        )

    else:

        render_missing_scenario_cards(
            group_list,
            dashboard_name,
            cols_per_row=cols_per_row
        )



def find_ct_lpb_no_execution(df, selected_opco):

    expected_inventory = {
        key
        for key in EXPECTED_INVENTORY.keys()
        if key[0].startswith(selected_opco + "_")
    }

    actual_inventory = build_actual_inventory(df)

    missing_inventory = sorted(
        expected_inventory - actual_inventory
    )

    return [
        (environment, hardware, release)
        for environment, hardware, release in missing_inventory
    ]

def build_environmental_dashboard(df, selected_opco):

    if df is None or df.empty:
        st.caption("No Environmental data available.")
        return

    missing_devices = check_environmental_execution(df,selected_opco)

    if not missing_devices:
        white_card(
            "✅ All devices executed Environmental scenario",
            "",
            "success"
        )
        return

    for i in range(0, len(missing_devices), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j >= len(missing_devices):
                continue
            with cols[j]:
                white_card(
                missing_devices[i+j],
                "",
                "error"
            )


def build_device_dashboard(df, selected_opco):

    if df is None or df.empty:
        st.caption("No device execution data available.")
        return

    missing_devices = check_missing_category_execution(df,selected_opco)

    if not missing_devices:
        white_card(
            "✅ All devices executed required test categories",
            "",
            "success"
        )
        return

    device_list = list(missing_devices.keys())

    for i in range(0, len(device_list), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j >= len(device_list):
                continue
            device = device_list[i + j]
            with cols[j]:
                white_card(
                device,
                "",
                "error"
)

def build_zapping_dashboard(df, selected_opco):

    if df is None or df.empty:
        st.caption("No Zapping data available.")
        return

    required_columns = [
        "platform",
        "experience"
    ]

    for column in required_columns:
        if column not in df.columns:
            white_card(
                f"{column} column not found",
                "",
                "error"
            )
            return

    df = df.copy()

    # -----------------------------------------
    # Detect which column contains city names
    # -----------------------------------------
    if (
        "cityname" in df.columns
        and df["cityname"].notna().any()
        and (df["cityname"].astype(str).str.strip() != "").any()
    ):
        city_column = "cityname"

    elif (
        "robotname" in df.columns
        and df["robotname"].notna().any()
        and (df["robotname"].astype(str).str.strip() != "").any()
    ):
        city_column = "robotname"

    else:
        white_card(
            "No column contains city information.",
            "",
            "error"
        )
        return

    df["opco"] = (
        df[city_column]
        .astype(str)
        .str.strip()
        .map(CITY_TO_OPCO)
    )

    df = df[df["opco"].notna()]

    df["environment"] = df.apply(
    lambda row: get_environment(
        # support both lowercased and original column names
        row.get("devicename", row.get("deviceName")),
        row.get("opco")
    ),
    axis=1
    )

    df = df[df["environment"].notna()]
    df = filter_by_opco(
    df,
    selected_opco,
    environment_column="environment"
    )

    # Remove invalid platform entries
    platform_series = (
        df["platform"]
        .astype(str)
        .str.strip()
    )

    df = df[
        ~(
            platform_series.isin(["GEN3", "AVSB", "GEN4","GEN4_SGM","GEN4_Mini_ZTE"]) |
            platform_series.str.startswith("Lightning", na=False)
        )
    ]

    groups = df.groupby(["environment", "platform"])

    no_run_cards = find_no_execution_platforms(
    df,
    selected_opco
    )
    group_list = []

    for (environment, platform), group in groups:

        ran = set(
            group["experience"]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
        )

        expected = EXPECTED_ZAPPING.get(environment, set())

        missing = sorted(
            scenario
            for scenario in (expected - ran)
            if scenario not in blocked_scenarios
        )

        if missing:
            group_list.append(
                (
                    (environment, platform, ""),
                    pd.DataFrame({"scenario": missing})
                )
            )

    if not group_list and not no_run_cards:
        white_card(
            "✅ All Zapping scenarios executed",
            "",
            "success"
)
        return

    for i in range(0, len(no_run_cards), 3):

        cols = st.columns(3)

        for j in range(3):

            if i + j >= len(no_run_cards):
                continue

            environment, platform = no_run_cards[i + j]

            with cols[j]:

                white_card(
                    f"{environment} | {platform}",
                    "⚠ No execution found",
                    "warning"
                )

    for i in range(0, len(group_list), 3):

        cols = st.columns(3)

        for j in range(3):

            if i + j >= len(group_list):
                continue

            (environment, platform, _), missing_df = group_list[i + j]

            with cols[j]:

                white_card(
                   f"{environment} | {platform}",
                    ", ".join(missing_df["scenario"])
                )
def is_dashboard_perfect(
    no_execution_devices,
    environmental_devices,
    ct_df,
    lpb_df,
    zap_master_df,
    selected_opco,
):
    """
    Returns True only if every dashboard is completely green.
    """

    # -------------------------------------------------
    # No Device Execution
    # -------------------------------------------------
    if len(no_execution_devices) > 0:
        return False

    # -------------------------------------------------
    # Environmental
    # -------------------------------------------------
    if len(environmental_devices) > 0:
        return False

    # -------------------------------------------------
    # Zapping
    # -------------------------------------------------
    if zap_master_df is not None:

        required_columns = {"platform", "experience"}

        if required_columns.issubset(zap_master_df.columns):

            temp = zap_master_df.copy()

            if (
                "cityname" in temp.columns
                and temp["cityname"].notna().any()
            ):
                city_column = "cityname"

            elif (
                "robotname" in temp.columns
                and temp["robotname"].notna().any()
            ):
                city_column = "robotname"

            else:
                return False

            temp["opco"] = (
                temp[city_column]
                .astype(str)
                .str.strip()
                .map(CITY_TO_OPCO)
            )

            temp["environment"] = temp.apply(
                lambda row: get_environment(
                    row.get("devicename", row.get("deviceName")),
                    row.get("opco")
                ),
                axis=1
            )

            temp = filter_by_opco(
                temp,
                selected_opco,
                environment_column="environment"
            )

            # Apply the same filtering as the Zapping dashboard
            platform_series = (
                temp["platform"]
                .astype(str)
                .str.strip()
            )

            temp = temp[
                ~(
                    platform_series.isin([
                        "GEN3",
                        "AVSB",
                        "GEN4",
                        "GEN4_SGM",
                        "GEN4_Mini_ZTE"
                    ]) |
                    platform_series.str.startswith(
                        "Lightning",
                        na=False
                    )
                )
            ]

            no_run_cards = find_no_execution_platforms(
                temp,
                selected_opco
            )

            if no_run_cards:
                return False

            groups = temp.groupby(["environment", "platform"])

            for (environment, platform), group in groups:

                ran = set(
                    group["experience"]
                    .dropna()
                    .astype(str)
                    .str.strip()
                    .unique()
                )

                expected = EXPECTED_ZAPPING.get(
                    environment,
                    set()
                )

                missing = [
                    scenario
                    for scenario in (expected - ran)
                    if scenario not in blocked_scenarios
                ]

                if missing:
                    return False

    # -------------------------------------------------
    # CT & Long Playback
    # -------------------------------------------------
    for dashboard_name, dashboard_df in [
        ("CT", ct_df),
        ("LongPlayback", lpb_df),
    ]:

        no_run = find_ct_lpb_no_execution(
            dashboard_df,
            selected_opco
        )

        if no_run:
            return False

        if dashboard_df is None:
            continue

        groups = dashboard_df.groupby(
            [
                "environmentversion",
                "platform",
                "releaseversion",
            ]
        )

        for (env, platform, release), group in groups:

            ran = set(
                group["scenario"]
                .dropna()
                .astype(str)
                .str.strip()
                .unique()
            )

            country = detect_country(env)

            expected = (
                EXPECTED_SCENARIOS
                .get(country, {})
                .get(dashboard_name, set())
            )

            missing = [
                scenario
                for scenario in (expected - ran)
                if scenario not in blocked_scenarios
            ]

            if missing:
                return False

    return True


def prepare_ct_dashboard_dataframe(df, dashboard_name):

    if df is None or df.empty:
        return None

    if "category" not in df.columns:
        white_card(
            "Category column not found",
            "",
            "error"
        )
        return None

    dashboard_df = df[df["category"] == dashboard_name].copy()

    if len(dashboard_df) == 0:
        return None

    return dashboard_df

def filter_by_opco(
    df,
    selected_opco,
    environment_column="environmentversion"
):
    """
    Returns only rows belonging to the selected OPCO.

    Example:
        selected_opco = "DE"

    Keeps:
        DE_DVBC
        DE_OTT

    Removes:
        CZ_DVBC
        PT_MCAST
    """

    if df is None or df.empty:
        return df

    if selected_opco is None:
        return df

    if environment_column not in df.columns:
        return df

    return df[
        df[environment_column]
        .astype(str)
        .str.upper()
        .str.startswith(selected_opco + "_")
    ].copy()

st.set_page_config(page_title="Smartgate Dashboard", layout="wide")

TOP_PANEL_HEIGHT = 420
BOTTOM_PANEL_HEIGHT = 180

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
    min-height:34px !important;
    height:34px !important;
    border-radius:6px !important;
    font-size:13px !important;
    padding:0px 6px !important;
    font-weight: 500 !important;
    background-color: white !important;
    box-shadow: none !important;
}

[data-testid="stWidgetLabel"] {

    font-size:13px !important;
}

/* Selected dropdown text */
div[data-baseweb="select"] span {
    font-size: 13px !important;
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
     height:34px !important;
    min-height:34px !important;
    padding:0px 10px !important;
    font-size:13px !important;
    font-weight:600 !important;
    border-radius:6px !important;
    font-weight: 600 !important;
    color: #2563eb !important;
    background-color: white !important;
}
            
/* Blocked scenario tags */
div[data-baseweb="tag"] {

    font-size: 12px !important;

    padding: 1px 4px !important;

    min-height: 22px !important;
}

/* Page spacing */
.block-container {
    padding-top: 2rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* White Cards */
.white-card{background:#fff;border:1px solid #E5E7EB;border-radius:10px;padding:12px;margin-bottom:10px;box-shadow:0 2px 6px rgba(0,0,0,.05);}
.white-card.success{border-left:4px solid #22C55E;color:#15803D;}
.white-card.error{border-left:4px solid #EF4444;}
.white-card.warning{border-left:4px solid #F59E0B;}
</style>
""", unsafe_allow_html=True)

def get_csv_folder(dashboard_type):
    if dashboard_type == "Zapping":
        return BASE_CSV_FOLDER / "Zapping"

    elif dashboard_type in ["Environmental", "No Device Execution"]:
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

def load_all_csvs():
    # Load latest CSVs and normalize column names for consistent access
    ct = load_latest_csv("CT")
    env = load_latest_csv("Environmental")
    zap = load_latest_csv("Zapping")

    def _normalize(df):
        if df is None:
            return None
        df.columns = df.columns.str.strip().str.lower()
        if "service" in df.columns:
            df.rename(columns={"service": "scenario"}, inplace=True)
        if "time" in df.columns:
            df["time"] = pd.to_datetime(df["time"], errors="coerce")
        return df

    return {
        "ct_master_df": _normalize(ct),
        "env_master_df": _normalize(env),
        "zap_master_df": _normalize(zap),
    }

def normalize_device_name(name):
    return str(name).strip().upper()

def check_environmental_execution(df, selected_opco):

    devices = get_devices_for_opco(selected_opco)

    if "devicename" not in df.columns:
        white_card(
            "deviceName column not found in CSV",
            "",
            "error"
        )
        st.stop()

    if "scenarioname" not in df.columns:
        white_card(
            "scenarioName column not found in CSV",
            "",
            "error"
        )
        st.stop()

    df = df.copy()

    df["devicename"] = df["devicename"].astype(str).str.strip().str.upper()
    df["scenarioname"] = df["scenarioname"].astype(str).str.strip().str.upper()

    scenario_df = df[
        df["scenarioname"] == "CHECK_MAINTENANCE_DATA_IN_SETTINGS"
    ]

    missing_devices = []

    for device in devices:
        if device not in set(scenario_df["devicename"]):
            missing_devices.append(device)

    return sorted(missing_devices)

    


def check_missing_category_execution(df, selected_opco):
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()
    devices = get_devices_for_opco(selected_opco)
    if "devicename" not in df.columns:
        white_card(
            "deviceName column not found in CSV",
            "",
            "error"
        )
        st.stop()

    if "category" not in df.columns:
        white_card(
            "category column not found in CSV",
            "",
            "error"
        )
        st.stop()

    df["devicename"] = df["devicename"].apply(normalize_device_name)
    df["category"] = df["category"].astype(str).str.strip()

    required_categories = {"CT", "Environmental", "LongPlayback"}

    results = {}

    for device in devices:
        device_categories = set(
            df[df["devicename"] == device]["category"].unique()
        )

        missing = required_categories - device_categories

        if missing:
            results[device] = sorted(missing)

    return results


logo_path = APP_DIR / "witbe_logo.png"
logo = get_base64_image(logo_path)

# ---------- HEADER ----------
col_logo, col_title = st.columns([0.35, 12])

with col_logo:
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.image(logo_path, width=35)

with col_title:
    title_placeholder = st.empty()


# ==========================================================
# TOP FILTER BAR
# ==========================================================

col1, col2, col3, col4, col5, col6, col7 = st.columns(
    [2.0, 1.7, 2.0, 3.0, 2.0, 1.5, 1.5]
)

if st.session_state.refresh_in_progress:
    st.caption("Refreshing dashboard data. Please wait...")

with col1:
    dashboard_type = st.selectbox(
        "Dashboard Type",
        [
            "All",
            "No Device Execution",
            "Environmental",
            "Zapping",
            "CT Dashboard",
            "Long Playback"
        ],
        key="dashboard_type"
    )

with col2:
    if dashboard_type in ["Environmental", "No Device Execution"]:
        time_filter = st.selectbox(
            "Time Filter",
            ["Last 24 Hours"],
            key="time_filter"
        )
    else:
        time_filter = st.selectbox(
            "Time Filter",
            [
                "Last 24 Hours",
                "Last 2 Days",
                "Last 7 Days",
                "Last 15 Days",
                "Last 30 Days",
                "Custom Range"
            ],
            key="time_filter"
        )


with col3:

    monitoring_mode = st.toggle(
        "🔄 Monitoring Mode",
        value=True,
        help="Automatically rotates through OPCOs."
    )

    if monitoring_mode:
        refresh_interval = st.selectbox(
            "Refresh Interval (sec)",
            [5, 10, 15, 30, 60],
            index=0,
            key="refresh_interval"
        )
    else:
        refresh_interval = 5


with col4:

    blocked_scenarios = st.multiselect(
        "Blocked Scenarios",
        options=ALL_SCENARIOS,
        default=[],
        placeholder="Select blocked scenarios..."
    )

with col5:

    blocked_opcos = st.multiselect(
        "Blocked OPCOs",
        options=AVAILABLE_OPCOS,
        default=[],
        key="blocked_opcos",
        placeholder="Select blocked OPCOs..."
    )

blocked_opcos = set(blocked_opcos)

available_opcos = [
    opco
    for opco in AVAILABLE_OPCOS
    if opco not in blocked_opcos
]

if not available_opcos:
    white_card(
        "All OPCOs are blocked.",
        "Please unblock at least one OPCO.",
        "warning"
    )
    st.stop()

if st.session_state.current_opco_index >= len(available_opcos):
    st.session_state.current_opco_index = 0

if monitoring_mode:

    st_autorefresh(
        interval=refresh_interval * 1000,
        key="monitor_refresh"
    )

# Current OPCO selected for monitoring
if monitoring_mode:
    current_index = min(
        st.session_state.current_opco_index,
        len(available_opcos) - 1
    )

    selected_opco = available_opcos[current_index]
else:
    selected_opco = st.selectbox(
        "Select OPCO",
        available_opcos,
        key="manual_opco"
    )


theme = OPCO_THEME.get(
    selected_opco,
    {
        "background": "#FFFFFF",
        "heading": "#1F2937"
    }
)

display_country = OPCO_DISPLAY_NAME.get(
    selected_opco,
    selected_opco
)

title_placeholder.html(
    f"""
    <div style="
        display:flex;
        align-items:center;
        gap:12px;
        margin-top:18px;
    ">

        <div style="
            font-size:28px;
            font-weight:700;
            color:#0b1020;
        ">
            Smartgate Execution Dashboard
        </div>

        <div style="
            background:{theme['heading']};
                color:white;
                padding:6px 16px;
                border-radius:16px;
                font-size:32px;
                font-weight:700;
                line-height:26px;
                min-width:48px;
                text-align:center;
        ">
            {display_country}
        </div>

    </div>
    """
)

st.markdown(
    f"""
    <style>
    .stApp {{
        background: white;
    }}

    .block-container {{
        background: {theme['background']};
        border-radius:16px;
        padding:20px !important;
        transition: background-color .6s ease;
    }}

    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background:white;
        border-radius:10px;
        box-shadow:0 2px 8px rgba(0,0,0,.08);
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================================
# Monitoring Mode Auto Rotation
# ==========================================================

if (
    monitoring_mode
    and
    not st.session_state.refresh_in_progress
    ):

    current_time = time.time()

    if "last_rotation_time" not in st.session_state:
        st.session_state.last_rotation_time = current_time

    elapsed = current_time - st.session_state.last_rotation_time

    if elapsed >= refresh_interval:

        st.session_state.current_opco_index = (
            st.session_state.current_opco_index + 1
        ) % len(available_opcos)

        st.session_state.last_rotation_time = current_time

        st.rerun()



with col6:  
    refresh_clicked = st.button(
        "🔄 Refresh Selected Dashboard",
        use_container_width=True,
        key="refresh_button",
        disabled=st.session_state.refresh_in_progress
    )

with col7:
    refresh_all_clicked = st.button(
        "🚀 Refresh All Dashboards",
        use_container_width=True,
        key="refresh_all_button",
        disabled=st.session_state.refresh_in_progress
    )


if refresh_clicked:

    if build_project():
        download_latest_csv(csv_dashboard)
        st.rerun()

if refresh_all_clicked:

    st.session_state.refresh_in_progress = True

    download_all_dashboards()

    st.session_state.refresh_in_progress = False

    st.rerun()

# ---------- LOAD ALL CSVs ----------

all_csvs = load_all_csvs()

ct_master_df = all_csvs["ct_master_df"]
env_master_df = all_csvs["env_master_df"]
zap_master_df = all_csvs["zap_master_df"]

# Normalize column names for any CSV that was found.
for master_df in (ct_master_df, env_master_df, zap_master_df):
    if master_df is not None:
        master_df.columns = (
            master_df.columns
            .str.strip()
            .str.lower()
        )
if dashboard_type == "All":
    csv_dashboard = "CT"

elif dashboard_type == "CT Dashboard":
    csv_dashboard = "CT"

elif dashboard_type == "Long Playback":
    csv_dashboard = "LongPlayback"

elif dashboard_type == "Environmental":
    csv_dashboard = "Environmental"

elif dashboard_type == "No Device Execution":
    csv_dashboard = "No Device Execution"

elif dashboard_type == "Zapping":
    csv_dashboard = "Zapping"

# ---------- LOAD LATEST CSV ----------
df = load_latest_csv(csv_dashboard)
ct_df = None
lpb_df = None
env_df = None

if df is None:
    white_card(
    "No CSV found",
    "Click Refresh Data",
    "warning"
    )
    st.stop()

# ---------- CLEAN COLUMN NAMES ----------
df.columns = df.columns.str.strip().str.lower()

if "service" in df.columns:
    df.rename(columns={"service": "scenario"}, inplace=True)

if "time" in df.columns:
    df["time"] = pd.to_datetime(df["time"], errors="coerce")


# ---------- CUSTOM DATE RANGE ----------

if time_filter == "Custom Range":

    left, right = st.columns(2)

    with left:
        start_date = st.date_input("Start Date")
        start_time = st.time_input("Start Time")

    with right:
        end_date = st.date_input("End Date")
        end_time = st.time_input("End Time")

if dashboard_type == "No Device Execution":
    st.subheader("Devices Without Test Execution")

    missing_execution = check_missing_category_execution(
    df,
    selected_opco
)

    if not missing_execution:
        white_card(
            "✅ All devices have execution in CT, Environmental and LongPlayback",
            "",
            "success"
        )
    else:
        white_card(
            "❌ Devices with incomplete execution coverage",
            "",
            "error"
        )

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

    missing_devices = check_environmental_execution(
    df,
    selected_opco
    )

    if not missing_devices:
        white_card(
            "✅ Check_Maintenance_Data_In_Settings has run on all devices",
            "",
            "success"
        )
    else:
        white_card(
            "❌ Devices with no Environmental execution",
            "",
            "error"
        )

        result_df = pd.DataFrame({
            "Device Name": missing_devices
        })

        st.dataframe(result_df, use_container_width=True)

    st.stop()

elif dashboard_type == "Zapping":
    st.subheader("📦 Missing Zapping Scenarios")
    build_zapping_dashboard(
        df,
        selected_opco
    )
    st.stop()

else:
    if "category" not in df.columns:
        white_card(
            "Category column not found",
            "",
            "error"
        )
        st.stop()

    # BEFORE time filtering - check what's available
    df_before_time = df[df["category"] == csv_dashboard].copy()
    
    # ----------------------------------------------------------
    # Apply OPCO filter once to the master dataframe
    # ----------------------------------------------------------
    filtered_master_df = filter_by_opco(
        df,
        selected_opco
    )

    # AFTER time filtering + OPCO filtering
    ct_df = prepare_ct_dashboard_dataframe(
        filtered_master_df,
        "CT"
    )

    lpb_df = prepare_ct_dashboard_dataframe(
        filtered_master_df,
        "LongPlayback"
    )

    env_df = prepare_ct_dashboard_dataframe(
        env_master_df,
        "Environmental"
    )

    if len(df) == 0:
        white_card(
            f"❌ No data found for category: {dashboard_type}",
            "",
            "error"
        )
        st.stop()

    
# ==========================================================
# DASHBOARD GRID LAYOUT
# ==========================================================

left, right = st.columns(2)

no_execution_devices = check_missing_category_execution(
    env_master_df,
    selected_opco
)

environmental_devices = check_environmental_execution(
    env_master_df,
    selected_opco
)

everything_executed = is_dashboard_perfect(
    no_execution_devices,
    environmental_devices,
    ct_df,
    lpb_df,
    zap_master_df,
    selected_opco,
)

# -------------------------------------------------
# TEMPORARY - Force Everything Executed (Testing)
# -------------------------------------------------


if dashboard_type == "All" and everything_executed:
    everything_executed_banner(selected_opco)

else:

    left, right = st.columns(2)

    no_execution_count = len(no_execution_devices)
    environmental_count = len(environmental_devices)

    no_execution_title = (
        f"### 📱 No Device Execution ({no_execution_count} "
        f"{'Device' if no_execution_count == 1 else 'Devices'})"
    )

    environmental_title = (
        f"### 🌍 Environmental ({environmental_count} "
        f"{'Device' if environmental_count == 1 else 'Devices'})"
    )

    # Move ALL of your existing dashboard rendering code here

    if dashboard_type in ["All","No Device Execution"]:
        with left:
            st.markdown(f"<h3 style='color:{theme['heading']};margin-bottom:8px;'>{no_execution_title.replace('### ','')}</h3>", unsafe_allow_html=True)
            build_device_dashboard(env_master_df, selected_opco)

    if dashboard_type in ["All","Environmental"]:
        with right:
            st.markdown(f"<h3 style='color:{theme['heading']};margin-bottom:8px;'>{environmental_title.replace('### ','')}</h3>", unsafe_allow_html=True)
            build_environmental_dashboard(env_master_df, selected_opco)

    st.markdown(f"<hr style='border:1px solid {theme['heading']}33;margin-top:8px;margin-bottom:8px;'>", unsafe_allow_html=True)

    if dashboard_type in ["All","Zapping"]:
        st.markdown(f"<h3 style='color:{theme['heading']};margin-bottom:8px;'>⚡ Zapping</h3>", unsafe_allow_html=True)
        build_zapping_dashboard(zap_master_df, selected_opco)

    st.markdown(f"<hr style='border:1px solid {theme['heading']}33;margin-top:8px;margin-bottom:8px;'>", unsafe_allow_html=True)

    if dashboard_type in ["All","CT Dashboard"]:
        st.markdown(f"<h3 style='color:{theme['heading']};margin-bottom:8px;'>📺 CT Dashboard</h3>", unsafe_allow_html=True)
        build_dashboard(
            ct_df if ct_df is not None else pd.DataFrame(),
            "CT",
            cols_per_row=3
        )

    st.markdown(f"<hr style='border:1px solid {theme['heading']}33;margin-top:8px;margin-bottom:8px;'>", unsafe_allow_html=True)

    if dashboard_type in ["All","Long Playback"]:
        st.markdown(f"<h3 style='color:{theme['heading']};margin-bottom:8px;'>▶️ Long Playback</h3>", unsafe_allow_html=True)
        if lpb_df is not None:
            build_dashboard(lpb_df, "LongPlayback", cols_per_row=3)

# ==========================================================
# BLOCKED SCENARIOS
# ==========================================================

st.markdown(
    f"<hr style='border:1px solid {theme['heading']}33;margin-top:8px;margin-bottom:8px;'>",
    unsafe_allow_html=True
)

st.markdown(
    f"<h3 style='color:{theme['heading']};margin-bottom:8px;'>🚫 Blocked Scenarios</h3>",
    unsafe_allow_html=True
)

blocked_data = BLOCKED_SCENARIOS.get(selected_opco, {})

cols = st.columns(3)

dashboard_names = [
    "CT",
    "LongPlayback",
    "Environmental"
]

for i, dashboard in enumerate(dashboard_names):

    scenarios = sorted(
        blocked_data.get(dashboard, set())
    )

    body = (
        "<br>".join(scenarios)
        if scenarios
        else "No blocked scenarios"
    )

    with cols[i]:

        white_card(
            dashboard,
            body
        )
