# DDD 模式指南

## 适用条件

- 项目有明确的业务领域（不是纯工具/脚本）
- 模块 ≥ 3 个，存在模块间协作
- 项目规模中等以上（> 50 文件）

## 核心概念

### 限界上下文 (Bounded Context)

每个业务子域有独立的模型定义，同一个词在不同上下文中含义不同。

- **DO**: 订单上下文的 `Product` 只包含 `id, name, price`；商品上下文的 `Product` 包含完整属性
- **DON'T**: 全局共用一个 `Product` 实体，所有模块往里加字段

### 聚合 (Aggregate)

一组紧密关联的实体和值对象，通过聚合根统一访问和修改，保证业务一致性。

- **DO**: `Order`（聚合根）包含 `OrderItem`（实体），通过 `Order.addItem()` 修改
- **DON'T**: 直接操作 `OrderItem` 绕过 `Order`

### 领域服务 (Domain Service)

不属于任何实体的业务逻辑，放在领域服务中。

- **DO**: `PricingService.calculateDiscount(order, user)` — 涉及多个聚合
- **DON'T**: 把折扣逻辑放在 `Order` 实体中（它不仅依赖订单，还依赖用户等级）

### 值对象 (Value Object)

无标识的不可变对象，通过属性值判等。

- **DO**: `Money(amount: 100, currency: 'CNY')` — 不可变，值相等即相同
- **DON'T**: 用 `number` 直接表示金额（丢失币种信息，可比较性差）

### 仓储 (Repository)

对聚合的持久化抽象，领域层定义接口，基础设施层实现。

- **DO**: 领域层 `interface OrderRepository { findById(id): Order }`
- **DON'T**: 领域层直接依赖 `TypeORM.getRepository(Order)`

## 分层架构

```
表现层 (Presentation)     → Controller / Handler / GraphQL Resolver
  ↓ 调用
应用层 (Application)      → ApplicationService / UseCase（编排，不含业务逻辑）
  ↓ 调用
领域层 (Domain)           → Entity, ValueObject, DomainService, Repository接口
  ↑ 实现
基础设施层 (Infrastructure) → RepositoryImpl, 外部API适配, ORM配置
```

**依赖方向**：上层依赖下层，领域层不依赖任何外层。

## 渐进式采用

不必一步到位全面 DDD：

1. **第一步**：至少做到分层（Controller vs Service vs Repository）
2. **第二步**：识别核心聚合，用实体方法替代贫血模型
3. **第三步**：对复杂模块引入限界上下文和领域事件
