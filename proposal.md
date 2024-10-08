# Project Proposal

Database Project Phase 0

SOEN 363: Data Systems for Software Engineers

# 1. Description 
**Topic:** Tracking SpaceX Launch Details

This project aims to create a comprehensive database on historical SpaceX rocket launches by integrating data from multiple sources. The goal is to create a simple yet complete structure for all SpaceX rocket launches, ensuring that all key aspects of the launch data are captured and organized efficiently. 

# 2. Implementation details 

## 2.1 Data Sources

| Source                            | API Type | Docs                                   |
| --------------------------------- | -------- | -------------------------------------- |
| https://www.rocketlaunch.live/api | REST     | https://www.rocketlaunch.live/api      |
| https://api.spacexdata.com/       | REST     | https://github.com/r-spacex/SpaceX-API |

### Proposed Entity Relation Diagram

ER Diagram Representing the Proposed Database:

![ER Diagram](/diagrams/out/ER-diagram/ER-diagram.png)
## 2.2 Implementation Platforms

**RDBMS:** PostgreSQL

**NoSQL System:** MongoDB

> [Data migration](https://www.mongodb.com/resources/compare/mongodb-postgresql/dsl-migrating-postgres-to-mongodb) from postgreSQL to MongoDB 

## 2.3 Programming Platform 

You may use any programming language of your choice for API consumption, data population, and database instance creation.
- Programming platform: Language platform (for API consumption) and/or scripting language or any other intermediate tools that you plan to use.


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
