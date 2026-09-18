# 06. Database Foundations

## 이 프로젝트에서 한 일

KNOU 데이터베이스시스템 과제에서 데이터를 단순 파일로 관리할 때 생기는 문제와, 이를 데이터베이스 구조로 관리하는 기본 원리를 학습했습니다.

### 파일 관리 방식의 한계

과제에서 다음 문제를 정리했습니다.

- **데이터 종속**: 데이터 구조가 특정 프로그램에 묶이는 문제
- **데이터 중복**: 같은 정보가 여러 곳에 반복 저장되는 문제
- **무결성 문제**: 서로 같은 의미의 데이터 값이 달라질 수 있는 문제
- **동시 접근 문제**: 여러 사용자가 동시에 수정할 때 값이 꼬일 수 있는 문제

### ER 모델링

온라인 서점 요구사항을 바탕으로 고객, 도서, 주문, 리뷰의 관계를 E-R 다이어그램으로 설계했습니다.

주요 내용:
- Customer
- Book
- Order
- Review
- 1:N / N:M 관계
- Key attribute
- Cardinality
- Participation constraint

ER 모델링은 실제 데이터베이스를 만들기 전에 **어떤 데이터를 어떤 관계로 저장할지 설계하는 단계**입니다.

## 사용 기술

`DBMS concepts` · `ER modeling` · `Relational modeling foundation`

## 현재 범위

현재 공개된 과제만으로는 **SQL을 이용해 실제 데이터베이스를 구축했다고 주장하지 않습니다.**

현재 단계는:
- DBMS 기본 개념 이해
- 관계형 데이터 구조 이해
- ER 모델 설계 경험

까지입니다.

## 제조업과의 연결 방향

향후 제조 데이터 구조로 바꾸면 다음과 같은 엔터티를 설계할 수 있습니다.

- LOT / Batch
- Material
- Process Condition
- Equipment
- Inspection / Quality Result

이후 SQL로 다음 기능을 구현할 계획입니다.

- 테이블 생성
- Primary Key / Foreign Key 설정
- 공정·품질 데이터 JOIN
- 제품·설비별 집계
- Batch / LOT별 생산·품질 KPI 조회

즉, 목표는 **공정조건과 품질결과를 같은 LOT/Batch 기준으로 연결할 수 있는 데이터 구조**를 만드는 것입니다.
