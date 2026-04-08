# Complexity Assessment Rules and Decomposition Templates

## Complexity Scoring Guide

### Algorithm Complexity

| Score | Criteria | Example |
|--|--|--|
| 1-2 | Simple CRUD, no business computation | Create/Read/Update/Delete |
| 3-4 | Simple computation/transformation | Data format conversion, simple aggregation |
| 5-6 | Rule engine / state machine | Order status flow, approval process |
| 7-8 | Complex algorithms | Scheduling algorithms, matching algorithms |
| 9-10 | Research-level algorithms | ML inference, complex optimization |

### Data Complexity

| Score | Criteria | Example |
|--|--|--|
| 1-2 | Single table < 10K rows | Config tables, dictionary tables |
| 3-4 | Multiple tables < 100K rows | User management, order management |
| 5-6 | Multiple tables < 1M rows with join queries | Reporting systems, historical data |
| 7-8 | Large data > 1M rows, requires sharding | Log analysis, behavior tracking |
| 9-10 | Real-time stream processing / distributed data | Real-time recommendations, stream computing |

### Integration Complexity

| Score | Criteria | Example |
|--|--|--|
| 1-2 | No external dependencies | Pure local functionality |
| 3-4 | 1-2 stable dependencies | Calling internal microservices |
| 5-6 | 3+ dependencies, some unstable | Bank API, SMS gateway |
| 7-8 | Multiple async dependencies requiring orchestration | Saga pattern, event orchestration |
| 9-10 | Cross-platform / cross-network integration | Hardware integration, legacy system interfacing |

### Concurrency Complexity

| Score | Criteria | Example |
|--|--|--|
| 1-2 | No concurrency contention | Single-user operations |
| 3-4 | Simple optimistic locking | Inventory deduction, version control |
| 5-6 | Requires distributed locks | Globally unique serial numbers |
| 7-8 | Complex concurrency orchestration | Multi-phase commit, distributed transactions |
| 9-10 | High-performance lock-free solutions | Lock-free queues, Actor model |

### Domain Complexity

| Score | Criteria | Example |
|--|--|--|
| 1-2 | Rules are simple and clear | Form submission |
| 3-4 | Multi-branch logic | Conditional approval, permission checks |
| 5-6 | Complex business rules + exception scenarios | Billing rules, contract management |
| 7-8 | Rules only domain experts understand | Medical diagnosis, financial risk control |
| 9-10 | Regulatory compliance + constantly changing | Tax calculation, cross-border settlement |

## Decomposition Templates

### Vertical Slice Template

```markdown
## Feature: [Name]

### Slice 1: MVP (Priority P0)
- Core user story: [...]
- Scope: Happy path only
- Tech: Simplest implementation approach

### Slice 2: Refinement (Priority P1)
- Exception handling + boundary scenarios
- Performance optimization

### Slice 3: Enhancement (Priority P2)
- Advanced features
- Extensibility improvements
```

### Horizontal Layer Template

```markdown
## Module: [Name]

### Step 1: Interface Definition
- Define API contract + DTOs
- Can be mock-integrated

### Step 2: Domain Layer
- Entity + business logic + unit tests

### Step 3: Persistence Layer
- Repository + Mapper + integration tests

### Step 4: Application Layer
- Service orchestration + transactions + API tests
```

## Estimation Guide

| Complexity | Estimation Multiplier | Notes |
|--|--|--|
| 1-3 | 1x | Normal estimation |
| 4-6 | 1.5x | Add 50% buffer |
| 7-8 | 2x | Add 100% buffer + spike |
| 9-10 | 3x+ | Requires prototype validation before estimating |

## Technical Decision Template

```markdown
## Decision: [Topic]

### Background
[Why this decision is needed]

### Candidate Solutions
| Solution | Advantages | Disadvantages | Risks |
|--|--|--|--|
| A | ... | ... | ... |
| B | ... | ... | ... |

### Evaluation Criteria
1. [Criterion 1] — Weight [30%]
2. [Criterion 2] — Weight [30%]
3. [Criterion 3] — Weight [20%]
4. [Criterion 4] — Weight [20%]

### Conclusion
Choose solution [X], reason: [...]
```
