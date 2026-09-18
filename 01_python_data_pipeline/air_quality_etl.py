"""
Academic exercise: monthly air-quality API -> JSON -> pandas -> CSV.

This file is a cleaned portfolio version of coursework code.
The original API credential and local paths are intentionally excluded.
"""

import json
from pathlib import Path

import pandas as pd
import requests

API_KEY = "YOUR_API_KEY"
OUT_DIR = Path("data/air_quality")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 1) Extract
for year in range(2012, 2025):
    for month in range(1, 13):
        ym = f"{year}{month:02d}"
        url = (
            "http://openAPI.seoul.go.kr:8088/"
            f"{API_KEY}/json/MonthlyAverageAirQuality/1/5/{ym}/한강대로"
        )

        response = requests.get(url, timeout=30)
        response.raise_for_status()

        with (OUT_DIR / f"output_{ym}.json").open("w", encoding="utf-8") as f:
            json.dump(response.json(), f, indent=2, ensure_ascii=False)

# 2) Transform
cols = ["MSRDT_MT", "MSRSTE_NM", "PM10"]
frames = []

for path in sorted(OUT_DIR.glob("output_*.json")):
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    rows = data["MonthlyAverageAirQuality"]["row"]
    df = pd.DataFrame(rows)[cols].copy()

    df["MSRDT_MT"] = pd.to_datetime(df["MSRDT_MT"], format="%Y%m", errors="coerce")
    df["MSRSTE_NM"] = df["MSRSTE_NM"].astype(str)
    df["PM10"] = pd.to_numeric(df["PM10"], errors="coerce")
    df = df.dropna()

    frames.append(df)

# 3) Load
merged = pd.concat(frames, ignore_index=True)
merged.to_csv(
    OUT_DIR / "merged_air_quality.csv",
    index=False,
    encoding="utf-8-sig",
)

print(merged.info())
print(merged.head())
