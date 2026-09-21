# Data Quality Report

## 1. 데이터 연결 상태

| Source | Rows | Unique batch_id | Duplicate batch_id |
|---|---:|---:|---:|
| batch_master.csv | 800 | 800 | 0 |
| material.csv | 800 | 800 | 0 |
| process_condition.csv | 800 | 800 | 0 |
| quality_result.csv | 800 | 800 | 0 |

4개 테이블 모두 800개의 고유 Batch를 포함하며 중복 `batch_id`는 없습니다.

`batch_master`를 기준으로 연결했을 때 최종 통합 데이터도 **800 Batch**를 유지했습니다. 따라서 이번 데이터에서는 테이블 연결 과정의 누락이나 중복 증폭이 확인되지 않았습니다.

## 2. 결측치

핵심 분석변수의 결측 셀은 총 **25개**이며, **24개 Batch**에 분포합니다.

| Variable | Missing |
|---|---:|
| raw_property | 4 |
| temperature | 8 |
| vacuum | 8 |
| viscosity | 5 |

결측치가 없는 Complete Case는 **776개**입니다.

결측치를 자동으로 대체하지 않은 이유는, 평균값 등으로 기계적으로 채우면 실제 공정·계측 문제의 흔적을 없앨 수 있기 때문입니다.

## 3. 통계적 이상치 후보

IQR(Interquartile Range) 기준으로 하나 이상의 이상치 후보를 가진 Batch는 **61개**입니다.

| Variable | IQR outlier candidates |
|---|---:|
| feed_ratio | 8 |
| raw_property | 0 |
| temperature | 8 |
| pressure | 4 |
| feed_rate | 4 |
| reaction_time | 3 |
| vacuum | 4 |
| energy_kwh_per_ton | 7 |
| viscosity | 6 |
| particle_size | 7 |
| quality_value | 13 |
| yield_pct | 14 |

이 수치는 데이터 오류 건수가 아닙니다.

> **통계적 이상치 ≠ 공정 이상 확정**

극단값은 센서 오류, 입력 오류, 정상적인 공정 산포, 실제 이상운전 중 어느 경우에도 발생할 수 있습니다. 따라서 이 단계에서는 값을 삭제하지 않고 `dq_outlier_count`와 `dq_review_flag`로 표시만 했습니다.

## 4. 검토 대상

- 결측치가 있는 Batch: **24개**
- IQR 이상치 후보가 있는 Batch: **61개**
- 둘 중 하나 이상으로 REVIEW 표시된 Batch: **83개**
- 별도 데이터 품질 플래그가 없는 Batch: **717개**

## 5. 품질판정 구조 확인

- OK: **650개**
- NG: **150개**
- NG 비율: **18.8%**

이 단계에서는 OK/NG 원인을 해석하지 않습니다. 품질판정 비율과 데이터 구조만 확인하고, 실제 차이는 다음 EDA 단계에서 분석합니다.

## 6. 정제 원칙

이번 단계의 처리 원칙은 다음과 같습니다.

1. 원본 Batch를 임의로 삭제하지 않음
2. 통계적 이상치를 자동 삭제하지 않음
3. 결측치를 임의의 평균값으로 채우지 않음
4. 데이터 품질 문제는 별도 Flag로 남김
5. 결측치를 허용하지 않는 분석용으로만 Complete Case 파일을 별도 생성

즉, **데이터를 깨끗하게 보이게 만드는 것보다 어떤 문제가 있었는지를 추적할 수 있게 만드는 것**을 우선했습니다.
