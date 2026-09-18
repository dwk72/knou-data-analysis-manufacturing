# 03. Time-Series Analysis

## Academic Foundation

KNOU 예측방법론 과제에서 2000~2025년 월별 전산업생산지수의 원계열과 계절조정계열을 대상으로 R 시계열 분석을 수행했습니다.

### Analysis Flow

1. 원계열 / 계절조정계열 시계열 시각화
2. Spectrum 비교
3. 계절조정계열 로그변환
4. 로그차분
5. ADF 정상성 검정
6. ACF / PACF 비교

과제 해석에서는 원계열에서 반복적인 계절변동이 관찰되고, 계절조정계열에서는 해당 주기성이 완화됨을 확인했습니다. 또한 로그변환과 차분을 통해 정상성 변화를 비교했습니다.

정리된 R 코드는 [industrial_production_analysis.R](./industrial_production_analysis.R)에 있습니다.

## Skills Demonstrated

`R` · `zoo` · `ggplot2` · `spectrum` · `log transform` · `differencing` · `ADF` · `ACF` · `PACF`

## Manufacturing Relevance — Planned

아직 제조 설비·공정 시계열에 적용한 결과는 없습니다. 다음 단계에서 같은 분석 흐름을 Synthetic 제조 데이터에 적용할 예정입니다.

예정 예시:
- 반응기 온도·압력·유량 Drift
- 설비 센서값의 주기성
- 배터리 공정조건의 시간 변화
- 불량률 / 수율 변화와 공정 시계열 비교

핵심 목표는 **시간축을 가진 공정 데이터에서 추세·주기성·비정상성을 먼저 확인한 뒤 후속 예측이나 이상감지로 넘어가는 것**입니다.
