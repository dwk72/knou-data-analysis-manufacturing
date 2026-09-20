# Synthetic Data Validation Summary

## 데이터 규모

- Batch 수: **800**
- 기간: **2026-01-01부터 약 9개월**
- 설비: **EQ_A / EQ_B / EQ_C**
- 원료 LOT: **12종**
- 품질판정: **OK / NG**

## 생성 시 의도한 구조

이 데이터는 다음 현상을 일부 포함하도록 만들었습니다.

1. 원료 LOT별 작은 물성 차이
2. 설비별 작은 공정·에너지 Offset
3. Batch 500 이후 반응시간과 에너지 사용량의 완만한 Drift
4. 일부 설비의 후반부 산포 증가
5. 공정조건·원료·설비·시간효과가 함께 작용하는 품질위험
6. 소량의 결측치와 센서성 이상값

## 데이터 품질 문제

의도적으로 삽입한 결측치:

- temperature: 8건
- vacuum: 8건
- viscosity: 5건
- raw_property: 4건

또한 temperature와 pressure에 극소수의 센서성 이상값을 추가했습니다.

## 품질판정 분포

- NG: **150건**
- OK: **650건**
- NG 비율: **18.8%**

품질판정은 특정 변수 하나의 단순 임계값으로 결정하지 않았습니다. 공정조건 조합, 원료 LOT, 설비, 시간 Drift와 Random Noise가 함께 영향을 주도록 구성했습니다.

## 해석 시 주의사항

이 데이터의 패턴은 실제 산업공정의 물리법칙이나 실제 관리기준을 의미하지 않습니다. 목적은 다음 분석 흐름을 검증하는 것입니다.

```text
Data Quality Check
→ EDA
→ Multivariate Analysis
→ Time-Series Analysis
→ Quality Modeling
→ Manufacturing Action
```

따라서 이후 분석에서도 통계적 관계를 실제 인과관계로 표현하지 않습니다.
