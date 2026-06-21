import pandas as pd
from pathlib import Path

CSV_FOLDER = Path(r"C:\projects\smartgate-downloads")
files = list(CSV_FOLDER.glob("*.csv"))
latest = max(files, key=lambda x: x.stat().st_mtime)

print(f"Reading: {latest}")
df = pd.read_csv(latest)

# Normalize columns
df.columns = df.columns.str.strip().str.lower()
if "service" in df.columns:
    df.rename(columns={"service": "scenario"}, inplace=True)

print(f"Total rows: {len(df)}")
print(f"\nColumns: {list(df.columns)}")

# Find TVGuide Loadtime
tvguide = df[df["scenario"] == "TVGuide Loadtime"]
print(f"\n=== TVGuide Loadtime ===")
print(f"Found {len(tvguide)} rows")
if len(tvguide) > 0:
    print("\nUnique combinations:")
    print(tvguide[["environmentversion", "platform", "releaseversion", "category"]].drop_duplicates().to_string())

# Find Amazon
amazon = df[df["scenario"] == "Amazon"]
print(f"\n=== Amazon ===")
print(f"Found {len(amazon)} rows")
if len(amazon) > 0:
    print("\nUnique combinations:")
    print(amazon[["environmentversion", "platform", "releaseversion", "category"]].drop_duplicates().to_string())

# Check IE_MCAST + AVSB specifically
print(f"\n=== IE_MCAST + AVSB scenarios ===")
ie_mcast = df[(df["environmentversion"].str.contains("IE_MCAST", na=False)) & 
               (df["platform"] == "AVSB")]
print(f"Total rows for IE_MCAST + AVSB: {len(ie_mcast)}")
print(f"\nUnique scenarios in IE_MCAST + AVSB (all categories):")
scenarios = ie_mcast["scenario"].dropna().unique()
print(sorted(set(scenarios)))

print(f"\nBy category in IE_MCAST + AVSB:")
for cat in ie_mcast["category"].unique():
    cat_data = ie_mcast[ie_mcast["category"] == cat]
    print(f"  {cat}: {sorted(set(cat_data['scenario'].dropna().unique()))}")
