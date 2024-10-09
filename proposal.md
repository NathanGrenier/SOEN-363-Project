# Project Proposal

Database Project Phase 0

SOEN 363: Data Systems for Software Engineers

# 1. Description 
**Topic:** Library of Alexandria

This project aims to create a comprehensive database of books by integrating data from multiple sources. The goal is to create a simple yet complete structure for data on various book entries found on public sources.

# 2. Implementation details 

## 2.1 Data Sources

| Source                                     | API Type | Docs                                                                                                          |
| ------------------------------------------ | -------- | ------------------------------------------------------------------------------------------------------------- |
| https://openlibrary.org/developers/api     | REST     | https://openlibrary.org/developers/api                                                                        |
| https://reststop.randomhouse.com/resources | REST     | https://www.penguinrandomhouse.biz/webservices/rest/, https://developer.penguinrandomhouse.com/docs/read/Home |

### Proposed Entity Relation Diagram

ER Diagram Representing the Proposed Database:

![ER Diagram](/diagrams/out/ER-diagram/ER-diagram.png)
## 2.2 Implementation Platforms

**RDBMS:** PostgreSQL

**NoSQL System:** MongoDB

> [Data migration](https://www.mongodb.com/resources/compare/mongodb-postgresql/dsl-migrating-postgres-to-mongodb) from postgreSQL to MongoDB 

## 2.3 Programming Platform 

- Python (scraping, formatting/normalizing)
- Docker (hosting)

# 3. Estimated Data Collection Plan  

**Target:** 0.5 GB of data.

| Date       | Data Size |
| ---------- | --------- |
| 2024/10/14 | ~40MB     |
| 2024/10/15 | ~40MB     |
| 2024/10/16 | ~40MB     |
| 2024/10/17 | ~40MB     |
| 2024/10/18 | ~40MB     |
| 2024/10/19 | ~40MB     |
| 2024/10/20 | ~40MB     |
| 2024/10/21 | ~40MB     |
| 2024/10/22 | ~40MB     |
| 2024/10/23 | ~40MB     |
| 2024/10/24 | ~40MB     |
| 2024/10/25 | ~40MB     |
| 2024/10/26 | ~40MB     |

## Notes

- While using cloud services are encourages, note that at the end you must submit your database in the system. The submission includes the DDL and the DML queries + the script code in zip format. Details will be posted in the project specification document.
> Dump Database into single file: https://www.postgresql.org/docs/current/backup.html
