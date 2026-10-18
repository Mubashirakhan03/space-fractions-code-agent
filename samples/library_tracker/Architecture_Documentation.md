# A. Executive Summary
The Library Book Tracker is a web-based system that helps a small school library manage its books. The system consists of a book catalogue with search, a borrowing desk, a returns desk, and an overdue report. The architecture follows a microservices approach deployed on a cloud platform.

Chosen architectural style: Microservices
Deployment topology: Cloud-based infrastructure

| Risk | Mitigation |
| --- | --- |
| 1. Lost loan records | Nightly database backups |
| 2. Slow search | Index book titles |

# B. Traceability & Rationale
| Requirement ID | Short Text | Diagram(s) | Component(s) | Artifact filename(s) | Rationale |
| --- | --- | --- | --- | --- | --- |
| FR-1 | Search books | UseCaseDiagram | CatalogueComponent | openapi.yaml | Members find books by title or author |
| FR-2 | Borrow a book | SequenceDiagram | LoanComponent | sql/library.sql | A member borrows an available book for 14 days |
| NFR-1 | Responsiveness | SequenceDiagram | CatalogueComponent | openapi.yaml | Search returns in under one second |

FR-3 (return a book and record late days) is also required.

# C. Architecture Overview
* CatalogueComponent: responsible for books and search
* LoanComponent: responsible for borrowing, returning and overdue detection
* MemberComponent: responsible for library members

# D. Detailed Technical Design
## CatalogueComponent
### Technology options
* Language/runtime: Node.js 20 (Justification: meets NFR-1 (responsiveness))
* Persistence: PostgreSQL 15 (Justification: meets NFR-1 (responsiveness))
* Cache: Redis 7 (Justification: meets NFR-1 (responsiveness))

### Interface design
```yml
openapi: 3.0.0
info:
  title: Library API
  version: 1.0.0
paths:
  /books:
    get:
      summary: Search books
      responses:
        200:
          description: Matching books
  /loans:
    post:
      summary: Borrow a book
      responses:
        201:
          description: Loan created
```
### Data model / schema
```sql
CREATE TABLE books (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  author TEXT NOT NULL
);
CREATE TABLE loans (
  id SERIAL PRIMARY KEY,
  book_id INT REFERENCES books(id),
  member_id INT NOT NULL,
  due_date DATE NOT NULL,
  returned_at DATE
);
```

# E. Operations & Deployment
* Deploy each service as a Docker container on Kubernetes.

# H. Testing Strategy
| Test Type | CatalogueComponent | LoanComponent |
| --- | --- | --- |
| Unit testing | | |

# K. Open Questions & Assumptions
## Assumptions
A1: A loan lasts 14 days.

## Unresolved stakeholder questions needing input
* Is there a limit on books per member?

# L. Deliverables
```markdown
openapi.yaml
sql/library_ddl.sql
```
