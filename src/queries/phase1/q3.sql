-- A simple `JOIN` query. As well as its **equivalent implementation** using cartesian product and where clause.

-- Simple JOIN query
SELECT 
    b.B_ID,
	b.B_TITLE,
    b.B_ISBN13,
    a.A_NAME as author_name
FROM Book b
JOIN Book_Author ba ON b.B_ID = ba.B_ID
JOIN Author a ON ba.A_ID = a.A_ID
ORDER BY b.B_ID;

-- Cartesian product and where clause equivalent
SELECT 
    b.B_ID,
	b.B_TITLE,
    b.B_ISBN13,
    a.A_NAME as author_name
FROM Book b, Book_Author ba, Author a
WHERE b.B_ID = ba.B_ID 
    AND ba.A_ID = a.A_ID
ORDER BY b.B_ID;