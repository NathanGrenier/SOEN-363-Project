// Demonstrate a full text search. Show the performance improvement by using indexes.

// Index
CREATE FULLTEXT INDEX bookDescriptions IF NOT EXISTS FOR (b:Book) ON EACH [b.description];

// Full Text Search Query (Without Full Text Index)
MATCH (n:Book)
WHERE n.description =~ '.*fight.*'
RETURN n.title, n.description
LIMIT 500;

// Full Text Search Query (With Full Text Index)
CALL db.index.fulltext.queryNodes("bookDescriptions", "fight") YIELD node, score
RETURN node.title, score, node.description
LIMIT 500;

// Performance Comparison (Accomplished by adding the PROFILE clause to the beginning of the query)

// Without Index: ~200ms
// With Index: ~6ms
