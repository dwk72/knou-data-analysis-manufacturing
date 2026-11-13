# SQL Query Outputs

모든 CSV는 `build_and_query.py`가 SQLite에서 직접 실행한 SQL 조회 결과를 저장한 것입니다.

| 파일 | 내용 |
|---|---|
| `01_join_sample.csv` | 4개 테이블 JOIN 결과 앞 20 Batch |
| `02_equipment_kpi.csv` | 설비별 Batch 수, NG율, 평균 수율, 평균 에너지 원단위 |
| `03_material_lot_kpi.csv` | 원료 LOT별 품질 KPI |
| `04_before_after_drift.csv` | Batch 500 전후 공정·품질 KPI |
| `05_rolling_40_ng_rate.csv` | Window Function으로 계산한 최근 40 Batch NG율 |
| `06_equipment_energy_rank.csv` | 설비별 평균 에너지 원단위 순위 |

이 결과는 합성 데이터에서 계산한 값이며 실제 제조 KPI가 아닙니다.
