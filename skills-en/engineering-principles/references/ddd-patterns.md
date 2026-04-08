# DDD Pattern Guide

## When to Apply

- Project has a clear business domain (not a pure utility/script)
- Modules ≥ 3, with inter-module collaboration
- Project is medium-scale or above (> 50 files)

## Core Concepts

### Bounded Context

Each business subdomain has its own independent model definitions; the same term can have different meanings in different contexts.

- **DO**: `Product` in the Order context only contains `id, name, price`; `Product` in the Catalog context contains full attributes
- **DON'T**: Share a single global `Product` entity with every module adding fields to it

### Aggregate

A group of closely related entities and value objects, accessed and modified through the aggregate root to ensure business consistency.

- **DO**: `Order` (aggregate root) contains `OrderItem` (entity), modified via `Order.addItem()`
- **DON'T**: Directly manipulate `OrderItem` bypassing `Order`

### Domain Service

Business logic that doesn't belong to any single entity goes into domain services.

- **DO**: `PricingService.calculateDiscount(order, user)` — involves multiple aggregates
- **DON'T**: Put discount logic inside `Order` entity (it depends not only on orders but also on user tier)

### Value Object

An immutable object without identity, compared by attribute values.

- **DO**: `Money(amount: 100, currency: 'CNY')` — immutable, equal by value
- **DON'T**: Use plain `number` for monetary amounts (loses currency info, poor comparability)

### Repository

A persistence abstraction for aggregates — the domain layer defines the interface, the infrastructure layer implements it.

- **DO**: Domain layer `interface OrderRepository { findById(id): Order }`
- **DON'T**: Domain layer directly depends on `TypeORM.getRepository(Order)`

## Layered Architecture

```
Presentation Layer        → Controller / Handler / GraphQL Resolver
  ↓ calls
Application Layer         → ApplicationService / UseCase (orchestration, no business logic)
  ↓ calls
Domain Layer              → Entity, ValueObject, DomainService, Repository interface
  ↑ implements
Infrastructure Layer      → RepositoryImpl, External API adapters, ORM config
```

**Dependency direction**: Upper layers depend on lower layers; the domain layer depends on no outer layer.

## Progressive Adoption

No need to go all-in on DDD from the start:

1. **Step 1**: At minimum, separate layers (Controller vs Service vs Repository)
2. **Step 2**: Identify core aggregates, replace anemic models with entity methods
3. **Step 3**: Introduce bounded contexts and domain events for complex modules
