# 06. Database Foundations

## Academic Foundation

KNOU 데이터베이스시스템 과제에서 파일 처리 시스템의 한계와 관계형 데이터베이스 모델링의 기초를 다뤘습니다.

### File Processing vs DBMS
과제에서 정리한 주요 문제:
- 데이터 종속
- 데이터 중복
- 데이터 무결성 훼손
- 동시 접근 이상

### ER Modeling Exercise
온라인 서점 관리 요구사항을 기반으로 다음 개체와 관계를 포함한 E-R 다이어그램을 설계했습니다.

- Customer
- Book
- Order
- Review
- 주문과 도서의 다대다 관계
- 고객과 주문의 일대다 관계
- 고객과 도서의 Review 관계
- Key attribute / cardinality / participation constraint

## Skills Demonstrated

`DBMS concepts` · `ER modeling` · `Relational modeling foundation`

## Current Limitation

현재 공개한 학업 과제만으로는 **SQL 실행 프로젝트를 수행했다고 주장하지 않습니다.** DBMS와 ER 모델링 기초를 학습한 수준입니다.

## Manufacturing Relevance — Planned

다음 단계에서 온라인 서점 ERD 대신 제조 데이터 구조로 확장할 예정입니다.

예정 엔터티:
- LOT / Batch
- Material
- Process Condition
- Equipment
- Inspection / Quality Result

이후 실제 SQL로 다음을 구현할 계획입니다.
- CREATE TABLE / PK / FK
- JOIN
- GROUP BY
- CTE
- Window Function
- LOT / Batch별 생산·품질 KPI 조회
