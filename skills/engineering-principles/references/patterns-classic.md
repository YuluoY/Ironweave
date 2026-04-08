# 经典模式（GoF）

## 创建型

### 工厂模式 (Factory)

```typescript
// DO: 封装复杂创建逻辑
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

### 建造者模式 (Builder)

```typescript
// DO: 多步骤构造，可选参数多
const query = new QueryBuilder('users')
  .where('age', '>', 18)
  .orderBy('name')
  .limit(10)
  .build()

// DON'T: 超长构造函数
new Query('users', null, [['age', '>', 18]], null, 'name', 'asc', 10)
```

### 单例 / DI 容器

```typescript
// DO: 通过 DI 容器管理生命周期（NestJS 示例）
@Injectable({ scope: Scope.DEFAULT }) // 默认单例
class DatabaseService { ... }

// DON'T: 手动全局单例
let instance: DatabaseService | null = null
export function getDatabase() {
  if (!instance) instance = new DatabaseService()
  return instance  // 测试无法替换
}
```

## 结构型

### 装饰器 (Decorator / HOC / Composable)

```typescript
// DO: 不修改原对象，透明增加功能
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

### 组合模式 (Composite)

```typescript
// DO: 统一接口处理树形结构
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

### 门面模式 (Facade)

```typescript
// DO: 简化复杂子系统交互
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

### 适配器 (Adapter) & 代理 (Proxy)

```typescript
// 适配器: 统一不同三方接口
interface StorageAdapter {
  upload(file: Buffer, key: string): Promise<string>
}
class S3Adapter implements StorageAdapter { ... }
class OSSAdapter implements StorageAdapter { ... }

// 代理: 控制访问（缓存/延迟/权限）
class CachedUserService implements UserService {
  constructor(private real: UserService, private cache: Cache) {}
  async getById(id: string) {
    return this.cache.get(id) ?? this.cache.set(id, await this.real.getById(id))
  }
}
```

## 行为型

### 策略模式 (Strategy)

```typescript
// DO: 算法家族可互换
interface PaymentStrategy {
  pay(amount: number): Promise<PaymentResult>
}
class AlipayStrategy implements PaymentStrategy { ... }
class WechatPayStrategy implements PaymentStrategy { ... }

// 运行时选择
const strategy = paymentStrategies.get(order.paymentMethod)
await strategy.pay(order.totalAmount)
```

### 观察者 / Event Bus

```typescript
// DO: 事件驱动解耦
orderService.on('orderCreated', (order) => {
  inventoryService.decrease(order.items)
  notificationService.notify(order.userId)
})

// DON'T: 创建订单函数里直接调用库存和通知
function createOrder() {
  // ...创建订单...
  inventoryService.decrease(items)   // 紧耦合
  notificationService.notify(userId) // 紧耦合
}
```

### 状态机 (State Machine)

```typescript
// DO: 状态+转换规则明确、可预测
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

### 命令模式 (Command)

```typescript
// DO: 操作对象化，支持撤销/重做/队列
interface Command { execute(): void; undo(): void }
class MoveCommand implements Command {
  constructor(private element: Element, private dx: number, private dy: number) {}
  execute() { this.element.move(this.dx, this.dy) }
  undo() { this.element.move(-this.dx, -this.dy) }
}
```

### 责任链 (Chain of Responsibility)

```typescript
// DO: 请求沿链条传递直到被处理
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
