# Backend-Specific Patterns

## Selection Quick Reference

| Scenario | Solution | When to Adopt |
|----------|----------|---------------|
| Read/write model divergence | **CQRS** | Read/write ratio > 10:1 or query/write models significantly different |
| Multi-step async transactions | **Saga** | Steps ≥ 3 with compensation logic |
| Complete change history | **Event Sourcing** | Need audit/replay/time travel |
| Business rule reuse | **Specification** | Rules are composable (and/or/not) |
| API version management | Path versioning / Header versioning | Public API has external consumers |
| Access control | **RBAC / ABAC** | Roles > 3 types or need attribute-level permissions |

## CQRS (Command Query Responsibility Segregation)

```typescript
// Read/write separation: writes go through command service, reads through query service
class OrderCommandService {
  async createOrder(cmd: CreateOrderCommand) { /* Write to primary DB */ }
}
class OrderQueryService {
  async getOrderDetail(id: string) { /* Read, can use cache/read replica */ }
}
```

## Saga (Multi-Step Async Transactions)

```typescript
// Each step has execute and compensate
interface SagaStep {
  execute(): Promise<void>
  compensate(): Promise<void>
}

// Execution chain: continue on success → reverse compensate on failure
async function runSaga(steps: SagaStep[]) {
  const completed: SagaStep[] = []
  for (const step of steps) {
    try {
      await step.execute()
      completed.push(step)
    } catch (e) {
      for (const s of completed.reverse()) await s.compensate()
      throw e
    }
  }
}
```

## Specification Pattern

```typescript
// Business rules are composable
interface Specification<T> {
  isSatisfiedBy(candidate: T): boolean
  and(other: Specification<T>): Specification<T>
  or(other: Specification<T>): Specification<T>
  not(): Specification<T>
}

// Usage:
const eligible = new AgeSpec(18).and(new RegionSpec('CN')).and(new VipSpec())
const users = await userRepo.findAll(eligible)
```

## Domain Service

```typescript
// Business logic that doesn't belong to a single entity goes into domain services
class TransferService {
  transfer(from: Account, to: Account, amount: Money) {
    if (!from.canWithdraw(amount)) throw new InsufficientFundsError()
    from.withdraw(amount)
    to.deposit(amount)
  }
}
```
