-- ==========================================================
-- zomato_analysis.sql
-- Zomato Bangalore Restaurant Analysis — 25 Advanced SQL Queries
-- Compatible: PostgreSQL 14+ / SQLite 3.35+ (minor syntax diff noted)
-- Author: Your Name
-- ==========================================================

-- ──────────────────────────────────────────────────────────
-- SETUP: Create and populate table (SQLite approach)
-- In PostgreSQL: use COPY or \copy instead of INSERT
-- ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS zomato (
    name              TEXT,
    online_order      BOOLEAN,
    book_table        BOOLEAN,
    rate_numeric      REAL,
    votes             INTEGER,
    location          TEXT,
    rest_type         TEXT,
    primary_rest_type TEXT,
    cuisines          TEXT,
    primary_cuisine   TEXT,
    approx_cost       REAL,
    cost_bucket       TEXT,
    is_high_rated     BOOLEAN,
    cuisine_count     INTEGER,
    listed_in_type    TEXT,
    listed_in_city    TEXT
);


-- ==========================================================
-- Q1. Total restaurant count and high-rated percentage
-- ==========================================================
SELECT
    COUNT(*)                                              AS total_restaurants,
    ROUND(AVG(rate_numeric), 3)                           AS avg_rating,
    ROUND(100.0 * SUM(CASE WHEN rate_numeric >= 4.0 THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_high_rated,
    ROUND(AVG(approx_cost), 2)                            AS avg_cost,
    SUM(votes)                                            AS total_votes
FROM zomato;


-- ==========================================================
-- Q2. Top 20 locations by restaurant density
-- ==========================================================
SELECT
    location,
    COUNT(*)                          AS restaurant_count,
    ROUND(AVG(rate_numeric), 2)       AS avg_rating,
    ROUND(AVG(approx_cost), 2)        AS avg_cost,
    SUM(votes)                        AS total_votes,
    ROUND(100.0 * COUNT(*) /
          (SELECT COUNT(*) FROM zomato), 2) AS market_share_pct
FROM zomato
GROUP BY location
ORDER BY restaurant_count DESC
LIMIT 20;


-- ==========================================================
-- Q3. Online order impact — T-test proxy with aggregates
-- ==========================================================
SELECT
    online_order,
    COUNT(*)                     AS count,
    ROUND(AVG(rate_numeric), 3)  AS avg_rating,
    ROUND(MIN(rate_numeric), 2)  AS min_rating,
    ROUND(MAX(rate_numeric), 2)  AS max_rating,
    ROUND(AVG(votes), 1)         AS avg_votes
FROM zomato
WHERE rate_numeric IS NOT NULL
GROUP BY online_order;


-- ==========================================================
-- Q4. Price segment analysis with rating breakdown
-- ==========================================================
SELECT
    cost_bucket,
    COUNT(*)                              AS restaurant_count,
    ROUND(AVG(rate_numeric), 3)           AS avg_rating,
    ROUND(MEDIAN(rate_numeric), 3)        AS median_rating,  -- PostgreSQL: PERCENTILE_CONT(0.5)
    ROUND(AVG(votes), 1)                  AS avg_votes,
    ROUND(100.0 * SUM(CASE WHEN online_order THEN 1 ELSE 0 END) / COUNT(*), 1) AS online_order_pct
FROM zomato
GROUP BY cost_bucket
ORDER BY AVG(approx_cost);


-- ==========================================================
-- Q5. Top cuisines by restaurant count + avg rating
-- ==========================================================
SELECT
    primary_cuisine,
    COUNT(*)                     AS restaurant_count,
    ROUND(AVG(rate_numeric), 3)  AS avg_rating,
    ROUND(AVG(approx_cost), 2)   AS avg_cost,
    SUM(votes)                   AS total_votes
FROM zomato
GROUP BY primary_cuisine
HAVING COUNT(*) >= 30
ORDER BY restaurant_count DESC
LIMIT 20;


-- ==========================================================
-- Q6. Table booking vs no-booking: multi-metric comparison
-- ==========================================================
SELECT
    book_table,
    COUNT(*)                     AS count,
    ROUND(AVG(rate_numeric), 3)  AS avg_rating,
    ROUND(AVG(approx_cost), 2)   AS avg_cost,
    ROUND(AVG(votes), 1)         AS avg_votes
FROM zomato
GROUP BY book_table;


-- ==========================================================
-- Q7. Window function: Location ranking by avg rating
-- ==========================================================
SELECT
    location,
    restaurant_count,
    avg_rating,
    RANK()       OVER (ORDER BY avg_rating DESC)       AS rating_rank,
    DENSE_RANK() OVER (ORDER BY restaurant_count DESC) AS density_rank,
    NTILE(4)     OVER (ORDER BY avg_rating DESC)       AS rating_quartile
FROM (
    SELECT
        location,
        COUNT(*)                   AS restaurant_count,
        ROUND(AVG(rate_numeric), 3) AS avg_rating
    FROM zomato
    GROUP BY location
    HAVING COUNT(*) >= 30
) loc_stats
ORDER BY rating_rank;


-- ==========================================================
-- Q8. CTE: Best value locations (high rating, low cost)
-- ==========================================================
WITH location_stats AS (
    SELECT
        location,
        COUNT(*)                    AS cnt,
        ROUND(AVG(rate_numeric), 3) AS avg_rating,
        ROUND(AVG(approx_cost), 2)  AS avg_cost
    FROM zomato
    GROUP BY location
    HAVING COUNT(*) >= 30
),
medians AS (
    SELECT
        ROUND(AVG(avg_rating), 3) AS median_rating,
        ROUND(AVG(avg_cost), 2)   AS median_cost
    FROM location_stats
)
SELECT
    ls.location,
    ls.cnt,
    ls.avg_rating,
    ls.avg_cost,
    CASE
        WHEN ls.avg_rating >= m.median_rating AND ls.avg_cost <= m.median_cost THEN 'Best Value'
        WHEN ls.avg_rating >= m.median_rating AND ls.avg_cost >  m.median_cost THEN 'Premium Quality'
        WHEN ls.avg_rating <  m.median_rating AND ls.avg_cost <= m.median_cost THEN 'Budget Underperformer'
        ELSE 'Overpriced'
    END AS quadrant
FROM location_stats ls
CROSS JOIN medians m
ORDER BY ls.avg_rating DESC;


-- ==========================================================
-- Q9. Running total of restaurants by location (cumulative)
-- ==========================================================
SELECT
    location,
    restaurant_count,
    SUM(restaurant_count) OVER (ORDER BY restaurant_count DESC
                                 ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_count,
    ROUND(100.0 * SUM(restaurant_count) OVER (ORDER BY restaurant_count DESC
                                               ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
          / SUM(restaurant_count) OVER (), 2) AS cumulative_pct
FROM (
    SELECT location, COUNT(*) AS restaurant_count FROM zomato GROUP BY location
)
ORDER BY restaurant_count DESC
LIMIT 20;


-- ==========================================================
-- Q10. Top-rated restaurants per location (Window PARTITION)
-- ==========================================================
WITH ranked AS (
    SELECT
        name,
        location,
        primary_cuisine,
        rate_numeric,
        votes,
        approx_cost,
        ROW_NUMBER() OVER (
            PARTITION BY location
            ORDER BY rate_numeric DESC, votes DESC
        ) AS rn
    FROM zomato
    WHERE votes >= 100 AND rate_numeric IS NOT NULL
)
SELECT * FROM ranked
WHERE rn <= 3
ORDER BY location, rn;


-- ==========================================================
-- Q11. Cuisine × Location: cross-tab average rating
-- ==========================================================
SELECT
    location,
    primary_cuisine,
    COUNT(*)                    AS count,
    ROUND(AVG(rate_numeric), 2) AS avg_rating,
    ROUND(AVG(approx_cost), 2)  AS avg_cost
FROM zomato
WHERE location IN (
    SELECT location FROM zomato
    GROUP BY location ORDER BY COUNT(*) DESC LIMIT 10
)
AND primary_cuisine IN (
    SELECT primary_cuisine FROM zomato
    GROUP BY primary_cuisine ORDER BY COUNT(*) DESC LIMIT 8
)
GROUP BY location, primary_cuisine
ORDER BY location, avg_rating DESC;


-- ==========================================================
-- Q12. Votes percentile analysis
-- ==========================================================
SELECT
    ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY votes), 0) AS p50_votes,
    ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY votes), 0) AS p75_votes,
    ROUND(PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY votes), 0) AS p90_votes,
    ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY votes), 0) AS p95_votes,
    ROUND(PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY votes), 0) AS p99_votes,
    MAX(votes)                                                      AS max_votes
