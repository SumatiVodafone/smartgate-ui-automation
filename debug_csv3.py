import pandas as pd
from pathlib import Path

CSV_FOLDER = Path(r"C:\projects\smartgate-downloads")
files = list(CSV_FOLDER.glob("*.csv"))
latest = max(files, key=lambda x: x.stat().st_mtime)

df = pd.read_csv(latest)
df.columns = df.columns.str.strip().str.lower()
if "service" in df.columns:
    df.rename(columns={"service": "scenario"}, inplace=True)

if "time" in df.columns:
    df["time"] = pd.to_numeric(df["time"], errors="coerce")
    df["time"] = pd.to_datetime(df["time"], unit="ms", errors="coerce")

now = pd.Timestamp.now()

# Before any filtering
ie_all = df[(df["environmentversion"].str.contains("IE_MCAST", na=False)) & 
            (df["platform"] == "AVSB") &
            (df["category"] == "CT") &
            (df["releaseversion"] == "58.02+2.2405.170")]

print(f"IE_MCAST + AVSB + CT + 58.02+2.2405.170")
print(f"BEFORE time filter: {len(ie_all)} rows")
print(f"Scenarios: {sorted(set(ie_all['scenario'].dropna().unique()))}\n")

# After "Last 24 Hours" filter
ie_24h = ie_all[ie_all["time"] >= now - pd.Timedelta(hours=24)]
print(f"AFTER 'Last 24 Hours' filter (>= {now - pd.Timedelta(hours=24)}): {len(ie_24h)} rows")
print(f"Scenarios: {sorted(set(ie_24h['scenario'].dropna().unique()))}\n")

# Show TVGuide Loadtime times
tvguide_times = ie_all[ie_all["scenario"] == "TVGuide Loadtime"]["time"].values
print(f"TVGuide Loadtime timestamps: {tvguide_times}")
print(f"Current time: {now}")
print(f"\nTVGuide rows are OLDER than 24-hour cutoff!")
