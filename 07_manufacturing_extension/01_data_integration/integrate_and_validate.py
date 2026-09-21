"""
4개의 제조 데이터 테이블을 Batch 기준으로 통합하고 데이터 품질을 점검합니다.

왜 이 단계가 필요한가?
제조현장의 데이터는 생산, 설비, 원료, 품질 시스템에 나뉘어 저장되는 경우가 많습니다.
분석을 시작하기 전에 같은 Batch의 기록이 정확히 연결되는지, 빠진 값이나 중복된 기록이
없는지 먼저 확인해야 이후 통계분석과 모델 결과를 신뢰할 수 있습니다.

입력
- ../data/batch_master.csv
- ../data/material.csv
- ../data/process_condition.csv
- ../data/quality_result.csv

출력
- output/integrated_master.csv
- output/analysis_ready_complete_cases.csv
- output/data_quality_summary.csv

중요
- 통계적 이상치는 자동으로 삭제하지 않습니다.
- IQR 기준 이상치는 '검토가 필요한 후보'로 표시만 합니다.
- 결측치가 있는 Batch도 integrated_master에는 그대로 보존합니다.
"""

from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------
# 0. 파일 위치와 분석에 사용할 변수 정의
# ---------------------------------------------------------------------

# 이 파일의 상위 폴더가 07_manufacturing_extension입니다.
BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 결측치와 통계적 이상치를 확인할 주요 수치형 변수입니다.
ANALYSIS_COLUMNS = [
    "feed_ratio",
    "raw_property",
    "temperature",
    "pressure",
    "feed_rate",
    "reaction_time",
    "vacuum",
    "energy_kwh_per_ton",
    "viscosity",
    "particle_size",
    "quality_value",
    "yield_pct",
]


# ---------------------------------------------------------------------
# 1. 원본 테이블 불러오기
# ---------------------------------------------------------------------

# 각 파일은 서로 다른 제조 정보를 담고 있지만 batch_id를 공통으로 가집니다.
batch = pd.read_csv(DATA_DIR / "batch_master.csv")
material = pd.read_csv(DATA_DIR / "material.csv")
process = pd.read_csv(DATA_DIR / "process_condition.csv")
quality = pd.read_csv(DATA_DIR / "quality_result.csv")

tables = {
    "batch_master": batch,
    "material": material,
    "process_condition": process,
    "quality_result": quality,
}


# ---------------------------------------------------------------------
# 2. 통합 전에 각 원본 테이블의 구조 확인
# ---------------------------------------------------------------------

print("=== Source table check ===")

reference_ids = set(batch["batch_id"])

for name, df in tables.items():
    row_count = len(df)
    unique_batch_count = df["batch_id"].nunique()
    duplicate_count = df["batch_id"].duplicated().sum()

    print(
        f"{name}: "
        f"rows={row_count}, "
        f"unique_batch_id={unique_batch_count}, "
        f"duplicates={duplicate_count}"
    )

    # batch_master를 기준으로 다른 테이블에 빠진 Batch가 있는지 확인합니다.
    if name != "batch_master":
        current_ids = set(df["batch_id"])

        missing_ids = reference_ids - current_ids
        extra_ids = current_ids - reference_ids

        if missing_ids:
            print(f"  -> batch_master에는 있지만 {name}에는 없는 Batch: {len(missing_ids)}")

        if extra_ids:
            print(f"  -> {name}에만 존재하는 Batch: {len(extra_ids)}")


# ---------------------------------------------------------------------
# 3. batch_id 기준으로 4개 테이블 통합
# ---------------------------------------------------------------------

# batch_master를 기준 테이블로 두고 나머지 정보를 차례로 붙입니다.
#
# validate="one_to_one"은 한 Batch가 양쪽 테이블에 여러 번 존재하면
# 오류를 발생시킵니다. 즉, 조용히 잘못된 다대다 결합이 생기는 것을 방지합니다.
master = (
    batch
    .merge(material, on="batch_id", how="left", validate="one_to_one")
    .merge(process, on="batch_id", how="left", validate="one_to_one")
    .merge(quality, on="batch_id", how="left", validate="one_to_one")
)

# 생산일자는 문자열보다 날짜형으로 바꾸어야
# 이후 시간순 정렬이나 시계열 분석을 안정적으로 수행할 수 있습니다.
master["production_date"] = pd.to_datetime(
    master["production_date"],
    errors="coerce",
)

# 분석 대상 숫자열은 명시적으로 숫자형으로 변환합니다.
# 변환할 수 없는 값이 있다면 NaN(결측치)로 바꾸어 문제를 숨기지 않습니다.
for column in ANALYSIS_COLUMNS:
    master[column] = pd.to_numeric(
        master[column],
        errors="coerce",
    )


# ---------------------------------------------------------------------
# 4. 결측치 점검
# ---------------------------------------------------------------------

# 각 Batch에 핵심 분석변수가 몇 개 비어 있는지 계산합니다.
master["dq_missing_count"] = (
    master[ANALYSIS_COLUMNS]
    .isna()
    .sum(axis=1)
)


# ---------------------------------------------------------------------
# 5. 통계적 이상치 후보 점검
# ---------------------------------------------------------------------

