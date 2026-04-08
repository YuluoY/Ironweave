# Anti-Pattern Identification and Improvement

> Common issues during code review and refactoring. Identify signals -> Judge severity -> Choose improvement direction.

## Quick Identification Table

| Anti-Pattern | Identification Signal | Severity | Improvement Direction |
|--------|---------|--------|---------|
| **God Object** | File > 500 lines, responsibilities > 3 | High | Split by responsibility into independent modules |
| **Circular Dependency** | A -> B -> A | High | Extract common module / Dependency inversion / Event decoupling |
| **Shotgun Surgery** | One requirement changes > 5 files | High | Identify change reasons, aggregate code driven by same cause |
| **Implicit Temporal Coupling** | Must call in specific order | High | Builder / FSM to enforce order |
| **Platform if-else** | Conditional branches > 3 levels | High | Strategy pattern / Polymorphism / Table-driven |
| **Over-abstraction** | Abstraction layers > implementation layers | Medium | Remove unnecessary intermediate layers |
| **Long Parameter List** | Parameters > 5 | Medium | Parameter object / Builder |
| **Data Clumps** | Same group of data always passed together | Medium | Extract into independent class/interface |
| **Anemic Model** | Data and operations completely separated | Medium | Cohese related behavior into entity |
| **Zombie Code** | No one calls it but afraid to delete | Low | Confirm no references then delete |

## Refactoring Priority

```
P0: Blocks current task / causes bugs          -> Fix immediately
P1: Currently passing by and low change cost    -> Fix in passing
P2: Large impact scope but not urgent           -> Record as tech debt
P3: Not pretty but doesn't affect functionality -> Don't fix
```

## Detailed Improvement Strategies

### God Object

```
Steps:
1. List all responsibilities of the current object
2. Group by "who cares about this data"
3. Extract each group into an independent module/class
4. Demote original object to coordinator (Facade) or delete
```

```typescript
// BEFORE: UserService does too many things
class UserService {
  register() { ... }
  login() { ... }
  sendEmail() { ... }
  generateReport() { ... }
  managePermissions() { ... }
}

// AFTER: Split by responsibility
class AuthService { register() { ... }; login() { ... } }
class EmailService { send() { ... } }
class ReportService { generate() { ... } }
class PermissionService { manage() { ... } }
```

### Circular Dependency

Four solutions, sorted by priority:

| Solution | Applicable Scenario |
|------|---------|
| **Extract common module** | Shared types/interfaces cause the cycle |
| **Dependency inversion** | A depends on B's concrete implementation -> A defines interface, B implements |
| **Event decoupling** | Neither side needs synchronous return values |
| **Merge modules** | Two modules are actually one concept |

```typescript
// BEFORE: Circular dependency
// order.service.ts
import { PaymentService } from './payment.service' // A -> B

// payment.service.ts
import { OrderService } from './order.service'     // B -> A

// AFTER: Event decoupling
// order.service.ts
this.eventBus.emit('orderCreated', order)

// payment.service.ts
this.eventBus.on('orderCreated', (order) => this.process(order))
```

### Shotgun Surgery

```
Steps:
1. Identify "change reason" - is it requirement-driven or technology-driven
2. Aggregate code driven by the same reason into one module
3. Consider introducing registration mechanism (strategy registration / plugin registration)
```

### Implicit Temporal Coupling

```typescript
// BEFORE: Must call in order, but compiler doesn't enforce
service.init()
service.configure()
service.start()  // Crashes if configure wasn't called

// AFTER: Builder enforces order
const service = ServiceBuilder.create()
  .withConfig(config)   // Must configure first
  .build()              // Validates at build time
  .start()              // Can only start after configured
```

### Over-abstraction

Identification signals:
- Interface has only one implementation with no foreseeable replacement scenario
- Intermediate layer only forwards, adds no logic
- 3 lines of code wrapped in 2 classes

```
Principle: Keep abstraction only when its benefit > reading comprehension cost
Action: Remove interfaces with only 1 implementation that don't need mocking
```

### Anemic Model vs Rich Model

```typescript
// BEFORE: Anemic model - data and operations separated
class Order { status: string; items: Item[]; total: number }
class OrderService {
  cancel(order: Order) {
    if (order.status !== 'pending') throw new Error('...')
    order.status = 'cancelled'
    order.total = 0
  }
}

// AFTER: Rich model - behavior cohesed into entity
class Order {
  cancel() {
    if (this.status !== 'pending') throw new Error('...')
    this.status = 'cancelled'
    this.total = 0
  }
}
```

> Note: Anemic model is reasonable for simple CRUD scenarios; only transition to rich model when business rules are complex.
