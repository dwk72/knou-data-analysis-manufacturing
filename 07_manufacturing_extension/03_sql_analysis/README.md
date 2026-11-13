# 제조 Batch SQL 분석

SQLite · JOIN · GROUP BY · CTE · Window Function · Manufacturing KPI

> 합성(Synthetic) 제조 데이터 기반 독립 확장입니다. 실제 공장 SQL 시스템이나 양산 KPI가 아닙니다.

## 왜 SQL을 추가했는가

기존 프로젝트에서는 Python/Pandas로 생산·원료·공정·품질 테이블을 통합했습니다. 실제 제조 데이터는 여러 테이블에 나뉘어 저장되는 경우가 많으므로, 같은 질문을 **관계형 데이터베이스와 SQL로도 조회할 수 있는지** 확인했습니다.

목적은 SQL 문법을 나열하는 것이 아니라 다음 제조 질문을 데이터 구조와 연결하는 것입니다.

| 제조 질문 | 사용한 SQL |
|---|---|
| 같은 Batch의 원료·공정·품질을 한 행에서 볼 수 있는가? | JOIN |
| 설비별 NG율·수율·에너지 원단위는? | GROUP BY, CASE |
| 원료 LOT별 품질 차이는? | GROUP BY |
| Batch 500 전후 Drift가 집계 KPI에서도 보이는가? | CTE |
| 최근 40 Batch NG율은 어떻게 변하는가? | Window Function |
| 설비별 에너지 원단위 순위는? | CTE, RANK |

## 데이터베이스 구조

```text
batch_master
     │ PK: batch_id
     ├──────── material
     ├──────── process_condition
     └──────── quality_result
               FK: batch_id
```

[스키마 정의](./schema.sql)에서 Primary Key와 Foreign Key를 명시했습니다. CSV의 빈 측정값은 숫자 0으로 바꾸지 않고 SQLite `NULL`로 보존합니다.

## 확인된 SQL 결과

### 설비별 KPI

| 설비 | Batch | NG율 | 평균 수율 | 평균 에너지 원단위 |
|---|---:|---:|---:|---:|
| EQ_A | 287 | 19.16% | 96.40 | 238.36 |
| EQ_B | 269 | 17.84% | 96.22 | 244.92 |
| EQ_C | 244 | 19.26% | 96.31 | 240.74 |

EQ_B는 평균 에너지 원단위가 가장 높지만 NG율은 세 설비 중 가장 낮습니다. 따라서 이 데이터에서도 **에너지 원단위 차이를 품질 원인으로 단순 연결할 수 없습니다.**

### Batch 500 전후

| 기간 | 평균 반응시간 | 평균 에너지 원단위 | NG율 |
|---|---:|---:|---:|
| Batch 1–500 | 59.86 | 237.25 | 16.40% |
| Batch 501–800 | 62.69 | 248.01 | 22.67% |

이는 합성 데이터 생성 코드에서 Batch 500 이후 Drift와 품질위험 증가를 의도적으로 넣은 결과입니다. 실제 공정 이상을 발견한 결과가 아닙니다.

### 원료 LOT

M12의 NG율은 37.88%로 가장 높게 집계됩니다. 하지만 생성 규칙에 LOT 위험효과가 포함되어 있으므로, 이를 실제 원료 품질 문제를 발견한 것처럼 해석하지 않습니다.

## 실행 방법

Python 표준 라이브러리의 `sqlite3`만 사용하므로 SQL 단계 자체에는 별도 DB 서버가 필요하지 않습니다.

```bash
python 07_manufacturing_extension/03_sql_analysis/build_and_query.py
```

실행하면 로컬 SQLite DB와 6개 조회 결과 CSV가 생성됩니다.

- [JOIN 예시](./output/01_join_sample.csv)
- [설비 KPI](./output/02_equipment_kpi.csv)
- [원료 LOT KPI](./output/03_material_lot_kpi.csv)
- [Batch 500 전후 비교](./output/04_before_after_drift.csv)
- [40-Batch 이동 NG율](./output/05_rolling_40_ng_rate.csv)
- [설비 에너지 순위](./output/06_equipment_energy_rank.csv)

SQLite DB 파일 자체는 GitHub에 올리지 않고 재생성하도록 했습니다.

## 검증

[test_manufacturing_sql.py](../../tests/test_manufacturing_sql.py)에서 다음을 확인합니다.

1. 4개 테이블이 각각 800행인지
2. Foreign Key 위반이 없는지
3. 공개된 SQL 결과 CSV가 코드 재실행 결과와 같은지
4. 최종 Batch B0800의 최근 40 Batch NG율이 40.00%인지

SQL 결과는 Synthetic 데이터의 구조를 검증하는 학습 사례입니다. 실제 제조 조건의 원인효과, 설비 우열, 원료 LOT 판정을 의미하지 않습니다.
