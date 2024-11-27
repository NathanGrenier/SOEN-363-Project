CREATE INDEX IF NOT EXISTS FOR (b:Book) ON (b.ratingsCount);

CREATE INDEX IF NOT EXISTS FOR (b:Book) ON (b.averageRating);

CREATE INDEX IF NOT EXISTS FOR (b:Book) ON (b.ratingsCount, b.averageRating);

CREATE INDEX IF NOT EXISTS FOR (b:Book) ON (b.publishDate);

CREATE INDEX IF NOT EXISTS FOR (b:Book) ON (b.pageCount);

CREATE INDEX IF NOT EXISTS FOR (c:Category) ON (c.name);

CREATE FULLTEXT INDEX bookDescriptions IF NOT EXISTS FOR (b:Book) ON EACH [b.description];
