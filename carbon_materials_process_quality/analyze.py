"""Activated-carbon manufacturing-oriented data quality and baseline EDA.

Source: University of Nottingham / Nanolayers, Zenodo v2
https://zenodo.org/records/23311682, DOI 10.5281/zenodo.23311682.
The source CSV is not redistributed; only aggregated results and SVG charts.
This does not claim plant validation, an optimal recipe, or causal effects.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import time
import urllib.request
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

RECORD_URL = "https://zenodo.org/records/23311682"
FILE_NAME = "mast3rboost-AC-UON.csv"
EXPECTED_MD5 = "0e38bd5c6a66dc8ff62f5831a90b55b0"
DOWNLOAD_URLS = (
    RECORD_URL + "/files/" + FILE_NAME + "?download=1",
    "https://zenodo.org/api/records/23311682/files/" + FILE_NAME + "/content",
)
BET = "[ouptut] ABET"  # Original publisher header typo
TEMP = "[input] Activation_temperature"
KC = "[input] K/C"
DR = "[output] DR_volume"
MICRO = "[output] nldft_Vmicro"
H2 = "[output] n_100bar"
REQUIRED = ("ID", BET, TEMP, KC, DR, MICRO, H2)
GROUPS = ("Literature", "MAST3RBoost")


def verify_md5(content: bytes) -> None:
    digest = hashlib.md5(content).hexdigest()
    if digest != EXPECTED_MD5:
        raise ValueError("Original Zenodo v2 MD5 mismatch: " + digest)


def fetch_source() -> bytes:
    errors = []
    for url in DOWNLOAD_URLS:
        for attempt in range(2):
            try:
                request = urllib.request.Request(
                    url,
                    headers={"User-Agent": "Mozilla/5.0 carbon-data-research", "Accept": "*/*"},
                )
                with urllib.request.urlopen(request, timeout=45) as response:
                    content = response.read()
                verify_md5(content)
                return content
            except Exception as exc:
                errors.append(str(exc))
                if attempt == 0:
                    time.sleep(2)
    raise RuntimeError("Cannot fetch unchanged Zenodo source: " + "; ".join(errors))


def parse_csv(text: str) -> pd.DataFrame:
    lines = text.splitlines()
    if len(lines) < 3:
        raise ValueError("Missing source rows")
    header = [x.strip() for x in lines[0].split(";")]
    if len(header) != 34 or any(k not in header for k in REQUIRED):
        raise ValueError("Unexpected source schema")
    if "m^2/g" not in lines[1]:
        raise ValueError("Expected source units row not found")
    cleaned = [lines[0].strip()]
    for line in lines[2:]:
        if not line.strip():
            continue
        fields = [x.strip() for x in line.split(";")]
        if len(fields) == len(header) + 1 and fields[-1] == "":
            fields.pop()  # Publisher CSV has a trailing delimiter
        if len(fields) != len(header):
            raise ValueError("Source row field count mismatch")
        cleaned.append(";".join(fields))
    df = pd.read_csv(io.StringIO("\n".join(cleaned)), sep=";", dtype={"ID": str})
    if len(df) != 237 or df["ID"].nunique() != 237 or df["ID"].isna().any():
        raise ValueError("Source grain changed: expected 237 unique material IDs")
    # Official record describes ordered first 188 literature + last 49 new samples.
    df["source_group"] = ["Literature"] * 188 + ["MAST3RBoost"] * 49
    for key in df.columns:
        if key not in ("ID", "source_group"):
            df[key] = pd.to_numeric(df[key], errors="coerce")
    return df


def profile(df: pd.DataFrame) -> dict:
    out = {
        "source_url": RECORD_URL,
        "source_doi": "10.5281/zenodo.23311682",
        "source_license": "CC BY-ND 2.5",
        "raw_file_republished": False,
        "source_md5": EXPECTED_MD5,
        "samples": int(len(df)),
        "source_columns": 34,
        "unique_ids": int(df["ID"].nunique()),
        "cohorts": {},
    }
    for group in GROUPS:
        sub = df[df.source_group == group]
        measured = sub[BET].dropna()
        out["cohorts"][group] = {
            "samples": int(len(sub)),
            "bet_observed": int(measured.size),
            "bet_missing": int(sub[BET].isna().sum()),
            "bet_mean_m2_g": round(float(measured.mean()), 2) if len(measured) else None,
            "bet_median_m2_g": round(float(measured.median()), 2) if len(measured) else None,
            "coverage": {
                label: int(sub[col].notna().sum())
                for label, col in (
                    ("BET", BET), ("DR_volume", DR), ("NLDFT_micropore", MICRO),
                    ("H2_uptake", H2),
                )
            },
        }
    return out


def plot(df: pd.DataFrame, directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "svg.hashsalt": "carbon-eda-v1",
        "font.size": 10,
    })
    colors = {"Literature": "#8464B9", "MAST3RBoost": "#23818A"}
    fig, ax = plt.subplots(figsize=(9, 5))
    for group in GROUPS:
        valid = df[df.source_group == group][[TEMP, BET]].dropna()
        ax.scatter(valid[TEMP], valid[BET], label=group + " (n=" + str(len(valid)) + ")",
                   color=colors[group], alpha=0.68, s=30)
    ax.set(xlabel="Activation temperature (reported °C)", ylabel="BET surface area (m²/g)",
           title="Activated carbon: reported temperature vs BET")
    ax.legend()
    ax.grid(alpha=0.20)
    fig.text(0.5, 0.015, "Nottingham/Nanolayers, Zenodo v2. Research data, not a production time series.",
             ha="center", fontsize=8)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(directory / "temperature_vs_bet.svg", format="svg", metadata={"Date": None})
    plt.close(fig)

    features = (("BET", BET), ("DR volume", DR), ("NLDFT micro V", MICRO),
                ("H2 uptake", H2))
    fig, ax = plt.subplots(figsize=(9, 5))
    width = 0.36
    for offset, group in ((-width / 2, "Literature"), (width / 2, "MAST3RBoost")):
        sub = df[df.source_group == group]
        values = [100 * sub[col].notna().mean() for _, col in features]
        ax.bar([j + offset for j in range(len(features))], values, width=width,
               color=colors[group], label=group)
    ax.set_xticks(range(len(features)), [name for name, _ in features])
    ax.set_ylim(0, 110)
    ax.set(ylabel="Measurements available (%)", title="Data coverage by study cohort")
    ax.grid(axis="y", alpha=0.2)
    ax.legend()
    fig.text(0.5, 0.015, "Missing measurements are often structural, not randomly unrecorded.",
             ha="center", fontsize=8)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(directory / "coverage_by_cohort.svg", format="svg", metadata={"Date": None})
    plt.close(fig)


def report(result: dict) -> str:
    a, b = result["cohorts"]["Literature"], result["cohorts"]["MAST3RBoost"]
    return "\n".join([
        "# 활성탄 제조조건·물성 데이터: 기초 분석 결과",
        "",
        "자료: University of Nottingham / Nanolayers, Zenodo v2, DOI 10.5281/zenodo.23311682.",
        "원본 데이터 이용조건: CC BY-ND 2.5. 이 저장소는 원본 CSV를 재배포하지 않습니다.",
        "",
        "## 시료·측정 범위 확인",
        "",
        "- 관측 단위: 활성탄 시료 237개 (서로 다른 양산 Batch가 아님).",
        "- 원본 변수 34개, 고유 시료 ID 237개.",
        "- 문헌 시료 188개 / MAST3RBoost 프로젝트 시료 49개.",
        "- 원본은 세미콜론 구분, 단위 행 포함, 마지막 빈 열 구분자 포함.",
        "- BET 열 원문 오타를 유지해 처리: [ouptut] ABET.",
        "",
        "| 구분 | 시료 수 | BET 관측 | BET 결측 | BET 평균(m²/g) |",
        "|---|---:|---:|---:|---:|",
        f"| 문헌 시료 | {a['samples']} | {a['bet_observed']} | {a['bet_missing']} | {a['bet_mean_m2_g']} |",
        f"| 연구 프로젝트 | {b['samples']} | {b['bet_observed']} | {b['bet_missing']} | {b['bet_mean_m2_g']} |",
        "",
        "## 그림",
        "",
        "![온도와 BET 관계](./figures/temperature_vs_bet.svg)",
        "",
        "![출처 집단별 측정 커버리지](./figures/coverage_by_cohort.svg)",
        "",
        "## 제조 엔지니어 관점의 해석",
        "",
        "1. 시료 출처에 따른 측정 항목의 차이를 먼저 점검해야 합니다.",
        "2. 문헌 시료에는 수소 흡착량이 대부분 측정되지 않았습니다. 이를 0으로 대체하지 않습니다.",
        "3. 서로 다른 실험계·원료·활성화 조건을 혼합한 평균 차이는 원인효과가 아닙니다.",
        "4. 활성화 온도와 BET를 비교할 때 원료 조성, K/C, 유지시간, 분석법 등을 함께 검토해야 합니다.",
        "5. 실제 Scale-up 판단을 하려면 원료 LOT, 설비 형상, 열이력, 분위기, 수율, 반복측정과 원단위 데이터가 추가로 필요합니다.",
        "",
        "## 범위 및 한계",
        "",
        "완료: 원본 무결성 검사, 시료 ID 검증, 단위 행·스키마 처리, 출처별 결측 확인, 기초 시각화.",
        "미완료: 인과 분석, 양산 전환 검증, 최적 제조조건 도출, 경제성·에너지 원단위 평가.",
        "",
    ])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, help="Unchanged original Zenodo CSV stored locally")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    raw = args.source.read_bytes() if args.source else fetch_source()
    verify_md5(raw)
    df = parse_csv(raw.decode("utf-8-sig"))
    results = profile(df)
    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    (output / "results").mkdir(exist_ok=True)
    (output / "results" / "summary.json").write_text(
        json.dumps(results, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    (output / "results" / "REPORT.md").write_text(report(results), encoding="utf-8")
    plot(df, output / "results" / "figures")
    print("Original Zenodo MD5:", EXPECTED_MD5)
    print("Samples:", results["samples"], "| original columns:", results["source_columns"])
    for group, summary in results["cohorts"].items():
        print(group, summary["samples"], "samples; BET observed", summary["bet_observed"])
    print("Saved aggregate report and charts:", output / "results")


if __name__ == "__main__":
    main()
