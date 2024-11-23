-- Two implementations of the **division operator** using:
-- 1. A regular nested query using `NOT IN`
-- 2. A correlated nested query using `NOT EXISTS` and `EXCEPT`

-- Subset of categories we want to check against
WITH SciFiFantasyCategories AS (
    SELECT C_ID 
    FROM Category 
    WHERE C_NAME IN ('Science Fiction', 'Fantasy')
)

-- Implementation 1: Using NOT IN
SELECT DISTINCT a.A_ID, a.A_NAME
FROM Author a
WHERE a.A_ID NOT IN (
    SELECT DISTINCT a2.A_ID
    FROM Author a2
    CROSS JOIN SciFiFantasyCategories sfc
    EXCEPT
    SELECT DISTINCT ba.A_ID
    FROM Book_Author ba
    JOIN Book_Category bc ON ba.B_ID = bc.B_ID
    WHERE bc.C_ID IN (SELECT C_ID FROM SciFiFantasyCategories)
)
LIMIT 100;

-- Implementation 2: Using NOT EXISTS with correlated subquery and EXCEPT
SELECT DISTINCT a.A_ID, a.A_NAME
FROM Author a
WHERE NOT EXISTS (
    -- Categories that the author doesn't write in
    SELECT C_ID 
    FROM SciFiFantasyCategories
    
    EXCEPT
    
    -- Categories the author has written in
    SELECT bc.C_ID
    FROM Book_Category bc
    JOIN Book_Author ba ON bc.B_ID = ba.B_ID
    WHERE ba.A_ID = a.A_ID
)
LIMIT 100;