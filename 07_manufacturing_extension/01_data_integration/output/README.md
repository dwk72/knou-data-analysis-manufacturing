# Data Integration Outputs

이 폴더는 [integrate_and_validate.py](../integrate_and_validate.py)의 실행 결과입니다.

| 파일 | 설명 |
|---|---|
| `integrated_master.csv` | 4개 테이블을 Batch 기준으로 통합한 전체 800 Batch |
| `analysis_ready_complete_cases.csv` | 핵심 분석변수에 결측치가 없는 776 Batch |
| `data_quality_summary.csv` | 주요 데이터 품질 지표 요약 |
| `outlier_summary.csv` | 변수별 IQR 범위와 이상치 후보 수 |

통계적 이상치는 자동 삭제하지 않았습니다. 제조 데이터의 극단값은 데이터 오류가 아니라 실제 공정 변화일 수도 있기 때문입니다.
