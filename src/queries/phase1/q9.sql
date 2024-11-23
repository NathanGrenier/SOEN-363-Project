-- Two queries that demonstrate the **overlap** and **covering** constraints. 

-- Overlap: Find books that are available in both physical and ebook formats  (should return noting)
SELECT b.B_TITLE, b.B_ISBN13
FROM Book b
WHERE EXISTS (
    SELECT 1 FROM Physical_Book pb WHERE pb.B_ID = b.B_ID
)
AND EXISTS (
    SELECT 1 FROM Ebook eb WHERE eb.B_ID = b.B_ID
);

-- Covering: Find books that are neither physical books nor ebooks (should be none as we enforce that all books are either physical or ebook)
SELECT b.B_TITLE, b.B_ISBN13
FROM Book b
WHERE NOT EXISTS (
    SELECT 1 FROM Physical_Book pb WHERE pb.B_ID = b.B_ID
)
AND NOT EXISTS (
    SELECT 1 FROM Ebook eb WHERE eb.B_ID = b.B_ID
);