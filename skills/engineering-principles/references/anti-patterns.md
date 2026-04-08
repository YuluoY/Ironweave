# 反模式识别与改进

> 代码审查和重构时的常见问题。识别信号 → 判断严重度 → 选择改进方向。

## 快速识别表

| 反模式 | 识别信号 | 严重度 | 改进方向 |
|--------|---------|--------|---------|
| **上帝对象** | 文件 > 500 行，职责 > 3 项 | 高 | 按职责拆分为独立模块 |
| **循环依赖** | A → B → A | 高 | 提取公共模块 / 依赖反转 / 事件解耦 |
| **散弹式修改** | 一个需求改 > 5 个文件 | 高 | 识别变化原因，聚合受同因驱动的代码 |
| **隐式时序耦合** | 必须按特定顺序调用 | 高 | Builder / FSM 强制顺序 |
| **平台型 if-else** | 条件分支 > 3 层 | 高 | 策略模式 / 多态 / 表驱动 |
| **过度抽象** | 抽象层 > 实现层 | 中 | 删除不必要中间层 |
| **过长参数列表** | 参数 > 5 个 | 中 | 参数对象化 / Builder |
| **数据泥团** | 同组数据总一起传递 | 中 | 提取为独立类/接口 |
| **贫血模型** | 数据和操作完全分离 | 中 | 将相关行为内聚到实体 |
| **僵尸代码** | 无人调用但不敢删 | 低 | 确认无引用后删除 |

## 重构优先级

```
P0: 阻碍当前任务 / 导致 bug         → 立即修复
P1: 当前路过且改动成本低             → 顺手修复
P2: 影响范围大但不紧急               → 记录技术债
P3: 不美观但不影响功能               → 不修
```

## 详细改进策略

### 上帝对象

```
步骤：
1. 列出当前对象的所有职责
2. 按"谁关心这数据"分组
3. 每组提取为独立模块/类
4. 原对象降级为协调者（Facade）或删除
```

```typescript
// BEFORE: UserService 做了太多事
class UserService {
  register() { ... }
  login() { ... }
  sendEmail() { ... }
  generateReport() { ... }
  managePermissions() { ... }
}

// AFTER: 按职责拆分
class AuthService { register() { ... }; login() { ... } }
class EmailService { send() { ... } }
class ReportService { generate() { ... } }
class PermissionService { manage() { ... } }
```

### 循环依赖

四种解法，按优先级排序：

| 方案 | 适用场景 |
|------|---------|
| **提取公共模块** | 共享类型/接口导致循环 |
| **依赖反转** | A 依赖 B 的具体实现 → A 定义接口，B 实现 |
| **事件解耦** | 双方不需要同步返回值 |
| **合并模块** | 两个模块本就是一个概念 |

```typescript
// BEFORE: 循环依赖
// order.service.ts
import { PaymentService } from './payment.service' // A → B

// payment.service.ts
import { OrderService } from './order.service'     // B → A

// AFTER: 事件解耦
// order.service.ts
this.eventBus.emit('orderCreated', order)

// payment.service.ts
this.eventBus.on('orderCreated', (order) => this.process(order))
```

### 散弹式修改

```
步骤：
1. 识别"变化原因"——是需求驱动还是技术驱动
2. 聚合受同一原因驱动的代码到一个模块
3. 考虑引入注册机制（策略注册/插件注册）
```

### 隐式时序耦合

```typescript
// BEFORE: 必须按顺序调用，但编译器不强制
service.init()
service.configure()
service.start()  // 如果没调 configure 会崩

// AFTER: Builder 强制顺序
const service = ServiceBuilder.create()
  .withConfig(config)   // 必须先配置
  .build()              // build 时校验
  .start()              // 配置完才能 start
```

### 过度抽象

识别信号：
- 接口只有一个实现，且没有可预见的替换场景
- 中间层只做转发，不加任何逻辑
- 3 行代码被包了 2 个 class

```
原则: 抽象的收益 > 阅读理解成本时才保留
行动: 删除只有 1 个实现且不需要 mock 的接口
```

### 贫血模型 vs 充血模型

```typescript
// BEFORE: 贫血模型——数据和操作分离
class Order { status: string; items: Item[]; total: number }
class OrderService {
  cancel(order: Order) {
    if (order.status !== 'pending') throw new Error('...')
    order.status = 'cancelled'
    order.total = 0
  }
}

// AFTER: 充血模型——行为内聚到实体
class Order {
  cancel() {
    if (this.status !== 'pending') throw new Error('...')
    this.status = 'cancelled'
    this.total = 0
  }
}
```

> 注意：贫血模型在 CRUD 简单场景是合理的，只有在业务规则复杂时才需要转向充血模型。
