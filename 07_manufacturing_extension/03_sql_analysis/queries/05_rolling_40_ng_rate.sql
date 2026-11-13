-- 제조 질문:
-- 최근 40 Batch 기준 NG 비율이 생산순서에 따라 어떻게 변하는가?
--
-- Window Function을 사용하면 각 행을 유지한 상태에서
-- 앞선 39개 Batch와 현재 Batch를 함께 계산할 수 있습니다.

WITH quality_by_batch AS (
    SELECT
        b.batch_id,
        b.sequence,
        CASE WHEN q.quality_flag = 'NG' THEN 1 ELSE 0 END AS ng_indicator
    FROM batch_master AS b
    JOIN quality_result AS q
        ON b.batch_id = q.batch_id
)
SELECT
    batch_id,
    sequence,
    COUNT(*) OVER (
        ORDER BY sequence
        ROWS BETWEEN 39 PRECEDING AND CURRENT ROW
    ) AS window_batches,
    ROUND(
        100.0
        * SUM(ng_indicator) OVER (
            ORDER BY sequence
            ROWS BETWEEN 39 PRECEDING AND CURRENT ROW
        )
        / COUNT(*) OVER (
            ORDER BY sequence
            ROWS BETWEEN 39 PRECEDING AND CURRENT ROW
        ),
        2
    ) AS rolling_40_ng_rate_pct
FROM quality_by_batch
ORDER BY sequence;
