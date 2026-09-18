# Manufacturing Extension Roadmap

현재 저장소는 KNOU 과제에서 실제로 수행한 분석을 정리한 단계입니다.

다음 단계에서는 같은 분석기법을 배터리·화학 생산기술 문제에 맞게 확장합니다. 아래 항목은 **향후 계획**이며 아직 완료된 제조 분석 결과는 아닙니다.

## 1. 제조 데이터 파이프라인

현재까지 수행:
- 공공 API 데이터 수집
- JSON 저장·읽기
- pandas DataFrame 변환
- 데이터 형식 정리
- 결측치 처리
- 여러 기간의 데이터 통합
- CSV 저장

다음 단계:
- 합성 `lot_id` / `batch_id` 제조 데이터 생성
- Material / Process / Equipment / Quality 데이터 분리
- Python으로 분석용 데이터 통합
- SQL로 공정·품질 데이터 연결

## 2. 다변량 공정분석

현재까지 수행:
- 상관행렬
- PCA
- Scree plot
- Biplot
- Factor Analysis
- R과 Python 결과 비교

다음 단계:
- 여러 공정변수의 관계 확인
- 차원축소
- 정상 LOT / 이상 LOT 비교
- 차이를 만드는 주요 변수 후보 확인

## 3. 공정 시계열 분석

현재까지 수행:
- 원계열 / 계절조정계열 비교
- 주기성 분석
- 로그변환 / 차분
- ADF 검정
- ACF / PACF

다음 단계:
- 반응기 온도·압력·유량 또는 배터리 공정조건의 시간 변화 분석
- 이동평균 등 Rolling statistics 적용
- 변화 시점과 이상구간 탐색
- 품질 이벤트와 공정 변화 비교

## 4. 품질 모델링

현재까지 수행:
- Linear Regression
- Logistic Regression
- 단계적 변수선택
- Accuracy / Sensitivity / Specificity
- CART Gini index

다음 단계:
- 공정조건과 품질결과 연결
- OK / NG 분류
- 품질 영향변수 후보 확인
- 모델 성능과 공정 해석을 분리해 검토

## 5. 작업 원칙

- 실제 회사의 기밀 데이터는 사용하지 않음
- 제조 확장 데이터는 Synthetic / Public data로 명확히 표시
- 상관관계를 원인으로 단정하지 않음
- 복잡한 ML보다 EDA와 공정 해석을 우선
- 실제 수행한 내용과 향후 계획을 명확히 구분
