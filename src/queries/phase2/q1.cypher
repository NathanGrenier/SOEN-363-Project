// A basic search query on an attribute value.

MATCH (b:Book { ratingsCount: 5 })
RETURN b.title, b.ratingsCount;
