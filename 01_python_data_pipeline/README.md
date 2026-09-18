# 01. Python Data Pipeline

## Academic Foundation

KNOU 과제에서 Python을 이용해 공공 데이터를 수집하고 분석 가능한 형태로 변환하는 과정을 수행했습니다.

### Case A: Monthly Air Quality API
- `requests`로 월별 공공 API 호출
- JSON 응답 저장
- `pandas` DataFrame 변환
- 날짜·문자·수치형 데이터 타입 변환
- 결측치 제거
- 기간별 DataFrame 병합
- CSV 저장
- 월별 및 연도별 PM10 변화 시각화

정리된 코드는 [air_quality_etl.py](./air_quality_etl.py)에 있습니다.

### Case B: Energy Use API
- 2015~2024 기간의 월별 API 데이터 수집
- JSON 파일 저장
- 필요한 열 선택
- 전기·가스·수도·난방 사용량 수치형 변환
- 월별 데이터 통합

정리된 코드는 [energy_use_etl.py](./energy_use_etl.py)에 있습니다.

## Skills Demonstrated

`Python` · `requests` · `JSON` · `pandas` · `data cleaning` · `ETL` · `CSV`

## Manufacturing Relevance — Planned

현재 단계에서 제조 데이터를 직접 분석한 것은 아닙니다. 이후 동일한 데이터 파이프라인 구조를 다음 문제에 적용할 예정입니다.

- LOT / Batch 단위 공정조건 통합
- 설비 로그와 품질검사 결과 연결
- 생산·품질 데이터의 타입 및 결측치 정리
- 후속 EDA / 통계모델 입력 데이터 생성

즉, 이 폴더는 **제조 분석 이전 단계인 데이터 수집·정리 역량의 학업 증빙** 역할을 합니다.
