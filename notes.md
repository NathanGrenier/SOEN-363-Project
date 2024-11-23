# Part 0
- [x] Consume 2 APIs

# Part 1
Submit: 
- [x] Code (data creation / population).
- [x] DDL and DML queries. Required to remove unnecessary / conditional imports from your script. 
- [x] Data Model (ERD) of your database.
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
- [x] Basic `SELECT` with simple `WHERE` clause.
- [x] Basic `SELECT` with simple `GROUP BY` clause (with and without having clause).
- [x] A simple `JOIN` query. 
  - [x] As well as its **equivalent implementation** using cartesian product and where clause.
- [x] A few queries to demonstrate various `JOIN` **types** on the same tables: `INNER` vs. `OUTER` (left and right) vs. `FULL JOIN`. (Use of null values in the database to show the differences is required)
- [x] A few queries to demonstrate use of `NULL` values for undefined / non-applicable.
- [x] A couple of examples to demonstrate correlated queries.
- [x] One example per set operations: `INTERSECT`, `UNION`, and `DIFFERENCE`. 
  - [x] Their **equivalences** without using set operations.
- [x] An example of a **view** that has a hard-coded criteria, by which the content of the view may change upon changing the hard-coded value (see L09 slide 24).
- [x] Two queries that demonstrate the **overlap** and **covering** constraints. 
- [x] Two implementations of the **division operator** using:
  - [x] A regular nested query using `NOT IN` 
  - [x] A correlated nested query using `NOT EXISTS` and `EXCEPT` ([SQL Division](https://www.geeksforgeeks.org/sql-division/)).
  > Note: If your database domain does not address this, create a simple data with a few entries (at least 4) and demonstrate an example of a SQL division.

# Part 2
Submit:
- [ ] Code (data creation / population) 
- [ ] Queries
- [ ] Data model
- [ ] Final report that provides an overview of your system as well as the approach you used and possible challenges you faced in populating data.
## Data Transfer

You must transfer the data from the relational database you created in Phase I into a NoSQL database. The goal of the project is to make sure the data is completely transferred into the NoSQL so that the performance of the data access as well as query options are compared.

> You may slightly modify the database model while you transfer the data into the new plat form. Examples are: 
> - Removing the IS-A relationships in phase I
> - Storing Weak entities as part of the data associated within main entities.

## Query Implementation

- [ ] A basic search query on an attribute value.
- [ ] A query that provides some aggregate data (i.e. number of entities satisfying a criteria)
- [ ] Find top n entities satisfying a criteria, sorted by an attribute.
- [ ] Simulate a relational group by query in NoSQL (aggregate per category).
- [ ] Build the appropriate indexes for previous queries, report the index creation statement and the query execution time before and after you create the index.
- [ ] Demonstrate a full text search. Show the performance improvement by using indexes.

# Final Report
Your final submission will include a report document that provides an overview of your system as well the data model and the approach / challenges you faces in populating the data.



# Final Presentation
Your project requires a final presentation, during which you demonstrate both databases and compare the data models. 
 
The presentation may be 10-15 minutes long. 

During the presentation you are expected to demonstrate: 
- How you populated the data in the relational database 
- How you transferred the data into the NoSQL platform. 
- Include some previews of code snippets. 
- Demonstrate major queries you created in both Relational and in the NoSQL database. 
- You may compare the data models and the changes in the two platforms, if necessary.

# Peer Review
