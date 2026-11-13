-- 제조 질문:
-- 서로 다른 4개 테이블에서 같은 Batch의 원료·공정·품질 정보를 한 행으로 볼 수 있는가?
--
-- SQL의 JOIN은 Python의 merge와 같은 역할을 합니다.
-- 여기서는 1:1 Batch 관계가 이미 검증된 데이터를 INNER JOIN으로 연결합니다.

SELECT
    b.batch_id,
    b.production_date,
    b.equipment_id,
    m.material_lot,
    p.temperature,
    p.pressure,
    p.reaction_time,
    p.energy_kwh_per_ton,
    q.yield_pct,
    q.quality_flag
FROM batch_master AS b
JOIN material AS m
    ON b.batch_id = m.batch_id
JOIN process_condition AS p
    ON b.batch_id = p.batch_id
JOIN quality_result AS q
    ON b.batch_id = q.batch_id
ORDER BY b.sequence
LIMIT 20;
