-- A few queries to demonstrate various `JOIN` **types** on the same tables: `INNER` vs. `OUTER` (left and right) vs. `FULL JOIN`. (Use of null values in the database to show the differences is required)

-- INNER JOIN
SELECT 
    b.B_ID,
	b.B_ISBN13,
	b.B_Title, 
    a.AW_NAME, 
    a.AW_YEAR 
FROM Book b
INNER JOIN Award a ON b.B_ID = a.B_ID;

-- OUTER LEFT JOIN
SELECT 
    b.B_ID,
	b.B_ISBN13,
    b.B_Title, 
    a.AW_NAME, 
    a.AW_YEAR 
FROM Book b
LEFT JOIN Award a ON b.B_ID = a.B_ID;

-- OUTER RIGHT JOIN
SELECT 
    b.B_ID,
	b.B_ISBN13,
    b.B_Title, 
    a.AW_NAME, 
    a.AW_YEAR 
FROM Book b
RIGHT JOIN Award a ON b.B_ID = a.B_ID;

-- FULL JOIN
SELECT 
    b.B_ID,
	b.B_ISBN13,
    b.B_Title, 
    a.AW_NAME, 
    a.AW_YEAR 
FROM Book b
FULL JOIN Award a ON b.B_ID = a.B_ID;