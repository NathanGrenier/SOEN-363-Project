// Build the appropriate indexes for previous queries, report the index creation statement and the query execution time before and after you create the index.

// Index 1:
CREATE INDEX IF NOT EXISTS FOR (b:Book) ON (b.ratingsCount);

// Query 1:
MATCH (b:Book { ratingsCount: 5 })
RETURN b.title, b.ratingsCount;

// Performance Comparison (Accomplished by adding the PROFILE clause to the beginning of the query)

// Without Index: ~51ms
// With Index: ~1ms

// Index 2:
CREATE INDEX IF NOT EXISTS FOR (b:Book) ON (b.averageRating);

// Query 2:
MATCH (b:Book)
WHERE b.averageRating > 4
RETURN count(b) AS books_with_rating_over_4;

// Performance Comparison (Accomplished by adding the PROFILE clause to the beginning of the query)

// Without Index: ~55ms
// With Index: ~1ms

// Index 3:
CREATE INDEX IF NOT EXISTS FOR (b:Book) ON (b.ratingsCount, b.averageRating);

// Query 3:
MATCH (b:Book)
WHERE b.ratingsCount > 5
RETURN b.title, b.ratingsCount, b.averageRating
 ORDER BY b.averageRating DESC
LIMIT 20;

// Performance Comparison (Accomplished by adding the PROFILE clause to the beginning of the query)

// Without Index: ~20ms
// With Index: ~1ms

// Index 4:
CREATE INDEX IF NOT EXISTS FOR (b:Book) ON (b.publishDate);

CREATE INDEX IF NOT EXISTS FOR (b:Book) ON (b.pageCount);

CREATE INDEX IF NOT EXISTS FOR (c:Category) ON (c.name);

// Query 4:
MATCH (b:Book)-[:IN_CATEGORY]->(c:Category)
WHERE b.averageRating <> -1 AND b.publishDate <> -1
WITH c.name AS CategoryName,
COUNT(b) AS BookCount,
AVG(b.averageRating) AS AvgCategoryRating,
MIN(b.publishDate) AS EarliestBookYear,
MAX(b.publishDate) AS LatestBookYear,
SUM(b.pageCount) AS TotalPagesInCategory
RETURN CategoryName,
BookCount,
ROUND(AvgCategoryRating, 2) AS AvgCategoryRating,
EarliestBookYear,
LatestBookYear,
TotalPagesInCategory
 ORDER BY BookCount DESC
LIMIT 20;

// Performance Comparison (Accomplished by adding the PROFILE clause to the beginning of the query)

// Without Index: ~230ms
// With Index: ~300ms
