# SOLID 原则

## SRP — 单一职责原则

一个类/函数只有一个引起它变化的原因。

- **DO**: 拆分 `UserService` 为 `UserAuthService` + `UserProfileService`
- **DON'T**: 一个 `UserService` 同时处理登录、注册、修改资料、发邮件

判断标准：如果你需要用"和"来描述一个类的职责，它可能违反了 SRP。

## OCP — 开闭原则

对扩展开放，对修改关闭。通过接口/抽象类实现新行为，而非修改已有代码。

- **DO**: 定义 `PaymentStrategy` 接口，新增支付方式实现新类
- **DON'T**: 在 `pay()` 方法中用 `if/else` 判断支付类型

适用信号：当你发现自己在添加新的 `else if` 分支时，考虑 OCP。

## LSP — 里氏替换原则

子类必须能替代父类使用，不改变程序正确性。

- **DO**: `Square extends Rectangle` 在所有使用 `Rectangle` 的地方行为一致
- **DON'T**: 子类重写方法后抛出父类调用方不期望的异常

适用信号：当子类需要限制或强制父类的某些行为时，继承关系可能不合适。

## ISP — 接口隔离原则

客户端不应依赖它不使用的接口。多个小接口优于一个大接口。

- **DO**: `Readable`, `Writable`, `Closable` 三个独立接口
- **DON'T**: 一个 `FileOperations` 接口包含 20 个方法，实现类只用其中 3 个

适用信号：实现类中有大量空方法或 `throw new NotImplementedError()`。

## DIP — 依赖倒置原则

高层模块不应依赖低层模块，两者都应依赖抽象。

- **DO**: `OrderService` 依赖 `OrderRepository`（接口），具体实现注入
- **DON'T**: `OrderService` 直接 `new MySQLOrderRepository()`

适用信号：`new` 关键字出现在业务类中（应通过依赖注入替代）。
