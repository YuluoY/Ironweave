# Classic Patterns (GoF)

## Creational

### Factory Pattern

```typescript
// DO: Encapsulate complex creation logic
class NotificationFactory {
  static create(channel: Channel): Notification {
    const map: Record<Channel, () => Notification> = {
      email: () => new EmailNotification(config.smtp),
      sms: () => new SmsNotification(config.smsGateway),
      push: () => new PushNotification(config.firebase),
    }
    const creator = map[channel]
    if (!creator) throw new Error(`Unknown channel: ${channel}`)
    return creator()
  }
}
```

### Builder Pattern

```typescript
// DO: Multi-step construction with many optional parameters
const query = new QueryBuilder('users')
  .where('age', '>', 18)
  .orderBy('name')
  .limit(10)
  .build()

// DON'T: Ultra-long constructor
new Query('users', null, [['age', '>', 18]], null, 'name', 'asc', 10)
```

### Singleton / DI Container

```typescript
// DO: Manage lifecycle through DI container (NestJS example)
@Injectable({ scope: Scope.DEFAULT }) // Default singleton
class DatabaseService { ... }

// DON'T: Manual global singleton
let instance: DatabaseService | null = null
export function getDatabase() {
  if (!instance) instance = new DatabaseService()
  return instance  // Cannot replace in tests
}
```

## Structural

### Decorator / HOC / Composable

```typescript
// DO: Transparently add functionality without modifying the original object
function withLogging<T extends (...args: any[]) => any>(fn: T): T {
  return ((...args: Parameters<T>) => {
    console.log(`Calling ${fn.name}`, args)
    return fn(...args)
  }) as T
}

// React HOC
const withAuth = (Component: FC) => (props: any) => {
  const { user } = useAuth()
  if (!user) return <Redirect to="/login" />
  return <Component {...props} user={user} />
}
```

### Composite Pattern

```typescript
// DO: Unified interface for tree structure handling
interface MenuItem {
  render(): string
  getPermissions(): string[]
}
class MenuGroup implements MenuItem {
  constructor(private children: MenuItem[]) {}
  render() { return this.children.map(c => c.render()).join('\n') }
  getPermissions() { return this.children.flatMap(c => c.getPermissions()) }
}
```

### Facade Pattern

```typescript
// DO: Simplify complex subsystem interactions
class OrderFacade {
  async placeOrder(dto: CreateOrderDto) {
    const inventory = await this.inventoryService.check(dto.items)
    const payment = await this.paymentService.charge(dto.payment)
    const order = await this.orderService.create(dto, payment.id)
    await this.notificationService.sendConfirmation(order)
    return order
  }
}
```

### Adapter & Proxy

```typescript
// Adapter: Unify different third-party interfaces
interface StorageAdapter {
  upload(file: Buffer, key: string): Promise<string>
}
class S3Adapter implements StorageAdapter { ... }
class OSSAdapter implements StorageAdapter { ... }

// Proxy: Control access (caching/lazy/permission)
class CachedUserService implements UserService {
  constructor(private real: UserService, private cache: Cache) {}
  async getById(id: string) {
    return this.cache.get(id) ?? this.cache.set(id, await this.real.getById(id))
  }
}
```

## Behavioral

### Strategy Pattern

```typescript
// DO: Interchangeable algorithm family
interface PaymentStrategy {
  pay(amount: number): Promise<PaymentResult>
}
class AlipayStrategy implements PaymentStrategy { ... }
class WechatPayStrategy implements PaymentStrategy { ... }

// Runtime selection
const strategy = paymentStrategies.get(order.paymentMethod)
await strategy.pay(order.totalAmount)
```

### Observer / Event Bus

```typescript
// DO: Event-driven decoupling
orderService.on('orderCreated', (order) => {
  inventoryService.decrease(order.items)
  notificationService.notify(order.userId)
})

// DON'T: Direct calls in create order function
function createOrder() {
  // ...create order...
  inventoryService.decrease(items)   // Tight coupling
  notificationService.notify(userId) // Tight coupling
}
```

### State Machine

```typescript
// DO: Clear and predictable state + transition rules
const orderFSM = {
  initial: 'draft',
  states: {
    draft:     { on: { SUBMIT: 'pending' } },
    pending:   { on: { APPROVE: 'confirmed', REJECT: 'draft' } },
    confirmed: { on: { SHIP: 'shipped', CANCEL: 'cancelled' } },
    shipped:   { on: { DELIVER: 'completed' } },
    completed: { type: 'final' },
    cancelled: { type: 'final' },
  }
}
```

### Command Pattern

```typescript
// DO: Objectify operations, support undo/redo/queue
interface Command { execute(): void; undo(): void }
class MoveCommand implements Command {
  constructor(private element: Element, private dx: number, private dy: number) {}
  execute() { this.element.move(this.dx, this.dy) }
  undo() { this.element.move(-this.dx, -this.dy) }
}
```

### Chain of Responsibility

```typescript
// DO: Request passes along chain until handled
abstract class Handler<T> {
  private next?: Handler<T>
  setNext(handler: Handler<T>) { this.next = handler; return handler }
  handle(request: T): T {
    if (this.canHandle(request)) return this.process(request)
    if (this.next) return this.next.handle(request)
    return request
  }
  abstract canHandle(request: T): boolean
  abstract process(request: T): T
}
```
