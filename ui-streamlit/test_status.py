import pandas as pd
import glob, os, re

CSV_FOLDER = r"C:/projects/smartgate-downloads"

files = sorted(glob.glob(os.path.join(CSV_FOLDER, "*.csv")), key=lambda x: -os.path.getmtime(x))
if not files:
    print("No CSV found")
    raise SystemExit(1)

df = pd.read_csv(files[0])
print("Loaded:", files[0])
print("Columns:", list(df.columns))

MASTER_SERVICES = {
    "ct": [
        "Amazon", "Catchup", "DAZN", "Disney", "Guide_Navigation", "HBO", "Media Library",
        "MiniPI To ExtendedPI", "Netflix", "Pause_Resume", "Random_Zapping", "Rewind_Playback",
        "StartOver", "TLM Launch Via Hotkey", "TLM_Navigation", "TVGuide Loadtime",
        "Tune Live TV Via TVGuide", "Tune Live TV Via TVGuide_GR_DTT",
        "Tune Live TV Via TVGuide_GR_MCAST_To_DTT", "VOD", "Wakeup From Standby",
        "Youtube", "nPVR"
    ],
    "environmental": [
        "BT Validation", "Device Health Status", "Network Validation",
        "Technical & System Integration"
    ],
    "longplayback": [
        "Amazon", "Catchup", "Disney", "HBO", "Live", "Netflix", "VOD", "Youtube", "nPVR"
    ]
}


def _norm(text):
    if text is None:
        return ""
    t = str(text).strip().lower()
    t = t.replace("_", " ")
    t = re.sub(r"[^a-z0-9 ]+", "", t)
    t = re.sub(r"\s+", " ", t)
    return t

present = set(_norm(s) for s in df['service'].astype(str).dropna().unique())
print('\nPresent (normalized):')
for p in sorted(list(present))[:50]:
    print(' -', p)

for cat, services in MASTER_SERVICES.items():
    print(f"\nCategory: {cat}")
    for s in services:
        ns = _norm(s)
        match = ns in present or any(ns in p or p in ns for p in present)
        print(f" {s:35} -> {'✅' if match else '❌'}")
