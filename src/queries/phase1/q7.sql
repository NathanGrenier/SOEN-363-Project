-- One example per set operations: `INTERSECT`, `UNION`, and `DIFFERENCE`. Also include their **equivalences** without using set operations.

-- `INTERSECT` example: Find the books that are physical and have a price in USD
SELECT 
    B.B_TITLE,
    B.B_IS_PHYSICAL
FROM Book B
JOIN Physical_Book PB ON B.B_ID = PB.B_ID
JOIN Price P ON B.B_ID = P.B_ID
WHERE P.P_CURRENCY = 'USD'
INTERSECT
SELECT 
	B.B_TITLE,
    B.B_IS_PHYSICAL
FROM Book B
JOIN Physical_Book PB ON B.B_ID = PB.B_ID
ORDER BY 1;

-- `INTERSECT` equivalence
SELECT 
    B.B_TITLE,
    B.B_IS_PHYSICAL
FROM Book B
JOIN Physical_Book PB ON B.B_ID = PB.B_ID
WHERE EXISTS (
    SELECT 1
    FROM Price P
    WHERE P.B_ID = B.B_ID
    AND P.P_CURRENCY = 'USD'
)
ORDER BY 1;

-- `UNION` example
SELECT 
	B_TITLE, 
	B_ISBN13
FROM Book
WHERE B_AVERAGE_RATING > 4.5
UNION
SELECT 
	B_TITLE, 
	B_ISBN13
FROM Book
WHERE B_AWARD_COUNT > 2;

-- `UNION` equivalence
SELECT DISTINCT 
	B_TITLE,
	B_ISBN13
FROM Book
WHERE B_AVERAGE_RATING > 4.5 
   OR B_AWARD_COUNT > 2;

-- `DIFFERENCE` example: Show the books that are physical but do not have a price in CAD
SELECT 
	B.B_TITLE,
	B.B_IS_PHYSICAL
FROM Book B
JOIN Physical_Book PB ON B.B_ID = PB.B_ID
EXCEPT
SELECT 
	B.B_TITLE,
	B.B_IS_PHYSICAL
FROM Book B
JOIN Price P ON B.B_ID = P.B_ID
WHERE P.P_CURRENCY = 'CAD';

-- `DIFFERENCE` equivalence
SELECT 
	B.B_TITLE,
	B.B_IS_PHYSICAL
FROM Book B
JOIN Physical_Book PB ON B.B_ID = PB.B_ID
WHERE NOT EXISTS (
    SELECT 1
    FROM Price P
    WHERE P.B_ID = B.B_ID
    AND P.P_CURRENCY = 'CAD'
);