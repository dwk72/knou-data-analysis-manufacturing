"""
Academic exercise: monthly energy-use API -> JSON -> pandas integration.

Portfolio version based on KNOU open-source data-analysis coursework.
Credential-bearing URL details are replaced with placeholders.
"""

import json
from pathlib import Path

import pandas as pd
import requests

API_URL = "YOUR_API_ENDPOINT"
OUT_DIR = Path("data/energy_use")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 1) Extract: collect monthly data
for year in range(2015, 2025):
    for month in range(1, 13):
        response = requests.get(
            API_URL,
            params={"year": year, "month": f"{month:02d}", "TYPE": "json"},
            timeout=30,
        )
        response.raise_for_status()

        with (OUT_DIR / f"output_{year}-{month:02d}.json").open(
            "w", encoding="utf-8"
        ) as f:
            json.dump(response.json(), f, indent=2, ensure_ascii=False)

# 2) Transform / integrate
cols = ["YEAR", "MON", "MM_TYPE", "EUS", "GUS", "WUS", "HUS"]
frames = []

for path in sorted(OUT_DIR.glob("output_*.json")):
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    rows = data["energyUseDataSummaryInfo"]["row"]
    df = pd.DataFrame(rows)

    df = df[df["MM_TYPE"] == "개인"][cols].copy()

    for col in ["EUS", "GUS", "WUS", "HUS"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    frames.append(df)

merged = pd.concat(frames, ignore_index=True)
merged.to_csv(
    OUT_DIR / "merged_energy_use.csv",
    index=False,
    encoding="utf-8-sig",
)

print(merged.info())
print(merged.head())
