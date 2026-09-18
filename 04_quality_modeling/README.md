# 04. Quality Modeling

## Academic Foundation

KNOU 데이터마이닝 과제에서 범주형 목표변수인 와인 품질 데이터를 이용해 선형회귀와 로지스틱 회귀를 비교하고, 단계적 변수선택과 모델 평가를 수행했습니다.

### Linear Regression
- 전체 입력변수로 회귀모형 적합
- `step()`을 이용한 단계적 변수선택
- 선택된 변수의 회귀계수 방향 해석
- 예측값 생성
- MSE / MAE 확인

### Logistic Regression
- 이항형 목표변수에 `glm(..., family = binomial)` 적용
- 단계적 변수선택
- 확률 예측
- cutoff 0.5로 class 결정
- Confusion Matrix
- Accuracy / Sensitivity / Specificity 확인

과제 결과에서 로지스틱 회귀의 예측 정확도는 75.1%, 민감도는 76.7%, 특이도는 73.2%였습니다.

### CART
- 범주형 분할 후보별 Gini index 계산
- Gini index가 최소인 분할집합 선택

정리된 R 코드는 [wine_quality_models.R](./wine_quality_models.R)에 있습니다.

## Skills Demonstrated

`R` · `Linear Regression` · `Logistic Regression` · `Stepwise Selection` · `Confusion Matrix` · `CART` · `Gini Index`

## Manufacturing Relevance — Planned

현재 대상 데이터는 와인 품질이며 제조공정 데이터가 아닙니다. 이후에는 동일한 문제구조를 다음과 같이 바꿀 계획입니다.

```text
Process Conditions
       ↓
Quality Result
       ↓
Regression / Classification
       ↓
Candidate Variables for Engineering Review
```

예정 적용:
- 공정조건 → OK / NG 분류
- 품질특성 예측
- 중요 변수 후보 확인
- 통계적 결과와 공정 엔지니어링 해석의 분리

이 단계에서는 상관·예측 결과를 원인으로 단정하지 않고, 후속 현장검증이 필요한 후보 변수로 해석하는 것을 원칙으로 합니다.
