# Medium-Scale Patterns (Module / Subsystem Level)

Patterns related to scheduling, coordination, flow control, and concurrency management.

## Pipeline / Middleware

```typescript
// Data flows through processing chain, each middleware independent
type Middleware = (ctx: Context, next: () => Promise<void>) => Promise<void>

const app = new App()
app.use(cors())        // CORS
app.use(authGuard())   // Authentication
app.use(rateLimit())   // Rate limiting
app.use(router())      // Routing
```

## Worker Pool

```typescript
// Limited concurrency + task queue
class WorkerPool {
  private running = 0
  private queue: (() => Promise<void>)[] = []

  constructor(private concurrency: number) {}

  async add<T>(task: () => Promise<T>): Promise<T> {
    if (this.running >= this.concurrency) {
      await new Promise<void>(r => this.queue.push(async () => r()))
    }
    this.running++
    try { return await task() }
    finally { this.running--; this.queue.shift()?.() }
  }
}
```

## Circuit Breaker

```typescript
// Three states: closed -> open -> half-open -> closed
class CircuitBreaker {
  private failures = 0
  private state: 'closed' | 'open' | 'half-open' = 'closed'

  async call<T>(fn: () => Promise<T>): Promise<T> {
    if (this.state === 'open') throw new Error('Circuit is open')
    try {
      const result = await fn()
      this.reset()
      return result
    } catch (e) {
      this.failures++
      if (this.failures >= this.threshold) this.state = 'open'
      throw e
    }
  }
}
```

## Repository Pattern

```typescript
// Data access abstraction, isolates ORM/SQL details
interface UserRepository {
  findById(id: string): Promise<User | null>
  findByEmail(email: string): Promise<User | null>
  save(user: User): Promise<User>
}

// Underlying implementation is swappable (TypeORM, Prisma, in-memory mock)
class TypeORMUserRepository implements UserRepository { ... }
class InMemoryUserRepository implements UserRepository { ... } // For testing
```

## Finite State Machine (FSM)

Applicable scenarios: form flows, workflow engines, game logic, protocol parsing, UI interaction states.

```typescript
// State + event + transition table = predictable behavior
interface FSM<S extends string, E extends string> {
  initial: S
  states: Record<S, { on?: Partial<Record<E, S>>; type?: 'final' }>
}

function transition<S extends string, E extends string>(
  fsm: FSM<S, E>, current: S, event: E
): S {
  const next = fsm.states[current]?.on?.[event]
  if (!next) throw new Error(`Invalid transition: ${current} + ${event}`)
  return next
}
```
