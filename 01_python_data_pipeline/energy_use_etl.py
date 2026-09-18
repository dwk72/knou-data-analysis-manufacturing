"""
월별 에너지 사용 데이터를 API에서 받아 하나의 CSV로 통합하는 예제입니다.

전체 흐름
1. 연도와 월을 바꾸어가며 API를 반복 호출한다.
2. 응답 결과를 월별 JSON 파일로 저장한다.
3. 필요한 항목만 선택한다.
4. 전기·가스·수도·난방 값을 숫자형으로 변환한다.
5. 월별 데이터를 하나로 합친다.
6. 최종 결과를 CSV로 저장한다.

※ 공개용 코드이므로 실제 API 주소와 인증정보는 예시값으로 대체했습니다.
"""

# json: JSON 파일을 저장하고 읽는 데 사용
import json

# Path: 폴더와 파일 경로를 안전하게 다루기 위한 도구
from pathlib import Path

# pandas: 표 형태의 데이터를 정리·변환하기 위한 라이브러리
import pandas as pd

# requests: API에 데이터 요청을 보내기 위한 라이브러리
import requests


# 실제 API 주소 대신 공개용 예시 문자열을 사용합니다.
# 실행 시에는 본인이 발급받은 API 주소로 교체해야 합니다.
API_URL = "YOUR_API_ENDPOINT"

# 수집한 원본 JSON과 최종 CSV를 저장할 폴더입니다.
OUT_DIR = Path("data/energy_use")

# 폴더가 없으면 자동으로 생성합니다.
OUT_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# 1. Extract: 월별 에너지 데이터 수집
# ------------------------------------------------------------

# 2015년부터 2024년까지 반복합니다.
for year in range(2015, 2025):

    # 각 연도의 1월부터 12월까지 반복합니다.
    for month in range(1, 13):

        # API에 연도, 월, 응답형식(JSON)을 전달해 데이터를 요청합니다.
        response = requests.get(
            API_URL,
            params={
                "year": year,
                "month": f"{month:02d}",
                "TYPE": "json",
            },
            timeout=30,
        )

        # 서버 오류나 잘못된 요청이 발생하면 즉시 확인할 수 있도록
        # 정상 응답(HTTP 200대)이 아닐 경우 오류를 발생시킵니다.
        response.raise_for_status()

        # 원본 응답을 월별 JSON 파일로 저장합니다.
        # 원본을 따로 보관하면 전처리 방법을 바꿔도 재수집할 필요가 없습니다.
        with (OUT_DIR / f"output_{year}-{month:02d}.json").open(
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                response.json(),
                f,
                indent=2,
                ensure_ascii=False,
            )


# ------------------------------------------------------------
# 2. Transform: 필요한 열을 선택하고 형식을 정리
# ------------------------------------------------------------

# 분석에 사용할 열만 지정합니다.
# YEAR / MON : 연도 / 월
# MM_TYPE    : 사용자 유형
# EUS        : 전기 사용량
# GUS        : 가스 사용량
# WUS        : 수도 사용량
# HUS        : 난방 사용량
cols = [
    "YEAR",
    "MON",
    "MM_TYPE",
    "EUS",
    "GUS",
    "WUS",
    "HUS",
]

# 월별 데이터를 임시로 담아둘 리스트입니다.
frames = []

# 저장한 모든 월별 JSON 파일을 순서대로 읽습니다.
for path in sorted(OUT_DIR.glob("output_*.json")):

    # JSON 파일을 Python 객체로 불러옵니다.
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # API 응답 중 실제 데이터 행(row)만 꺼냅니다.
    rows = data["energyUseDataSummaryInfo"]["row"]

    # 행 데이터를 표 형태(DataFrame)로 바꿉니다.
    df = pd.DataFrame(rows)

    # 과제에서 분석한 '개인' 유형만 남기고,
    # 필요한 열만 선택합니다.
    df = df[df["MM_TYPE"] == "개인"][cols].copy()

    # 에너지 사용량이 문자로 들어온 경우 계산할 수 없으므로
    # 네 개 항목을 숫자형으로 변환합니다.
    for col in ["EUS", "GUS", "WUS", "HUS"]:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce",
        )

    # 정리된 월별 데이터를 리스트에 추가합니다.
    frames.append(df)


# ------------------------------------------------------------
# 3. Load: 월별 데이터를 하나로 통합해 저장
# ------------------------------------------------------------

# 여러 달의 데이터를 위아래로 이어 붙여 하나의 표로 만듭니다.
merged = pd.concat(
    frames,
    ignore_index=True,
)

# 통합된 데이터를 CSV 파일로 저장합니다.
merged.to_csv(
    OUT_DIR / "merged_energy_use.csv",
    index=False,
    encoding="utf-8-sig",
)

# 데이터 구조와 앞부분을 출력해 결과를 빠르게 확인합니다.
print(merged.info())
print(merged.head())
