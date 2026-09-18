# KNOU Data Analysis → Manufacturing

방송통신대학교 통계·데이터과학/컴퓨터과학 과제에서 수행한 데이터 수집·전처리·통계분석·머신러닝·데이터베이스 학습 결과를 정리하고, 이후 배터리·화학 **생산기술(Manufacturing / Process Engineering)** 문제로 확장하기 위한 포트폴리오 저장소입니다.

> **현재 버전의 범위**
> - 지금까지 실제로 수행한 KNOU 과제와 코드에 근거한 `Academic Foundation` 정리
> - 개인정보가 포함된 원본 PDF/DOCX는 공개하지 않음
> - 제조 데이터 적용 결과는 아직 구현하지 않았으며, `Manufacturing Extension`으로 별도 확장 예정
> - 따라서 현재 README의 제조 연계 내용은 **향후 적용 방향**이며 실제 제조 데이터 분석 결과를 의미하지 않음

## Portfolio Structure

| Section | Academic foundation | Tools / methods | Manufacturing extension |
|---|---|---|---|
| [01. Python Data Pipeline](./01_python_data_pipeline/) | 공공 API 데이터 수집, JSON → DataFrame, 전처리·병합·CSV 저장 | Python, requests, pandas, JSON | LOT/Batch·설비·품질 데이터 통합 |
| [02. Multivariate Analysis](./02_multivariate_analysis/) | 기술통계, 상관분석, PCA, Factor Analysis | R, Python | 다변량 공정상태 분석, 이상 LOT 탐색 |
| [03. Time-Series Analysis](./03_time_series_analysis/) | 생산지수 시계열, spectrum, ADF, ACF/PACF | R, zoo, forecast, tseries | 공정 Drift·주기성·이상징후 분석 |
| [04. Quality Modeling](./04_quality_modeling/) | 와인 품질 선형/로지스틱 회귀, 변수선택, CART | R | 품질 영향인자 탐색, OK/NG 예측 |
| [05. ML/DL Foundations](./05_ml_dl_foundations/) | MNIST 모델 구조·optimizer·learning rate 실험 | PyTorch / TensorFlow 학습 | 품질예측·비전·이상감지로 확장 |
| [06. Database Foundations](./06_database_foundations/) | DBMS 기본개념, ER 모델링 | Relational DB, ERD | Batch/LOT–Process–Quality 스키마 및 SQL |

## What is already demonstrated

### Python
- `requests` 기반 공공 API 호출
- JSON 데이터 저장·파싱
- `pandas.DataFrame` 변환
- 숫자/날짜 타입 변환 및 결측치 처리
- 월별/연도별 데이터 병합
- CSV 저장 및 기초 시각화

### R / Statistics
- 단순·다중회귀
- 로지스틱 회귀
- 단계적 변수선택
- PCA 및 인자분석
- Varimax / Promax 회전
- 시계열 스펙트럼 분석
- 로그변환·차분
- ADF 정상성 검정
- ACF / PACF 해석

### Machine Learning
- PyTorch 기반 MNIST 모델 구조 변경
- ReLU 추가
- SGD → Adam optimizer 변경
- learning rate 비교
- 모델 구조/하이퍼파라미터 변경 후 성능 비교

### Database
- 파일 처리 시스템의 데이터 종속·중복·무결성·동시접근 문제 학습
- 온라인 서점 요구사항 기반 ER 모델링
- 관계형 데이터 모델링 기초

## Why manufacturing?

이 저장소의 목적은 데이터 분석 기법 자체를 나열하는 것이 아니라, 이후 다음과 같은 생산기술 분석 흐름으로 연결하는 것입니다.

```text
Data Collection
      ↓
Data Cleaning / Integration
      ↓
EDA & Multivariate Analysis
      ↓
Time-Series Monitoring
      ↓
Quality / Process Modeling
      ↓
Engineering Interpretation
```

예정된 제조 확장은 배터리 또는 화학공정의 **합성(Synthetic) 데이터**를 사용합니다. 실제 근무지의 원본 데이터나 기밀자료는 사용하지 않습니다.

## Current Status

- [x] Python API / ETL academic foundation
- [x] R/Python multivariate-analysis foundation
- [x] R time-series foundation
- [x] R quality-modeling foundation
- [x] ML/DL learning evidence
- [x] DBMS / ER modeling foundation
- [ ] Manufacturing synthetic dataset
- [ ] Manufacturing EDA extension
- [ ] Process time-series extension
- [ ] Manufacturing quality prediction
- [ ] SQL manufacturing schema & queries

상세 확장 계획은 [ROADMAP.md](./ROADMAP.md)를 참고합니다.

## Notes on source material

원본 과제에는 이름·학번·연락처 등 개인정보가 포함되어 있어 공개 저장소에는 업로드하지 않습니다. 이 저장소에는 과제에서 실제 수행한 분석 흐름과 코드를 개인정보·인증키·로컬 경로를 제거해 재정리합니다.

---

**Target roles:** Manufacturing Engineering · Process Engineering · Production Technology · Battery / Chemical Manufacturing · Manufacturing Data Analytics
