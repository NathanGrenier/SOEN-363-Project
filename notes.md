# Part 0
- [x] Consume 2 APIs

# Part 1
## Database Design Requirements
- [x] Proper use of: 
  - Keys
  - Indexes
  - Integrity constraints
- [x] How you provide the **link** between the two data sources. Answer: We use the book's ISBN.
- [x] At least 1 **IS-A** relationship
- [x] At least 1 example of a **weak entity**
- [x] An example of a complex referential integrity (i.e. using **assertions** or **triggers**).
- [x] Use of **domains** and **types**. (A couple examples)
- [x] Make sure that no **real domain data** (ex: isbn) is used as internal keys (primary / foreign)
- [x] Examples of a hard-coded **views** that filters some rows and columns, based on the **user access rights** (i.e. a full access user may see all columns while a low-key user may only see certain columns and for a subset of data).

## Query Implementation
Demonstrate the following query types:
- [ ] Basic `SELECT` with simple `WHERE` clause.
- [ ] Basic `SELECT` with simple `GROUP BY` clause (with and without having clause).
- [ ] A simple `JOIN` query. 
  - [ ] As well as its **equivalent implementation** using cartesian product and where clause.
- [ ] A few queries to demonstrate various `JOIN` **types** on the same tables: `INNER` vs. `OUTER` (left and right) vs. `FULL JOIN`. (Use of null values in the database to show the differences is required)
- [ ] A few queries to demonstrate use of `NULL` values for undefined / non-applicable.
- [ ] A couple of examples to demonstrate correlated queries.
- [ ] One example per set operations: `INTERSECT`, `UNION`, and `DIFFERENCE`. 
  - [ ] Their **equivalences** without using set operations.
- [ ] An example of a **view** that has a hard-coded criteria, by which the content of the view may change upon changing the hard-coded value (see L09 slide 24).
- [ ] Two queries that demonstrate the **overlap** and **covering** constraints. 
- [ ] Two implementations of the **division operator** using:
  - [ ] A regular nested query using `NOT IN` 
  - [ ] A correlated nested query using `NOT EXISTS` and `EXCEPT` ([SQL Division](https://www.geeksforgeeks.org/sql-division/)).
  > Note: If your database domain does not address this, create a simple data with a few entries (at least 4) and demonstrate an example of a SQL division.

## Report
Your final submission will include a report document that provides an overview of your system as well the data model and the approach / challenges you faces in populating the data.

# Part 2