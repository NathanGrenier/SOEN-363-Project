-- An example of a **view** that has a hard-coded criteria, by which the content of the view may change upon changing the hard-coded value (see L09 slide 24).

CREATE VIEW expensive_books AS
SELECT
    b.B_TITLE,
    p.P_PRICE
FROM
    Book b
JOIN Price p ON b.B_ID = p.B_ID
WHERE
    p.P_PRICE > 100 -- Hard-coded price threshold
ORDER BY p.P_PRICE ASC;