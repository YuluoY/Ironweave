# 错误处理规则与反模式

## 异常处理反模式

| 反模式 | 问题 | 正确做法 |
|--|--|--|
| catch + 忽略 | 错误被吞没，难以排查 | 至少记日志或重新抛出 |
| catch Exception 笼统捕获 | 掩盖编程错误(NPE 等) | 按异常类型分别捕获 |
| 用错误码代替异常 | 调用方容易忘记检查 | 用异常表达错误路径 |
| 异常作为控制流 | 性能差、可读性差 | 异常仅表达异常情况 |
| 日志 + 重新抛出 | 同一异常被打印多次 | 只在最终处理点打日志 |
| 返回 null 表示错误 | 调用方 NPE 风险 | 用 Optional 或抛异常 |
| 在 finally 中抛异常 | 覆盖原始异常 | finally 只做清理 |

## 错误消息设计

### 面向用户的消息
- 不暴露技术细节（不出现类名、SQL、堆栈）
- 说明发生了什么 + 建议操作
- 示例：`"任务不存在，请检查任务ID"` ✅
- 反例：`"NullPointerException at TaskService.java:42"` ❌

### 面向开发者的日志
- 包含完整上下文：参数值、状态、调用链
- 结构化记录，便于检索
- 示例：`log.error("启动任务失败 taskId={} status={}", taskId, status, e)`

## 事务与异常的关系

| 异常类型 | 事务行为 | 配置 |
|--|--|--|
| RuntimeException | 自动回滚 | Spring 默认 |
| Checked Exception | 不回滚 | 需要 `@Transactional(rollbackFor)` |
| 校验异常(Controller 层) | 无事务 | 在事务外抛出 |

### Spring @Transactional 规则
```java
// 推荐：明确 rollbackFor
@Transactional(rollbackFor = Exception.class)
public void process() { ... }

// 反模式：catch 异常后不重新抛出
@Transactional
public void process() {
    try {
        // ...
    } catch (Exception e) {
        log.error("...", e);
        // ❌ 事务不会回滚！
    }
}
```

## 日志级别规范

| 级别 | 使用场景 |
|--|--|
| ERROR | 系统异常、不可恢复错误 |
| WARN | 可恢复但异常的情况(重试成功、降级触发) |
| INFO | 业务关键节点(任务启动、完成、状态变更) |
| DEBUG | 调试信息(方法参数、中间状态) |

## 超时配置参考

| 调用类型 | 连接超时 | 读取超时 | 总超时 |
|--|--|--|--|
| 数据库查询 | 3s | 10s | 15s |
| 内部微服务 | 3s | 5s | 10s |
| 第三方 API | 5s | 15s | 30s |
| 文件上传 | 5s | 60s | 120s |

## 死信队列处理

当消息消费失败且不可重试时：

1. 投入死信队列（DLQ）
2. 记录失败原因 + 原始消息
3. 告警通知运维
4. 提供手动重放接口
5. 定期清理过期死信

## 幂等性与错误重试

重试机制要求业务操作幂等：

| 操作类型 | 幂等方案 |
|--|--|
| 创建 | Idempotency-Key + 去重表 |
| 更新 | 乐观锁(版本号) |
| 删除 | 直接幂等(删除不存在的资源返回 204) |
| 状态变更 | 状态机校验(只从合法前置状态转换) |
