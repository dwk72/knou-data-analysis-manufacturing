-- 제조 질문:
-- Batch 500 이후에 삽입된 시간 Drift가 집계 KPI에서도 보이는가?
--
-- CTE(Common Table Expression)에서 먼저 각 Batch를 두 기간으로 분류한 뒤
-- 반응시간, 에너지 원단위, NG 비율을 비교합니다.

WITH periodized AS (
    SELECT
        CASE
            WHEN b.sequence <= 500 THEN 'Batch 1-500'
            ELSE 'Batch 501-800'
        END AS period,
        p.reaction_time,
        p.energy_kwh_per_ton,
        q.quality_flag
    FROM batch_master AS b
    JOIN process_condition AS p
        ON b.batch_id = p.batch_id
    JOIN quality_result AS q
        ON b.batch_id = q.batch_id
)
SELECT
    period,
    COUNT(*) AS batches,
    ROUND(AVG(reaction_time), 2) AS avg_reaction_time,
    ROUND(AVG(energy_kwh_per_ton), 2) AS avg_energy_kwh_per_ton,
    SUM(CASE WHEN quality_flag = 'NG' THEN 1 ELSE 0 END) AS ng_count,
    ROUND(
        100.0 * SUM(CASE WHEN quality_flag = 'NG' THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS ng_rate_pct
FROM periodized
GROUP BY period
ORDER BY CASE period
    WHEN 'Batch 1-500' THEN 1
    ELSE 2
END;
