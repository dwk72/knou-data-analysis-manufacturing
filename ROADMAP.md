# Manufacturing Extension Roadmap

현재 저장소는 KNOU 과제에서 실제 수행한 분석을 정리한 **Academic Foundation** 단계입니다. 아래 항목은 이후 배터리·화학 생산기술 문제로 확장할 계획이며, 아직 완료된 결과로 주장하지 않습니다.

## 1. Manufacturing Data Pipeline

Academic foundation:
- 공공 API 호출
- JSON 저장 및 파싱
- pandas DataFrame 변환
- 타입 변환, 결측치 처리, 기간별 병합
- CSV 저장

Planned extension:
- Synthetic `lot_id` / `batch_id` 기반 제조 데이터 생성
- Material / Process / Equipment / Quality 테이블 분리
- Python 전처리 파이프라인 구성
- SQL 스키마 및 JOIN / GROUP BY / CTE / Window Function 실습

## 2. Multivariate Process Analysis

Academic foundation:
- 상관행렬
- PCA
- Scree plot
- Biplot
- Factor Analysis
- Varimax / Promax rotation
- R과 Python 결과 비교

Planned extension:
- 공정변수 상관구조 파악
- 차원축소
- 정상군 / 이상 LOT 비교
- 주요 loading 기반 공정변수 후보 도출

## 3. Process Time-Series

Academic foundation:
- 월별 생산지수 원계열 / 계절조정계열 비교
- Spectrum
- 로그변환 / 차분
- ADF test
- ACF / PACF

Planned extension:
- 반응기 온도·압력·유량 또는 배터리 공정조건의 Drift 분석
- Rolling statistics
- Change-point / anomaly 후보 탐색
- 설비·품질 이벤트와 시계열 변화 비교

## 4. Quality Modeling

Academic foundation:
- Linear Regression
- Logistic Regression
- Stepwise variable selection
- Accuracy / Sensitivity / Specificity
- CART Gini index

Planned extension:
- 공정조건 → 품질결과 연결
- OK / NG 분류
- 변수 영향 해석
- 모델 성능과 엔지니어링 해석 분리

## 5. Principles

- 실제 회사 기밀 데이터 사용 금지
- 제조 확장 데이터는 Synthetic / Public data로 명확히 표기
- 상관관계를 인과관계로 표현하지 않음
- ML보다 EDA와 공정 해석을 우선
- 사용한 도구와 실제 경험 수준을 구분
