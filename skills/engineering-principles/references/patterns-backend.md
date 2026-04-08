# 后端特定模式

## 选型速查

| 场景 | 方案 | 引入条件 |
|------|------|---------|
| 读写模型差异大 | **CQRS** | 读写比 > 10:1 或查询/写入模型显著不同 |
| 多步骤异步事务 | **Saga** | 步骤 ≥ 3 且含补偿逻辑 |
| 完整变更历史 | **Event Sourcing** | 需要审计/回放/时间旅行 |
| 业务规则复用 | **Specification** | 规则可组合（and/or/not） |
| API 版本管理 | 路径版本 / Header 版本 | 公共 API 有外部消费者 |
| 权限控制 | **RBAC / ABAC** | 角色 > 3 种 或 需要属性级权限 |

## CQRS（命令与查询分离）

```typescript
// 读写分离：写入走命令服务，读取走查询服务
class OrderCommandService {
  async createOrder(cmd: CreateOrderCommand) { /* 写入主库 */ }
}
class OrderQueryService {
  async getOrderDetail(id: string) { /* 读取，可走缓存/读库 */ }
}
```

## Saga（多步骤异步事务）

```typescript
// 每个步骤有执行和补偿
interface SagaStep {
  execute(): Promise<void>
  compensate(): Promise<void>
}

// 执行链：成功则继续 → 失败则反向补偿
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

## Specification（规约模式）

```typescript
// 业务规则可组合
interface Specification<T> {
  isSatisfiedBy(candidate: T): boolean
  and(other: Specification<T>): Specification<T>
  or(other: Specification<T>): Specification<T>
  not(): Specification<T>
}

// 使用：
const eligible = new AgeSpec(18).and(new RegionSpec('CN')).and(new VipSpec())
const users = await userRepo.findAll(eligible)
```

## Domain Service

```typescript
// 业务逻辑不属于单个实体时，放入领域服务
class TransferService {
  transfer(from: Account, to: Account, amount: Money) {
    if (!from.canWithdraw(amount)) throw new InsufficientFundsError()
    from.withdraw(amount)
    to.deposit(amount)
  }
}
```
