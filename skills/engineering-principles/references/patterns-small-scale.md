# 小尺度模式（函数级）

单个函数或几行代码粒度的模式。

## Guard Clause（提前返回）

```typescript
// DO: 提前返回消除嵌套
function getPayAmount(employee: Employee): number {
  if (employee.isSeparated) return 0
  if (employee.isRetired) return retiredAmount()
  return normalPayAmount()
}

// DON'T: 多层嵌套
function getPayAmount(employee: Employee): number {
  if (!employee.isSeparated) {
    if (!employee.isRetired) {
      return normalPayAmount()
    } else {
      return retiredAmount()
    }
  } else {
    return 0
  }
}
```

## Pipe / Compose（管道与组合）

```typescript
// DO: 线性数据流变换
const result = pipe(rawInput, normalize, parse, validate, format)

// DON'T: 嵌套调用
const result = format(validate(parse(normalize(rawInput))))
```

## 表驱动（Table-Driven）

```typescript
// DO: 用数据替代分支逻辑
const statusConfig: Record<Status, { icon: string; color: string }> = {
  active: { icon: '✅', color: 'green' },
  pending: { icon: '⏳', color: 'yellow' },
  error: { icon: '❌', color: 'red' },
}
const { icon, color } = statusConfig[status] ?? statusConfig.pending

// DON'T: if-else 逐个判断
if (status === 'active') { icon = '✅'; color = 'green' }
else if (status === 'pending') { icon = '⏳'; color = 'yellow' }
```

## Null Object（空对象）

```typescript
// DO: 无操作对象代替 null 检查
const logger = options.logger ?? { log: () => {}, warn: () => {} }

// DON'T: 到处检查 if (logger)
if (logger) { logger.log(...) }
```

## 惰性求值 & 闭包封装

```typescript
// 惰性求值：延迟到首次访问才计算
class Config {
  private _parsed?: ParsedConfig
  get parsed() { return this._parsed ??= parseConfig(this.raw) }
}

// 闭包封装私有状态
function createCounter(initial = 0) {
  let count = initial
  return { increment: () => ++count, get: () => count }
}
```
