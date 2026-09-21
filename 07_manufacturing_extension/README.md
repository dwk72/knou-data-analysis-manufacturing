# 07. Manufacturing Extension

## 프로젝트 목적

앞선 학업 프로젝트에서 사용한 Python, R, 통계분석, 머신러닝, 데이터베이스 개념을 하나의 제조 문제에 연결합니다.

이번 확장에서는 실제 회사 데이터를 사용하지 않고, **배터리 소재·화학 Batch 공정을 단순화한 합성(Synthetic) 데이터**를 사용합니다.

핵심 질문은 다음과 같습니다.

> Batch 간 품질 편차와 수율 변동이 커졌을 때, 여러 공정·원료·설비 데이터에서 어떤 항목을 먼저 확인해야 하는가?

목표는 불량 원인을 자동으로 확정하는 것이 아니라, **현장 엔지니어가 우선 확인할 후보를 데이터로 좁히는 것**입니다.

---

## 1. Problem

Batch 생산공정에서 최근 품질 편차와 수율 변동이 증가했다고 가정합니다.

생산 데이터는 한곳에 모여 있지 않고 다음처럼 여러 영역에 나뉘어 있다고 봅니다.

- Batch 기본정보
- 원료 LOT 정보
- 공정조건
- 설비 정보
- 품질검사 결과

따라서 첫 단계는 이 데이터를 Batch 기준으로 연결해 분석 가능한 형태로 만드는 것입니다.

---

## 2. Process Context

이 프로젝트는 특정 회사나 실제 공정을 재현하지 않습니다.

다만 배터리 소재·화학 제조에서 일반적으로 볼 수 있는 다음 구조를 단순화해 사용합니다.

```text
Raw Material
     ↓
Batch Production
     ↓
Process Conditions
     ↓
Intermediate Quality
     ↓
Final Quality / Yield
```

분석 대상은 특정 장치의 상세 설계보다 **Batch별 공정조건과 품질결과의 관계**입니다.

---

## 3. Initial Hypotheses

분석을 시작하기 전에 다음과 같은 가설을 설정합니다.

1. 특정 원료 LOT에서 품질 편차가 커질 수 있다.
2. 일부 설비에서 공정값이 일정하게 치우칠 수 있다.
3. 반응시간·온도·압력 등 공정변수의 조합이 품질과 관련될 수 있다.
4. 시간이 지나면서 특정 변수에 Drift가 발생할 수 있다.
5. 단일 변수보다 여러 변수의 조합이 이상 Batch를 더 잘 설명할 수 있다.

이 가설들은 정답이 아니라 **분석 순서를 정하기 위한 출발점**입니다.

---

## 4. Data Structure

합성 데이터는 다음 4개 테이블로 나눕니다.

```text
batch_master
     │
     ├── material
     │
     ├── process_condition
     │
     └── quality_result
```

### batch_master
Batch 식별과 생산 시점, 사용 설비를 관리합니다.

### material
원료 LOT와 배합 관련 정보를 관리합니다.

### process_condition
Batch별 주요 운전조건을 관리합니다.

### quality_result
중간·최종 품질과 수율, 품질판정을 관리합니다.

상세 변수는 [DATA_SCHEMA.md](./DATA_SCHEMA.md)에 정리합니다.

---

## 5. Analysis Flow

기존 학업 프로젝트의 분석기법을 아래 순서로 연결합니다.

```text
1. Data Integration
      ↓
2. Data Quality Check / EDA
      ↓
3. Multivariate Analysis
      ↓
4. Time-Series Analysis
      ↓
5. Quality Modeling
      ↓
6. Validation
      ↓
7. Manufacturing Action
```

### 1) Data Integration
Python과 SQL을 이용해 분리된 테이블을 Batch 기준으로 연결합니다.

확인 항목:
- 중복 Batch
- 결측치
- 데이터 타입
- 비정상 범위
- 테이블 간 누락 여부

### 2) EDA
정상 Batch와 이상 Batch가 어떤 점에서 다른지 먼저 확인합니다.

예:
- 변수별 분포
- OK / NG 그룹 비교
- 설비별 품질 차이
- 원료 LOT별 품질 차이
- 상관관계

### 3) Multivariate Analysis
PCA 등을 이용해 여러 공정변수를 동시에 봅니다.

질문:
- 이상 Batch가 정상 Batch와 다른 공정영역에 위치하는가?
- 어떤 변수가 그 차이에 크게 기여하는가?

### 4) Time-Series Analysis
생산 순서에 따라 변수의 변화가 누적되는지 확인합니다.

질문:
- 특정 공정값이 서서히 이동하는가?
- 품질 저하 전에 변화가 시작되는가?
- 반복되는 패턴이 있는가?

### 5) Quality Modeling
로지스틱 회귀를 기준모델로 사용해 품질판정을 분류합니다.

평가 항목:
- Accuracy
- Precision
- Recall
- F1
- Confusion Matrix

복잡한 모델은 기준모델의 한계를 확인한 뒤 필요할 때 추가합니다.

---

## 6. Validation

분석 결과를 그대로 원인으로 해석하지 않습니다.

세 가지 관점에서 검증합니다.

### 데이터 검증
- 결측·중복·이상치
- 데이터 범위
- 테이블 연결 오류

### 통계 검증
- Train / Test 분리
- 분류성능 비교
- 필요 시 통계검정
- 단순 기준모델과 비교

### 공정 타당성 검토
통계적으로 관계가 있더라도 공정적으로 설명 가능한지 별도로 확인합니다.

예를 들어 한 변수와 NG가 함께 증가해도 원료 LOT, 설비, 생산시점의 영향을 함께 확인합니다.

---

## 7. Manufacturing Action

최종 산출물은 단순한 그래프나 예측값이 아닙니다.

분석 결과를 다음과 같은 **점검 우선순위**로 연결하는 것을 목표로 합니다.

```text
이상 Batch 확인
    ↓
관련 변수 후보
    ↓
원료 / 설비 / 공정조건 교차확인
    ↓
우선 점검 항목 선정
    ↓
추가 데이터 확인 또는 실험
```

예시:

- 특정 설비에서만 이상이 집중된다면 설비상태와 교정이력을 우선 확인
- 특정 원료 LOT에서 품질편차가 커진다면 원료 성적과 투입이력을 우선 확인
- 특정 공정영역에서 NG가 증가한다면 운전조건과 작업기준을 우선 검토

> 데이터 분석은 원인을 자동으로 확정하기 위한 것이 아니라, 현장조사의 탐색 범위를 줄이기 위한 의사결정 지원 수단으로 사용합니다.

---

## 8. Current Status

- [x] 제조 Case 정의
- [x] 분석 목적 정의
- [x] 초기 가설 설정
- [x] 데이터 테이블 구조 설계
- [x] 분석 순서 설계
- [x] Synthetic 데이터 생성
- [x] Python 데이터 통합
- [ ] SQL Query 작성
- [ ] EDA
- [ ] PCA
- [ ] Time-Series 분석
- [ ] Logistic Regression
- [ ] Validation
- [ ] Manufacturing Action 정리

데이터 생성 원칙은 [GENERATION_RULES.md](./GENERATION_RULES.md), 실제 생성 결과는 [data](./data/), 데이터 검증 요약은 [VALIDATION_SUMMARY.md](./VALIDATION_SUMMARY.md)에 정리합니다.\n\n첫 분석 단계인 데이터 통합·품질점검은 [01_data_integration](./01_data_integration/)에서 확인할 수 있습니다.
