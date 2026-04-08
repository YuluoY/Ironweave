# 设计模式指南

> 核心理念：**设计服务于约束，不服务于教科书**。复杂度必须有回报——如果简单代码能解决，不引入模式。

## 模式选型总表

| 信号 | 推荐模式 | 避免 |
|------|---------|------|
| 多个 `if/else` 选择不同行为 | 策略模式 / 多态 | 平铺 switch-case |
| 创建逻辑复杂或需要灵活切换 | 工厂模式 | 每处重复 new |
| 多步骤构造，参数 > 5 个 | 建造者模式 | 超长构造函数 |
| 多对象响应同一事件 | 观察者 / Event Bus | 直接调用紧耦合 |
| 接口不兼容需要适配 | 适配器模式 | 修改第三方源码 |
| 不修改原类增加功能 | 装饰器 / HOC | 继承链加深 |
| 控制创建数量（连接池） | 对象池 / DI 容器 | 手动全局单例 |
| 树形结构统一操作 | 组合模式 | 每层特殊处理 |
| 状态转换有明确规则 | 状态机 | 散落 if-else |
| 操作需要撤销/重做 | 命令模式 | 手动逆向 |
| 深层嵌套条件 | Guard Clause 提前返回 | 多层 if-else |
| 线性数据变换流程 | Pipe/Compose | 临时变量链 |
| 外部调用可能失败 | 断路器 + 指数退避 | 无限重试 |

## 按尺度查阅

| 尺度 | 文件 | 内容 |
|------|------|------|
| 函数级 | `patterns-small-scale.md` | Guard Clause、Pipe/Compose、表驱动、Null Object、惰性求值、闭包 |
| 类/对象级 | `patterns-classic.md` | GoF 创建型（Factory/Builder/Singleton）、结构型（Decorator/Composite/Facade/Adapter/Proxy）、行为型（Strategy/Observer/State Machine/Command/责任链） |
| 模块级 | `patterns-module.md` | Pipeline/Middleware、Worker Pool、Circuit Breaker、Repository、FSM |
| 前端 | `patterns-frontend.md` | React/Vue 模式选型、样式/路由/错误边界 |
| 后端 | `patterns-backend.md` | CQRS、Saga、Event Sourcing、Specification、RBAC/ABAC |
| 跨域 | `patterns-crosscut.md` | 插件系统、指数退避重试、缓存策略、结构化日志、DI |
| 系统级 | `patterns-architecture.md` | 分层/六边形/Clean Architecture/微内核/模块化单体/微服务/事件驱动/Serverless |
| 代码质量 | `anti-patterns.md` | 10 种反模式识别信号 + 改进策略 + 重构优先级 |