FROM zomato;
-- SQLite alternative: use ntile workaround or Python


-- ==========================================================
-- Q13. Market gap analysis: high rated but low count cuisines
-- ==========================================================
WITH cuisine_stats AS (
    SELECT
        primary_cuisine,
        COUNT(*) AS cnt,
        ROUND(AVG(rate_numeric), 3) AS avg_rating
    FROM zomato
    GROUP BY primary_cuisine
)
SELECT *
FROM cuisine_stats
WHERE cnt < 100 AND avg_rating >= 4.0
ORDER BY avg_rating DESC, cnt ASC;


-- ==========================================================
-- Q14. Full-service premium: online_order + book_table combo
-- ==========================================================
SELECT
    online_order,
    book_table,
    COUNT(*)                    AS count,
    ROUND(AVG(rate_numeric), 3) AS avg_rating,
    ROUND(AVG(approx_cost), 2)  AS avg_cost,
    ROUND(AVG(votes), 1)        AS avg_votes
FROM zomato
GROUP BY online_order, book_table
ORDER BY avg_rating DESC;


-- ==========================================================
-- Q15. Online order penetration by location
-- ==========================================================
SELECT
    location,
    COUNT(*)                                                                   AS total,
    SUM(CASE WHEN online_order THEN 1 ELSE 0 END)                             AS online_count,
    ROUND(100.0 * SUM(CASE WHEN online_order THEN 1 ELSE 0 END) / COUNT(*), 2) AS online_pct
