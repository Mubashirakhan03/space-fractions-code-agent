## ScenarioView
1. UseCase — Scenario View: Use Case Diagram
```plantuml
@startuml UseCaseDiagram
left to right direction
actor Member as "Member"
actor Librarian as "Librarian"
rectangle Library {
  usecase "Search Books" as (SearchBooks)
  usecase "Borrow Book" as (BorrowBook)
  usecase "Return Book" as (ReturnBook)
  usecase "Add Book" as (AddBook)
  usecase "View Overdue Report" as (OverdueReport)
}
Member -- (SearchBooks)
Member -- (BorrowBook)
Member -- (ReturnBook)
Librarian -- (AddBook)
Librarian -- (OverdueReport)
@enduml
```

## LogicView
2. Class — Logic View: Class Diagram
```plantuml
@startuml ClassDiagram
class Book {
  - id: int
  - title: string
  - author: string
  + isAvailable(): bool
}
class Member {
  - id: int
  - name: string
  + borrow(book: Book): Loan
}
class Loan {
  - id: int
  - dueDate: date
  - returnedAt: date
  + returnBook(): void
  + daysLate(): int
}
Member --* Loan
Loan --* Book
@enduml
```
3. State — Logic View: State Diagram
```plantuml
@startuml StateDiagram
state Available
state Borrowed
state Overdue
[*] --> Available
Available --> Borrowed : borrow()
Borrowed --> Available : returnBook()
Borrowed --> Overdue : dueDatePassed()
Overdue --> Available : returnBook()
@enduml
```

## ProcessView
4. Sequence — Process View: Sequence Diagram
```plantuml
@startuml SequenceDiagram
participant Member
participant LoanService
participant Catalogue
Member->>LoanService: borrow(bookId)
LoanService->>Catalogue: isAvailable(bookId)
Catalogue->>LoanService: return true
LoanService->>Member: return loan
@enduml
```

## DevelopmentView
5. Component — Development View: Component Diagram
```plantuml
@startuml ComponentDiagram
component CatalogueComponent
component LoanComponent
component MemberComponent
LoanComponent -- CatalogueComponent
LoanComponent -- MemberComponent
@enduml
```
