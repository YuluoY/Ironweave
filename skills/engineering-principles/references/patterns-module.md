# 中尺度模式（模块 / 子系统级）

调度、协调、流控、并发管理相关模式。

## 管道 / 中间件 (Pipeline / Middleware)

```typescript
// 数据沿处理链流过，每个中间件独立
type Middleware = (ctx: Context, next: () => Promise<void>) => Promise<void>

const app = new App()
app.use(cors())        // 跨域
app.use(authGuard())   // 认证
app.use(rateLimit())   // 限流
app.use(router())      // 路由
```

## 工作池 (Worker Pool)

```typescript
// 有限并发 + 任务队列
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

## 断路器 (Circuit Breaker)

```typescript
// 三态: closed → open → half-open → closed
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

## 仓库模式 (Repository)

```typescript
// 数据访问抽象，隔离 ORM/SQL 细节
interface UserRepository {
  findById(id: string): Promise<User | null>
  findByEmail(email: string): Promise<User | null>
  save(user: User): Promise<User>
}

// 底层实现可替换（TypeORM, Prisma, 内存mock）
class TypeORMUserRepository implements UserRepository { ... }
class InMemoryUserRepository implements UserRepository { ... } // 测试用
```

## 有限状态机 (FSM)

适用场景：表单流程、工作流引擎、游戏逻辑、协议解析、UI 交互状态。

```typescript
// 状态 + 事件 + 转换表 = 可预测行为
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