FROM zomato
GROUP BY location
HAVING COUNT(*) >= 30
ORDER BY online_pct DESC;


-- ==========================================================
-- Q16. CTE: High-vote, low-rating anomalies (problematic restaurants)
-- ==========================================================
WITH percentiles AS (
    SELECT PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY votes) AS p90_votes
    FROM zomato
)
SELECT
    z.name, z.location, z.primary_cuisine,
    z.rate_numeric, z.votes, z.approx_cost
FROM zomato z, percentiles p
WHERE z.votes >= p.p90_votes
  AND z.rate_numeric < 3.5
ORDER BY z.votes DESC
LIMIT 15;


-- ==========================================================
-- Q17. YOY-like: Restaurant count by price bucket + cuisine
-- ==========================================================
SELECT
    cost_bucket,
    primary_cuisine,
    COUNT(*) AS count,
    ROUND(AVG(rate_numeric), 2) AS avg_rating
FROM zomato
WHERE primary_cuisine IN (
    SELECT primary_cuisine FROM zomato
    GROUP BY primary_cuisine ORDER BY COUNT(*) DESC LIMIT 5
)
GROUP BY cost_bucket, primary_cuisine
ORDER BY cost_bucket, count DESC;


-- ==========================================================
-- Q18. Window LAG: rank shift from votes to ratings
-- ==========================================================
WITH loc_ranks AS (
    SELECT
        location,
        COUNT(*) AS cnt,
        ROUND(AVG(rate_numeric), 3) AS avg_rating,
        ROUND(AVG(votes), 1) AS avg_votes
    FROM zomato GROUP BY location HAVING COUNT(*) >= 30
)
SELECT
    location,
    cnt,
    avg_rating,
    avg_votes,
    RANK() OVER (ORDER BY avg_rating DESC) AS rating_rank,
    RANK() OVER (ORDER BY avg_votes DESC)  AS votes_rank,
    RANK() OVER (ORDER BY avg_rating DESC) - RANK() OVER (ORDER BY avg_votes DESC) AS rank_shift
FROM loc_ranks
ORDER BY rank_shift DESC;


-- ==========================================================
-- Q19. Budget segment leaders (cost ≤ 300, high rating)
-- ==========================================================
SELECT
    name, location, primary_cuisine,
    rate_numeric, votes, approx_cost
FROM zomato
WHERE approx_cost <= 300
  AND rate_numeric >= 4.0
  AND votes >= 50
ORDER BY rate_numeric DESC, votes DESC
LIMIT 20;


-- ==========================================================
-- Q20. Executive KPI rollup
-- ==========================================================
SELECT
    COUNT(*)                                                AS total_restaurants,
    COUNT(DISTINCT location)                                AS unique_locations,
    COUNT(DISTINCT primary_cuisine)                         AS unique_cuisines,
    ROUND(AVG(rate_numeric), 2)                             AS avg_rating,
    ROUND(AVG(approx_cost), 2)                              AS avg_cost_for_two,
    ROUND(100.0 * SUM(CASE WHEN online_order THEN 1 ELSE 0 END) / COUNT(*), 1) AS online_order_pct,
    ROUND(100.0 * SUM(CASE WHEN book_table  THEN 1 ELSE 0 END) / COUNT(*), 1) AS book_table_pct,
    ROUND(100.0 * SUM(CASE WHEN rate_numeric >= 4.0 THEN 1 ELSE 0 END)
                / SUM(CASE WHEN rate_numeric IS NOT NULL THEN 1 END), 1)       AS high_rated_pct,
    SUM(votes)                                              AS total_votes
