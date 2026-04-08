# Mermaid Diagram Quick Reference

For any visualization needed in requirement documents, always use Mermaid.

## Common Types

| Type | Typical Use | Mermaid Syntax |
|------|------------|----------------|
| Module diagram | Dependencies or boundaries between features/subsystems/packages | `graph TD` / `graph LR` |
| Flowchart | Operation steps, state machines, business branches | `flowchart` |
| Sequence diagram | Interaction sequence between users, frontend, backend, third parties | `sequenceDiagram` |
| Architecture diagram | Position of this feature in the overall system, data flow | `flowchart` / `flowchart LR` |
| **ER diagram** | **Persisted entities for this feature**, fields, relationships | **`erDiagram`** |

## When to Draw Diagrams

- Involves **more than two roles or system interactions** → Sequence diagram
- Has **3+ process branches** → Flowchart
- Involves **new/changed entities** → ER diagram
- **Inter-module calls or dependencies** → Module diagram
- Prefer drawing multiple concise diagrams over writing lengthy text descriptions of complex interactions

## Embedding Method

Diagrams are embedded within Markdown ` ```mermaid ` code blocks. For complex scenarios, split into multiple diagrams, each focusing on a single concern.

## Examples

### Sequence Diagram (Login Flow)

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant SMS as SMS Service

    U->>F: Enter phone number
    F->>B: Request verification code
    B->>SMS: Send verification code
    SMS-->>U: Receive verification code
    U->>F: Enter verification code
    F->>B: Submit login request
    B-->>F: Return Token
    F-->>U: Redirect to homepage
```

### ER Diagram (User and Session)

```mermaid
erDiagram
    USER {
        int id PK
        string phone
        string email
        string status
        datetime created_at
    }
    SESSION {
        int id PK
        int user_id FK
        string token
        datetime expires_at
    }
    USER ||--o{ SESSION : "has"
```
