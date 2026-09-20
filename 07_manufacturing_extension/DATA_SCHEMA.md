# Manufacturing Data Schema

## 설계 원칙

데이터 구조는 복잡한 실제 MES나 LIMS를 재현하지 않고, 생산기술 분석에 필요한 관계만 남겨 단순화합니다.

핵심 연결키는 `batch_id`입니다.

```text
batch_master.batch_id
        │
        ├── material.batch_id
        ├── process_condition.batch_id
        └── quality_result.batch_id
```

---

## 1. batch_master

Batch의 기본정보와 생산순서를 관리합니다.

| Column | 의미 | 예시 |
|---|---|---|
| batch_id | Batch 고유번호 | B0001 |
| production_date | 생산일자 | 2026-01-03 |
| equipment_id | 사용 설비 | EQ_A |
| shift | 생산 Shift | DAY |
| sequence | 생산 순번 | 1 |

### 분석에서의 역할
- 시간순서 정렬
- 설비별 비교
- Batch 단위 데이터 연결

---

## 2. material

Batch에 투입된 원료 정보를 관리합니다.

| Column | 의미 | 예시 |
|---|---|---|
| batch_id | Batch 고유번호 | B0001 |
| material_lot | 원료 LOT | M03 |
| feed_ratio | 원료 배합비 | 1.02 |
| raw_property | 원료 대표 물성 | 98.7 |

### 분석에서의 역할
- 원료 LOT별 품질편차 확인
- 원료특성과 최종품질 관계 확인
- 원료 효과와 공정조건 효과 구분

---

## 3. process_condition

Batch 운전조건을 관리합니다.

| Column | 의미 | 예시 |
|---|---|---|
| batch_id | Batch 고유번호 | B0001 |
| temperature | 대표 운전온도 | 182.4 |
| pressure | 대표 압력 | 2.31 |
| feed_rate | 투입속도 | 101.8 |
| reaction_time | 반응시간 | 61.5 |
| vacuum | 진공 관련 지표 | 0.84 |
| energy_kwh_per_ton | 제품 1톤당 에너지 사용량 | 245 |

### 분석에서의 역할
- 공정변수 분포 확인
- 상관관계 분석
- PCA
- 시간에 따른 Drift 확인
- 품질모델 입력변수

> 단위와 수치범위는 실제 회사 공정값을 의미하지 않으며, 분석 연습을 위한 합성값입니다.

---

## 4. quality_result

중간품질, 생산성 및 최종 판정을 관리합니다.

| Column | 의미 | 예시 |
|---|---|---|
| batch_id | Batch 고유번호 | B0001 |
| viscosity | 중간 품질지표 | 430 |
| particle_size | 입도 관련 품질지표 | 18.2 |
| quality_value | 최종 연속형 품질값 | 99.1 |
| yield_pct | 수율 | 96.8 |
| quality_flag | 최종 품질판정 | OK |

### 분석에서의 역할
- OK / NG 그룹 비교
- 품질값 예측
- 수율 분석
- 로지스틱 회귀 목표변수

---

## 5. 분석용 통합 데이터

분석 시에는 위 4개 테이블을 `batch_id` 기준으로 연결합니다.

최종 형태 예시:

```text
batch_id
production_date
equipment_id
material_lot
feed_ratio
raw_property
temperature
pressure
feed_rate
reaction_time
vacuum
energy_kwh_per_ton
viscosity
particle_size
quality_value
yield_pct
quality_flag
```

이 데이터셋을 EDA, PCA, 시계열 분석, 품질모델링의 공통 입력으로 사용합니다.
