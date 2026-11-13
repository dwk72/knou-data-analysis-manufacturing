# 과제 기반 GitHub 복원 기록

## 범위

2025년도 방송대 제출 과제 DOCX/PDF와 공개 GitHub 기본 브랜치를 비교했습니다. 제출 원본 문서에는 학번·성명·연락처 등이 포함될 수 있으므로 문서 자체는 GitHub에 올리지 않았습니다. 공개된 소스에는 개인식별정보, 로컬 절대경로, 인증정보를 포함하지 않습니다.

| 영역 | 제출 자료 근거 | GitHub 코드 상태 | 검증·남은 제약 |
|---|---|---|---|
| 01 Python ETL | 오픈소스기반데이터분석 제출 DOCX | 기존 air_quality_etl.py / energy_use_etl.py | 원래 API 인증키와 수집 응답은 게시하지 않음. API 재현 미확인 |
| 02 다변량분석 | 다변량분석 제출 DOCX | coursework_methods.R(방법 재구성), multivariate_demo.py(Iris 독립 예제) 추가 | Python 예제 오프라인 실행 확인. 과제 CSV 없음, R 실행 미검증 |
| 03 시계열분석 | 예측방법론 제출 DOCX와 별도 R 원본 파일 | 기존 industrial_production_analysis.R | 입력 원계열·계절조정 엑셀은 GitHub에 없음, 재현 미확인 |
| 04 회귀·데이터마이닝 | 회귀모형·데이터마이닝 제출 DOCX | 기존 wine_quality_models.R, 추가 mtcars_regression_reconstructed.R | 와인 데이터 원본 없음; mtcars는 R 내장 데이터. 이 환경에는 R 실행기가 없어 새 R 파일 미검증 |
| 05 머신러닝·딥러닝 | 머신러닝 PDF의 코드 캡처, 딥러닝 제출 DOCX | mnist_reconstructed.py 추가 | 코드 캡처에서 MNIST 네트워크 구조를 재구성. 모델 forward/1 step 오프라인 점검 통과. 실제 MNIST 10 epoch 재학습은 미수행 |
| 06 데이터베이스 | 데이터베이스시스템 제출 DOCX의 개념 설명·그림 | README 기존 | 학업 과제 자체의 SQL 실행 근거는 확인되지 않음. 별도 독립 확장으로 07 제조 프로젝트에 SQLite 구현 추가 |
| 07 제조 확장 | 공개 합성 제조 Batch 프로젝트 | 생성·통합·품질검증 Python, 기초 EDA SVG 3개, SQLite 스키마·JOIN·GROUP BY·CTE·Window Function 제조 KPI 조회 | Python/SQL 재현성 테스트와 시각화 재생성 검증 구성. 실제 공정 데이터·실제 DBMS 운영환경 검증은 수행하지 않음 |

## 표현 규칙

1. **기존 제출물의 텍스트에 근거한 코드**와 **설명을 바탕으로 재구성한 코드**를 구분합니다.
2. Iris 데모의 PCA 설명분산을 원래 과제 결과로 소개하지 않습니다.
3. 제출 머신러닝 과제 PDF에 기재된 MNIST 정확도 97.82%는 과거 결과입니다. 재구성된 코드의 새 실행 결과가 아닙니다.
4. 와인 품질분석의 학업 보고서 숫자를 현장 적용 성과로 소개하지 않습니다.
5. 제조 확장 사례는 합성 데이터 기반의 생성·통합·품질검증·기초 EDA·SQLite 제조 KPI 조회까지 완료된 것으로 소개합니다. 원인규명 / 실제 개선 실적은 주장하지 않습니다.
6. 과제 원본이나 개인·학교 식별정보, 승인받지 않은 데이터는 이 공개 저장소에 넣지 않습니다.

## 인력 채용 포트폴리오 연결

공개 가능한 독립 제조 사례는 [07 제조 Batch 프로젝트](./07_manufacturing_extension/)이며, 데이터 통합·품질점검·기초 EDA와 [SQLite 제조 KPI 분석](./07_manufacturing_extension/03_sql_analysis/)까지 구분해 확인할 수 있습니다. 학업 재구성 스크립트는 기초 역량의 보조 근거로 소개합니다.
