import pandas as pd
from pathlib import Path

CSV_FOLDER = Path(r"C:\projects\smartgate-downloads")
files = list(CSV_FOLDER.glob("*.csv"))
latest = max(files, key=lambda x: x.stat().st_mtime)

df = pd.read_csv(latest)
df.columns = df.columns.str.strip().str.lower()
if "service" in df.columns:
    df.rename(columns={"service": "scenario"}, inplace=True)

# Check time parsing
if "time" in df.columns:
    df["time"] = pd.to_numeric(df["time"], errors="coerce")
    df["time"] = pd.to_datetime(df["time"], unit="ms", errors="coerce")

# Get IE_MCAST + AVSB + CT TVGuide Loadtime rows
ie_tvguide = df[(df["environmentversion"].str.contains("IE_MCAST", na=False)) & 
                 (df["platform"] == "AVSB") &
                 (df["category"] == "CT") &
                 (df["scenario"] == "TVGuide Loadtime")]

print(f"IE_MCAST + AVSB + CT + TVGuide Loadtime rows: {len(ie_tvguide)}")
print("\nTimestamps for these rows:")
print(ie_tvguide[["environmentversion", "releaseversion", "time"]].to_string())

# Check current time
now = pd.Timestamp.now()
print(f"\n\nCurrent time: {now}")
print(f"Last 24 hours: {now - pd.Timedelta(hours=24)}")

# Filter by last 24 hours
ie_tvguide_24h = ie_tvguide[ie_tvguide["time"] >= now - pd.Timedelta(hours=24)]
print(f"\nRows in last 24 hours: {len(ie_tvguide_24h)}")

# Check IE_MCAST + AVSB + CT all scenarios with times
print(f"\n\n=== IE_MCAST + AVSB + CT by time range ===")
ie_all = df[(df["environmentversion"].str.contains("IE_MCAST", na=False)) & 
            (df["platform"] == "AVSB") &
            (df["category"] == "CT")]
print(f"Total CT rows: {len(ie_all)}")
print(f"Time range: {ie_all['time'].min()} to {ie_all['time'].max()}")

# Group by releaseversion
print(f"\nGrouped by releaseversion:")
for rv in ie_all["releaseversion"].unique():
    rv_data = ie_all[ie_all["releaseversion"] == rv]
    scenarios = set(rv_data["scenario"].dropna().unique())
    has_tvguide = "TVGuide Loadtime" in scenarios
    times = rv_data["time"].unique()
    print(f"  {rv}: {len(rv_data)} rows, TVGuide={has_tvguide}, time range: {min(times)} to {max(times)}")
