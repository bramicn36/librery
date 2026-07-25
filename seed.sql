INSERT INTO authors (name, country) VALUES
('Jane Austen', 'England'),
('Gabriel García Márquez', 'Colombia'),
('Haruki Murakami', 'Japan');

INSERT INTO books (title, author_id, year, available) VALUES
('Pride and Prejudice', 1, 1813, TRUE),
('Emma', 1, 1815, FALSE),
('One Hundred Years of Solitude', 2, 1967, TRUE),
('Love in the Time of Cholera', 2, 1985, FALSE),
('Norwegian Wood', 3, 1987, TRUE),
('Kafka on the Shore', 3, 2002, TRUE);

INSERT INTO loans (book_id, borrower, loan_date, return_date) VALUES
(2, 'John Smith', '2026-03-15', NULL),
(4, 'Maria Garcia', '2026-03-20', NULL),
(6, 'David Cohen', '2026-02-01', '2026-02-28');
