-- Basic `SELECT` with simple `GROUP BY` clause (with and without `HAVING` clause).

-- Without `HAVING` clause
SELECT 
    B_PUBLISHER,
    COUNT(*) as books_published,
    ROUND(AVG(B_AVERAGE_RATING), 2) as avg_rating
FROM Book
GROUP BY B_PUBLISHER
ORDER BY books_published DESC;

-- With `HAVING` clause
SELECT 
    B_PUBLISHER,
    COUNT(*) as books_published,
    ROUND(AVG(B_AVERAGE_RATING), 2) as avg_rating
FROM Book
GROUP BY B_PUBLISHER
HAVING COUNT(*) > 100 
    AND AVG(B_AVERAGE_RATING) > 4.0
ORDER BY avg_rating DESC;