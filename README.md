# 제조 데이터 포트폴리오 | 탄소소재 · 화학공정

화학공정·생산기술 관점에서 데이터를 검증하고, 제조조건과 품질의 관계를 해석해 다음 점검·실험을 설계하는 포트폴리오입니다.

## 대표 사례: 탄소소재 제조조건과 BET 비표면적 분석

> 공개 활성탄 **연구데이터** 분석 · 실제 생산라인 Batch 자료 아님 · 실험 **미실시** · 공정개선 실적 아님

| 제조 관점의 질문 | 확인한 결과 | 엔지니어링 판단 |
|---|---|---|
| 데이터의 비교 가능성 | 시료 237개, 문헌 188개 / Nottingham 연구 49개 | 서로 다른 연구·측정값을 같은 공정의 반복으로 취급하지 않음 |
| 온도와 품질의 관계 | 문헌 600·700·800°C 중 BET 측정 162개 | 다른 원료·연구조건이 섞여 인과효과로 해석하지 않음 |
| 원료 조성과 물성 | 800°C 고정 연구시료 49개, K/C–O/C 상관 +0.918 | 온도효과 추정 불가. 조성변수의 상호연관과 해석 오류 확인 |
| 다음 확인 방법 | LOT 2개 × K/C 3수준 × 2일, 제조 12회 **예비 제안** | K/C 투입량 대응·안전·표본수 사전검증 미완료로 **NO-GO** |

이 프로젝트에서 강조하는 것은 모델의 높은 점수가 아니라, 실제 제조조건 변경 전에 **검증 가능한 데이터·가설·실험 계획과 실행 불가 조건을 구분한 판단**입니다.

[<escape>1쪽 프로젝트 요약</escape>](./carbon_materials_process_quality/PORTFOLIO_SUMMARY.md) · [탄소소재 분석 상세](./carbon_materials_process_quality/) · [탐색 회귀·시각화](./carbon_materials_process_quality/02_process_relationships/) · [확인실험 제안](./carbon_materials_process_quality/03_confirmation_plan/) · [공학 검토](./carbon_materials_process_quality/03_confirmation_plan/TECHNICAL_REVIEW.md)

### 검증 및 자료 출처

- Python·Pandas·Matplotlib, 부트스트랩·반복 교차검증 및 GitHub Actions 자동 재현성 확인
- 원자료: University of Nottingham / Nanolayers, [Zenodo v2](https://zenodo.org/records/23311682), DOI 10.5281/zenodo.23311682. CC BY-ND 2.5, 원본 CSV 미배포
- 데이터 기준: 237개 활성탄 연구시료. 양산 수율·에너지 원단위·설비 이력·제품 규격 없음
- 실험 계획은 승인된 Recipe가 아니며, 실제 제조·측정·품질 개선을 수행하지 않았음

---

## 기존 프로젝트 (보존)

### 화학·배터리 합성 Batch 데이터 통합·품질검증

[기존 제조 Batch 프로젝트](./07_manufacturing_extension/) · [데이터 통합 및 점검](./07_manufacturing_extension/01_data_integration/) · [기초 EDA 시각화](./07_manufacturing_extension/02_eda/)

- 합성 Batch 데이터 800개를 직접 생성하고 원료·공정·생산·품질 정보 4개 테이블로 나누었습니다.
- Batch ID 기준으로 자료를 연결해 결측·IQR 이상치 후보를 검토했습니다.
- REVIEW 83개 Batch를 구분하고 원본 800개와 결측 없는 776개 분석용 데이터셋을 보존했습니다.
- Python 자동 재현성 검사 4개 테스트를 통과했습니다.
- 실측 공장 데이터와 실제 개선 실적은 아닙니다.

기존 프로젝트의 경로와 내용은 유지했습니다. 이전 GitHub 첫 화면 내용도 [LEGACY_README.md](./LEGACY_README.md)에 별도로 보존했습니다.

## 방송통신대학교 통계·컴퓨터과학 학업 기반

| 영역 | 관련 코드 및 정리 |
|---|---|
| Python 데이터 수집·처리 | [01_python_data_pipeline](./01_python_data_pipeline/) |
| PCA·인자분석 | [02_multivariate_analysis](./02_multivariate_analysis/) |
| 시계열 분석 | [03_time_series_analysis](./03_time_series_analysis/) |
| 회귀·품질모델링 | [04_quality_modeling](./04_quality_modeling/) |
| 머신러닝·딥러닝 실습 | [05_ml_dl_foundations](./05_ml_dl_foundations/) |
| 데이터베이스 기초 | [06_database_foundations](./06_database_foundations/) |

학업 과제를 공개용으로 재구성한 코드에는 원본 데이터가 누락된 사례가 있습니다. [복원·검증 범위](./RESTORATION_STATUS.md)에서 수행 여부와 재현 한계를 구분해 확인할 수 있습니다.

## 포트폴리오 원칙

- 실제 공개 연구데이터, 학습용 합성 데이터, 실무경험을 구분해 표기합니다.
- 원료·공정조건과 품질변수 사이의 상관관계를 원인효과로 단정하지 않습니다.
- 측정 누락과 자료 출처·시료 단위를 확인한 뒤 분석합니다.
- 개인식별정보·회사 기밀자료·API 인증정보를 공개하지 않습니다.
- 구현과 검증이 완료되지 않은 기능은 성과로 소개하지 않습니다.

관련 직무: 탄소소재 / 전자소재 / 화학공정 / 생산기술 / 제조 데이터 분석.
