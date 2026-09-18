"""
월별 대기질 데이터를 공공 API에서 받아 CSV 파일로 정리하는 예제입니다.

전체 흐름
1. API에서 월별 데이터를 가져온다.
2. 원본 응답을 JSON 파일로 저장한다.
3. 분석에 필요한 열만 선택한다.
4. 날짜와 숫자 형식을 정리한다.
5. 여러 달의 데이터를 하나로 합친다.
6. 최종 결과를 CSV로 저장한다.

※ 공개용 코드이므로 실제 API 인증키와 개인 PC 경로는 제거했습니다.
"""

# json: API에서 받은 JSON 형식의 데이터를 파일로 저장하거나 읽을 때 사용
import json

# Path: 운영체제에 관계없이 폴더와 파일 경로를 다루기 위한 도구
from pathlib import Path

# pandas: 표 형태의 데이터를 정리하고 분석하는 대표적인 Python 라이브러리
import pandas as pd

# requests: 인터넷의 API에 데이터를 요청할 때 사용하는 라이브러리
import requests


# 실제 인증키 대신 예시 문자열을 사용합니다.
# 코드를 실행하려면 본인의 API 키로 교체해야 합니다.
API_KEY = "YOUR_API_KEY"

# 수집한 JSON과 최종 CSV를 저장할 폴더입니다.
OUT_DIR = Path("data/air_quality")

# 폴더가 없으면 새로 만듭니다.
# parents=True: 상위 폴더가 없어도 함께 생성
# exist_ok=True: 이미 폴더가 있어도 오류를 내지 않음
OUT_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# 1. Extract: API에서 원본 데이터 가져오기
# ------------------------------------------------------------

# 2012년부터 2024년까지 연도별로 반복합니다.
for year in range(2012, 2025):

    # 각 연도 안에서 1월부터 12월까지 반복합니다.
    for month in range(1, 13):

        # API가 요구하는 YYYYMM 형식의 문자열을 만듭니다.
        # 예: 2024년 3월 -> "202403"
        ym = f"{year}{month:02d}"

        # 요청할 API 주소를 만듭니다.
        # 여기서는 '한강대로' 측정소의 월평균 대기질 데이터를 요청합니다.
        url = (
            "http://openAPI.seoul.go.kr:8088/"
            f"{API_KEY}/json/MonthlyAverageAirQuality/1/5/{ym}/한강대로"
        )

        # API에 데이터를 요청합니다.
        # timeout=30은 30초 안에 응답이 없으면 요청을 중단한다는 의미입니다.
        response = requests.get(url, timeout=30)

        # 요청이 실패했다면 오류를 발생시켜 문제를 바로 확인할 수 있게 합니다.
        response.raise_for_status()

        # API 응답을 월별 JSON 파일로 저장합니다.
        # 원본 데이터를 보존해두면 이후 전처리 방법을 바꾸더라도
        # API를 다시 호출하지 않고 재분석할 수 있습니다.
        with (OUT_DIR / f"output_{ym}.json").open(
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
# 2. Transform: 분석하기 좋은 형태로 정리하기
# ------------------------------------------------------------

# 원본 데이터에서 사용할 열만 지정합니다.
# MSRDT_MT : 측정 연월
# MSRSTE_NM: 측정소 이름
# PM10     : 미세먼지(PM10) 값
cols = ["MSRDT_MT", "MSRSTE_NM", "PM10"]

# 월별 DataFrame을 잠시 담아둘 빈 리스트입니다.
frames = []

# 앞에서 저장한 모든 JSON 파일을 파일명 순서대로 읽습니다.
for path in sorted(OUT_DIR.glob("output_*.json")):

    # JSON 파일을 Python 객체로 읽습니다.
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # API 응답에서 실제 관측값이 들어 있는 'row' 부분만 꺼냅니다.
    rows = data["MonthlyAverageAirQuality"]["row"]

    # 관측값을 행과 열이 있는 표(DataFrame)로 바꾸고,
    # 위에서 정한 필요한 열만 남깁니다.
    df = pd.DataFrame(rows)[cols].copy()

    # 날짜 문자열을 실제 날짜 형식으로 변환합니다.
    # 변환할 수 없는 값은 오류 대신 결측치(NaT)로 처리합니다.
    df["MSRDT_MT"] = pd.to_datetime(
        df["MSRDT_MT"],
        format="%Y%m",
        errors="coerce",
    )

    # 측정소 이름은 문자형으로 통일합니다.
    df["MSRSTE_NM"] = df["MSRSTE_NM"].astype(str)

    # PM10 값은 계산할 수 있도록 숫자형으로 변환합니다.
    # 숫자로 바꿀 수 없는 값은 결측치(NaN)로 처리합니다.
    df["PM10"] = pd.to_numeric(
        df["PM10"],
        errors="coerce",
    )

    # 날짜나 PM10 값이 비어 있는 행은 분석에서 제외합니다.
    df = df.dropna()

    # 정리된 월별 데이터를 리스트에 추가합니다.
    frames.append(df)


# ------------------------------------------------------------
# 3. Load: 정리한 데이터를 하나로 합쳐 저장하기
# ------------------------------------------------------------

# 월별 DataFrame을 위아래로 이어 붙여 하나의 데이터셋으로 만듭니다.
merged = pd.concat(
    frames,
    ignore_index=True,
)

# 최종 데이터를 CSV 파일로 저장합니다.
# utf-8-sig를 사용하면 Excel에서도 한글이 비교적 안정적으로 표시됩니다.
merged.to_csv(
    OUT_DIR / "merged_air_quality.csv",
    index=False,
    encoding="utf-8-sig",
)

# 데이터 구조와 앞부분을 출력해 정상적으로 정리됐는지 확인합니다.
print(merged.info())
print(merged.head())
