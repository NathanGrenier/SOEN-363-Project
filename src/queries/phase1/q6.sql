-- A couple of examples to demonstrate correlated queries.

-- Books with more awards than average
WITH AverageAwards AS (
    SELECT AVG(B_AWARD_COUNT) AS average_award_count
    FROM Book
)
SELECT
    b.B_Title,
    b.B_AWARD_COUNT,
    (SELECT average_award_count FROM AverageAwards) AS average_award_count
FROM
    Book b
WHERE
    b.B_AWARD_COUNT > (SELECT average_award_count FROM AverageAwards);

-- Book with the highest price in each currency
SELECT
    P.P_CURRENCY,
    B.B_TITLE,
    P.P_PRICE
FROM
    Price P
JOIN Book B ON P.B_ID = B.B_ID
WHERE
    P.P_PRICE = (
        SELECT
            MAX(P2.P_PRICE)
        FROM
            Price P2
        WHERE
            P2.P_CURRENCY = P.P_CURRENCY
    )
GROUP BY
    P.P_CURRENCY, B.B_TITLE, P.P_PRICE;