FROM zomato;


-- ==========================================================
-- Q21. Cuisine popularity trend (votes as proxy for demand)
-- ==========================================================
SELECT
    primary_cuisine,
    COUNT(*)                    AS restaurant_count,
    SUM(votes)                  AS total_votes,
    ROUND(AVG(votes), 1)        AS avg_votes_per_restaurant,
    ROUND(AVG(rate_numeric), 2) AS avg_rating
FROM zomato
GROUP BY primary_cuisine
HAVING COUNT(*) >= 30
ORDER BY avg_votes_per_restaurant DESC
LIMIT 15;


-- ==========================================================
-- Q22. Restaurant type performance matrix
-- ==========================================================
SELECT
    primary_rest_type,
    COUNT(*)                    AS count,
    ROUND(AVG(rate_numeric), 3) AS avg_rating,
    ROUND(AVG(approx_cost), 2)  AS avg_cost,
    ROUND(AVG(votes), 1)        AS avg_votes,
    ROUND(100.0 * SUM(CASE WHEN online_order THEN 1 ELSE 0 END) / COUNT(*), 1) AS online_pct,
    ROUND(100.0 * SUM(CASE WHEN book_table  THEN 1 ELSE 0 END) / COUNT(*), 1) AS booking_pct
FROM zomato
GROUP BY primary_rest_type
HAVING COUNT(*) >= 50
ORDER BY avg_rating DESC;


-- ==========================================================
-- Q23. Pareto analysis: 80/20 of restaurants driving 80% votes
-- ==========================================================
WITH vote_rank AS (
    SELECT
        name, location, votes,
        SUM(votes) OVER (ORDER BY votes DESC
                          ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cum_votes,
        SUM(votes) OVER () AS total_votes,
        ROW_NUMBER() OVER (ORDER BY votes DESC) AS rn,
        COUNT(*) OVER () AS total_count
    FROM zomato
)
SELECT
    rn,
    name,
    location,
    votes,
    ROUND(100.0 * cum_votes / total_votes, 2) AS cumulative_vote_pct,
    ROUND(100.0 * rn / total_count, 2)         AS cumulative_restaurant_pct
FROM vote_rank
WHERE cumulative_vote_pct <= 80
ORDER BY rn
LIMIT 50;


-- ==========================================================
-- Q24. Recursive CTE: Location hierarchy simulation
-- (PostgreSQL only — simulates area grouping)
-- ==========================================================
WITH RECURSIVE area_hierarchy AS (
    -- Base: distinct locations
    SELECT DISTINCT location AS area, location AS sub_area, 0 AS level
    FROM zomato

    UNION ALL

    -- Recursive: group by first word of location name as parent
    SELECT
        SPLIT_PART(ah.area, ' ', 1) AS area,
        ah.area AS sub_area,
        ah.level + 1
    FROM area_hierarchy ah
    WHERE ah.level = 0
      AND SPLIT_PART(ah.area, ' ', 1) != ah.area
)
SELECT area, COUNT(DISTINCT sub_area) AS sub_areas
FROM area_hierarchy
WHERE level = 1
GROUP BY area
ORDER BY sub_areas DESC
LIMIT 10;


-- ==========================================================
-- Q25. Full business summary — combined CTE
-- ==========================================================
WITH
base AS (SELECT * FROM zomato WHERE rate_numeric IS NOT NULL),
loc_top AS (
    SELECT location, COUNT(*) AS n FROM base
    GROUP BY location ORDER BY n DESC LIMIT 1
),
cuisine_top AS (
    SELECT primary_cuisine, COUNT(*) AS n FROM base
    GROUP BY primary_cuisine ORDER BY n DESC LIMIT 1
),
type_top AS (
    SELECT primary_rest_type, COUNT(*) AS n FROM base
    GROUP BY primary_rest_type ORDER BY n DESC LIMIT 1
)
SELECT
    (SELECT COUNT(*) FROM base)                         AS total_restaurants,
    (SELECT ROUND(AVG(rate_numeric),2) FROM base)       AS avg_rating,
    (SELECT ROUND(AVG(approx_cost),2) FROM base)        AS avg_cost,
    (SELECT location FROM loc_top)                      AS dominant_location,
    (SELECT primary_cuisine FROM cuisine_top)           AS dominant_cuisine,
    (SELECT primary_rest_type FROM type_top)            AS dominant_rest_type,
    (SELECT ROUND(100.0*SUM(CASE WHEN online_order THEN 1 ELSE 0 END)/COUNT(*),1) FROM base) AS online_pct;
