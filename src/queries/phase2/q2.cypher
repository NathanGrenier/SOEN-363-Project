// A query that provides some aggregate data (i.e. number of entities satisfying a criteria)

MATCH (b:Book)
WHERE b.averageRating > 4
RETURN count(b) AS books_with_rating_over_4;
