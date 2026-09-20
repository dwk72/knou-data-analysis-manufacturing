# Synthetic Manufacturing Data

이 폴더의 CSV 파일은 실제 회사나 실제 공정을 재현한 데이터가 아닙니다.

`generate_synthetic_data.py`에서 정의한 규칙에 따라 만든 **합성(Synthetic) Batch 데이터**이며, 생산기술 데이터 분석 흐름을 연습하기 위한 용도입니다.

## 포함 파일

| 파일 | 역할 |
|---|---|
| `batch_master.csv` | Batch 번호, 생산일자, 설비, Shift, 생산순서 |
| `material.csv` | 원료 LOT, 투입비, 원료 대표 물성 |
| `process_condition.csv` | 온도, 압력, 투입속도, 반응시간, 진공, 에너지 원단위 |
| `quality_result.csv` | 점도, 입도, 품질값, 수율, OK/NG 판정 |

모든 파일은 `batch_id`로 연결할 수 있습니다.

## 설계된 특징

- 정상적인 Random Noise
- 원료 LOT별 작은 차이
- 설비별 작은 Offset
- 생산 후반부의 Time Drift
- 일부 변수의 결측치
- 극소수 센서성 이상값
- 여러 조건의 조합으로 증가하는 NG 위험

중요한 점은 **특정 변수 하나만으로 품질 결과가 결정되지 않도록 만든 것**입니다. 따라서 이후 EDA, 다변량 분석, 시계열 분석, 품질모델링을 순서대로 적용할 이유가 생깁니다.

상세한 생성 원칙은 [../GENERATION_RULES.md](../GENERATION_RULES.md), 변수 정의는 [../DATA_SCHEMA.md](../DATA_SCHEMA.md)를 참고합니다.
