// Find top n entities satisfying a criteria, sorted by an attribute.

MATCH (b:Book)
WHERE b.ratingsCount > 5
RETURN b.title, b.ratingsCount, b.averageRating
 ORDER BY b.averageRating DESC
LIMIT 20;
