// Simulate a relational group by query in NoSQL (aggregate per category).

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
