# Cross-Domain Patterns

General scenarios encountered in both frontend and backend.

## Selection Quick Reference

| Scenario | Recommended Solution | Key Points |
|----------|---------------------|------------|
| Plugin system | Registration + lifecycle hooks | When third parties need to extend behavior |
| Retry & fault tolerance | Exponential backoff + circuit breaker | `delay = base * 2^attempt`, max 3-5 retries |
| Caching strategy | Cache-aside / Write-through | Cache-aside for read-heavy, write-light scenarios |
| Logging & observability | Structured logging + distributed tracing | Must-have for production environments |
| Dependency injection | Constructor injection / DI container | When testability is needed |
| Concurrency control | Locks / Semaphores / Queues | Identify critical resources before choosing |

## Exponential Backoff Retry

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

## Plugin System

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

## Structured Logging

```typescript
// DO: Structured fields for easy search
logger.info('Order created', {
  orderId: order.id,
  userId: order.userId,
  total: order.total,
  traceId: ctx.traceId,
})

// DON'T: String concatenation
logger.info(`Order ${order.id} created by ${order.userId} total ${order.total}`)
```