# IQR 방식은 데이터의 중앙 50% 범위를 이용해
# 일반적인 분포에서 멀리 떨어진 값을 찾는 간단한 방법입니다.
#
# 여기서 중요한 점:
# 'IQR 이상치 = 잘못된 데이터'가 아닙니다.
# 실제 공정변동이나 중요한 이상징후일 수도 있으므로 삭제하지 않고 표시만 합니다.
outlier_count = pd.Series(
    0,
    index=master.index,
    dtype="int64",
)

outlier_summary = []

for column in ANALYSIS_COLUMNS:
    series = master[column].dropna()

    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    is_outlier = (
        (master[column] < lower)
        | (master[column] > upper)
    )

    outlier_count += is_outlier.fillna(False).astype(int)

    outlier_summary.append(
        {
            "column": column,
            "q1": q1,
            "q3": q3,
            "lower_bound": lower,
            "upper_bound": upper,
            "outlier_count": int(is_outlier.sum()),
        }
    )

master["dq_outlier_count"] = outlier_count

# 결측치 또는 통계적 이상치가 있으면 검토 대상으로 표시합니다.
# 자동 삭제 대신 사람이 확인할 수 있는 흔적을 남기는 방식입니다.
master["dq_review_flag"] = (
    (master["dq_missing_count"] > 0)
    | (master["dq_outlier_count"] > 0)
).map({
    True: "REVIEW",
    False: "PASS",
})


# ---------------------------------------------------------------------
# 6. 분석용 데이터셋 분리
# ---------------------------------------------------------------------

# integrated_master:
# 원본 정보를 최대한 보존한 통합본입니다.
integrated_master = master.copy()

# complete_cases:
# 결측치를 허용하지 않는 PCA나 일부 모델링에서 사용할 수 있도록
# 핵심 분석변수에 결측치가 없는 Batch만 별도로 만듭니다.
#
# 통계적 이상치는 삭제하지 않습니다.
complete_cases = master.loc[
    master["dq_missing_count"] == 0
].copy()


# ---------------------------------------------------------------------
# 7. 결과 저장
# ---------------------------------------------------------------------

# 날짜는 사람이 읽기 쉬운 YYYY-MM-DD 형태로 저장합니다.
for df in [integrated_master, complete_cases]:
    df["production_date"] = df["production_date"].dt.strftime("%Y-%m-%d")

integrated_master.to_csv(
    OUTPUT_DIR / "integrated_master.csv",
    index=False,
    encoding="utf-8-sig",
)

complete_cases.to_csv(
    OUTPUT_DIR / "analysis_ready_complete_cases.csv",
    index=False,
    encoding="utf-8-sig",
)

pd.DataFrame(outlier_summary).to_csv(
    OUTPUT_DIR / "outlier_summary.csv",
    index=False,
    encoding="utf-8-sig",
)

summary = pd.DataFrame(
    [
        {
            "metric": "integrated_rows",
            "value": len(integrated_master),
            "meaning": "4개 원본 테이블 통합 후 Batch 수",
        },
        {
            "metric": "missing_cells",
            "value": int(integrated_master[ANALYSIS_COLUMNS].isna().sum().sum()),
            "meaning": "핵심 분석변수의 전체 결측 셀 수",
        },
        {
            "metric": "rows_with_missing",
            "value": int((integrated_master["dq_missing_count"] > 0).sum()),
            "meaning": "결측치가 1개 이상 있는 Batch 수",
        },
        {
            "metric": "complete_case_rows",
            "value": len(complete_cases),
            "meaning": "핵심 분석변수에 결측치가 없는 Batch 수",
        },
        {
            "metric": "rows_with_iqr_outlier",
            "value": int((integrated_master["dq_outlier_count"] > 0).sum()),
            "meaning": "IQR 기준 이상치 후보가 있는 Batch 수",
        },
        {
            "metric": "rows_flagged_for_review",
            "value": int((integrated_master["dq_review_flag"] == "REVIEW").sum()),
            "meaning": "결측 또는 이상치 때문에 검토가 필요한 Batch 수",
        },
    ]
)

summary.to_csv(
    OUTPUT_DIR / "data_quality_summary.csv",
    index=False,
    encoding="utf-8-sig",
)


# ---------------------------------------------------------------------
# 8. 실행 결과를 화면에 요약
# ---------------------------------------------------------------------

print("\n=== Integrated data quality summary ===")
print(f"Integrated rows       : {len(integrated_master)}")
print(f"Integrated columns    : {len(integrated_master.columns)}")
print(
    "Missing cells         : "
    f"{int(integrated_master[ANALYSIS_COLUMNS].isna().sum().sum())}"
)
print(
    "Rows with missing     : "
    f"{int((integrated_master['dq_missing_count'] > 0).sum())}"
)
print(f"Complete-case rows    : {len(complete_cases)}")
print(
    "Rows with IQR outlier : "
    f"{int((integrated_master['dq_outlier_count'] > 0).sum())}"
)
print(
    "Rows flagged REVIEW   : "
    f"{int((integrated_master['dq_review_flag'] == 'REVIEW').sum())}"
)

print("\nQuality flag distribution")
print(integrated_master["quality_flag"].value_counts())
