-- 제조 질문:
-- 설비별 생산량, NG 비율, 평균 수율, 평균 에너지 원단위가 어떻게 다른가?
--
-- GROUP BY로 설비 단위 KPI를 한 번에 집계합니다.
-- 결과 차이는 합성 데이터에서 설정한 구조를 반영하며 실제 설비 성능을 의미하지 않습니다.

SELECT
    b.equipment_id,
    COUNT(*) AS batches,
    SUM(CASE WHEN q.quality_flag = 'NG' THEN 1 ELSE 0 END) AS ng_count,
    ROUND(
        100.0 * SUM(CASE WHEN q.quality_flag = 'NG' THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS ng_rate_pct,
    ROUND(AVG(q.yield_pct), 2) AS avg_yield_pct,
    ROUND(AVG(p.energy_kwh_per_ton), 2) AS avg_energy_kwh_per_ton
FROM batch_master AS b
JOIN process_condition AS p
    ON b.batch_id = p.batch_id
JOIN quality_result AS q
    ON b.batch_id = q.batch_id
GROUP BY b.equipment_id
ORDER BY b.equipment_id;
