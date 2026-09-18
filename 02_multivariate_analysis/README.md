# 02. Multivariate Analysis

## Academic Foundation

KNOU 다변량분석 과제에서 R과 Python을 이용해 기술통계, 상관분석, 주성분분석(PCA), 인자분석(Factor Analysis)을 수행했습니다.

### Descriptive & Correlation Analysis
- 히스토그램
- 산점도행렬
- 상관계수행렬
- 변수 간 상관구조 해석

### Principal Component Analysis
- 표준화
- 고윳값 및 설명분산 확인
- Scree plot
- 유효 주성분 선정
- 주성분계수 해석
- Biplot
- R과 Python PCA 결과 비교

과제에서는 고윳값이 1보다 큰 주성분 3개를 유효 주성분으로 해석했고, R과 Python의 주성분계수는 부호 차이를 제외하면 절대값이 동일함을 확인했습니다.

### Factor Analysis
- 인자분석 적합성 확인
- 초기 인자분석
- 인자부하량 해석
- Varimax / Promax rotation
- 인자 수 선정
- R / Python 결과 비교

과제에서는 2개의 유의한 인자를 선정하고 회전 전후의 loading 변화를 비교했습니다.

## Skills Demonstrated

`R` · `Python` · `Correlation` · `PCA` · `Factor Analysis` · `Scree Plot` · `Biplot` · `Varimax` · `Promax`

## Manufacturing Relevance — Planned

현재 분석 대상은 제조 데이터가 아닙니다. 이후 제조 확장에서는 다음과 같은 형태로 적용할 예정입니다.

- 다수 공정변수의 상관구조 파악
- PCA 기반 차원축소
- 정상 LOT / 이상 LOT의 score 차이 탐색
- loading을 이용한 주요 영향변수 후보 확인
- 품질·설비·공정 데이터를 하나의 다변량 공간에서 비교

이 폴더의 현재 역할은 **여러 변수가 동시에 움직이는 데이터를 R/Python으로 해석할 수 있음을 보여주는 학업 증빙**입니다.
