# 跨域模式

前后端都会遇到的通用场景。

## 选型速查

| 场景 | 推荐方案 | 要点 |
|------|---------|------|
| 插件系统 | 注册 + 生命周期钩子 | 第三方需扩展行为时使用 |
| 重试与容错 | 指数退避 + 熔断器 | `delay = base * 2^attempt`，最大 3-5 次 |
| 缓存策略 | Cache-aside / Write-through | 读多写少用 Cache-aside |
| 日志与可观测 | 结构化日志 + 链路追踪 | 生产环境必须有 |
| 依赖注入 | 构造函数注入 / DI 容器 | 需可测试性的场景 |
| 并发控制 | 锁 / 信号量 / 队列 | 识别临界资源再选方案 |

## 指数退避重试

```typescript
async function withRetry<T>(fn: () => Promise<T>, maxRetries = 3): Promise<T> {
  for (let i = 0; i <= maxRetries; i++) {
    try { return await fn() }
    catch (e) {
      if (i === maxRetries) throw e
      await sleep(Math.min(1000 * Math.pow(2, i), 30000))
    }
  }
  throw new Error('unreachable')
}
```

## 插件系统

```typescript
interface Plugin {
  name: string
  install(app: App): void
  destroy?(): void
}

class PluginManager {
  private plugins: Plugin[] = []

  register(plugin: Plugin) {
    plugin.install(this.app)
    this.plugins.push(plugin)
  }

  destroyAll() {
    this.plugins.reverse().forEach(p => p.destroy?.())
  }
}
```

## 结构化日志

```typescript
// DO: 结构化字段，便于检索
logger.info('Order created', {
  orderId: order.id,
  userId: order.userId,
  total: order.total,
  traceId: ctx.traceId,
})

// DON'T: 拼接字符串
logger.info(`Order ${order.id} created by ${order.userId} total ${order.total}`)
```
