# Small-Scale Patterns (Function Level)

Patterns at the granularity of a single function or a few lines of code.

## Guard Clause (Early Return)

```typescript
// DO: Early return eliminates nesting
function getPayAmount(employee: Employee): number {
  if (employee.isSeparated) return 0
  if (employee.isRetired) return retiredAmount()
  return normalPayAmount()
}

// DON'T: Multi-level nesting
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

## Pipe / Compose

```typescript
// DO: Linear data flow transformation
const result = pipe(rawInput, normalize, parse, validate, format)

// DON'T: Nested calls
const result = format(validate(parse(normalize(rawInput))))
```

## Table-Driven

```typescript
// DO: Replace branch logic with data
const statusConfig: Record<Status, { icon: string; color: string }> = {
  active: { icon: '✅', color: 'green' },
  pending: { icon: '⏳', color: 'yellow' },
  error: { icon: '❌', color: 'red' },
}
const { icon, color } = statusConfig[status] ?? statusConfig.pending

// DON'T: if-else checking one by one
if (status === 'active') { icon = '✅'; color = 'green' }
else if (status === 'pending') { icon = '⏳'; color = 'yellow' }
```

## Null Object

```typescript
// DO: No-op object instead of null checks
const logger = options.logger ?? { log: () => {}, warn: () => {} }

// DON'T: Checking if (logger) everywhere
if (logger) { logger.log(...) }
```

## Lazy Evaluation & Closure Encapsulation

```typescript
// Lazy evaluation: Defer computation until first access
class Config {
  private _parsed?: ParsedConfig
  get parsed() { return this._parsed ??= parseConfig(this.raw) }
}

// Closure encapsulating private state
function createCounter(initial = 0) {
  let count = initial
  return { increment: () => ++count, get: () => count }
}
```
