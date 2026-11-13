-- 제조 질문:
-- 원료 LOT별 품질판정과 평균 품질·수율에 차이가 있는가?
--
-- LOT별 차이는 후속 확인 대상을 좁히는 참고정보입니다.
-- 이 결과만으로 원료 LOT를 불량 원인으로 확정하지 않습니다.

SELECT
    m.material_lot,
    COUNT(*) AS batches,
    SUM(CASE WHEN q.quality_flag = 'NG' THEN 1 ELSE 0 END) AS ng_count,
    ROUND(
        100.0 * SUM(CASE WHEN q.quality_flag = 'NG' THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS ng_rate_pct,
    ROUND(AVG(q.quality_value), 2) AS avg_quality_value,
    ROUND(AVG(q.yield_pct), 2) AS avg_yield_pct
FROM material AS m
JOIN quality_result AS q
    ON m.batch_id = q.batch_id
GROUP BY m.material_lot
ORDER BY m.material_lot;
