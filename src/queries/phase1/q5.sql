-- A few queries to demonstrate use of `NULL` values for undefined / non-applicable.

-- Books without any ratings
SELECT 
    B_TITLE,
    B_ISBN13,
    B_AVERAGE_RATING,
    B_RATING_COUNT
FROM Book
ORDER BY B_AVERAGE_RATING ASC;

-- Books without any awards
SELECT 
    b.B_Title, 
    a.AW_NAME, 
    a.AW_YEAR 
FROM Book b
LEFT JOIN Award a ON b.B_ID = a.B_ID
ORDER BY a.AW_NAME ASC;