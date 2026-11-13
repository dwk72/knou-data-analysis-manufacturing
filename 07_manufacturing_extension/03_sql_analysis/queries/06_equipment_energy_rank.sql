-- 제조 질문:
-- 설비별 평균 에너지 원단위를 높은 순서로 순위화하면 어떻게 되는가?
--
-- 먼저 설비별 평균을 CTE에서 계산하고,
-- RANK Window Function으로 상대 순위를 부여합니다.

WITH equipment_energy AS (
    SELECT
        b.equipment_id,
        COUNT(*) AS batches,
        AVG(p.energy_kwh_per_ton) AS avg_energy_kwh_per_ton
    FROM batch_master AS b
    JOIN process_condition AS p
        ON b.batch_id = p.batch_id
    GROUP BY b.equipment_id
)
SELECT
    equipment_id,
    batches,
    ROUND(avg_energy_kwh_per_ton, 2) AS avg_energy_kwh_per_ton,
    RANK() OVER (
        ORDER BY avg_energy_kwh_per_ton DESC
    ) AS energy_rank
FROM equipment_energy
ORDER BY energy_rank, equipment_id;
