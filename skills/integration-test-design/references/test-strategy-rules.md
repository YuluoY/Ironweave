# 集成测试策略规则与反模式

## 测试金字塔比例

| 层级 | 占比 | 执行速度 | 维护成本 |
|--|--|--|--|
| 单元测试 | 70% | < 100ms/个 | 低 |
| 集成测试 | 20% | < 5s/个 | 中 |
| E2E 测试 | 10% | < 30s/个 | 高 |

## 集成测试命名规范

```
should_[预期行为]_when_[条件]
```

示例：
- `should_return_paginated_list_when_page_size_is_specified`
- `should_throw_not_found_when_task_does_not_exist`
- `should_rollback_when_downstream_service_fails`

## 反模式

| 反模式 | 问题 | 正确做法 |
|--|--|--|
| 共享测试数据 | 测试间相互依赖 | 每个测试自建数据 |
| 测试顺序依赖 | 并行执行失败 | 测试间无状态共享 |
| 过度 Mock | 测试不真实 | Mock 仅限不可控外部依赖 |
| God Test | 一个测试验证所有 | 一个测试一个断言主题 |
| 硬编码 URL/Port | 环境变更即失败 | 使用动态配置 |
| Sleep 等待 | 不稳定、浪费时间 | 使用 Awaitility / polling |
| 忽略清理 | 测试污染 | `@AfterEach` 或事务回滚 |

## TestContainers 最佳实践

### 容器复用（加速 CI）
```java
// 使用 static container（测试类间共享）
@Testcontainers
class Test1 {
    @Container
    static PostgreSQLContainer<?> pg = new PostgreSQLContainer<>("postgres:16");
}
```

### 容器等待策略
```java
new GenericContainer<>("custom-image")
    .waitingFor(Wait.forHttp("/health").forStatusCode(200))
    .withStartupTimeout(Duration.ofSeconds(60));
```

## WireMock 规范

### 精确匹配（推荐）
```java
stubFor(get(urlEqualTo("/api/external/123"))
    .willReturn(aResponse()
        .withStatus(200)
        .withHeader("Content-Type", "application/json")
        .withBody("""
            {"id": 123, "name": "test"}
            """)));
```

### 模拟超时
```java
stubFor(get(urlEqualTo("/api/slow"))
    .willReturn(aResponse()
        .withStatus(200)
        .withFixedDelay(5000)));  // 5秒延迟
```

### 模拟 500 错误
```java
stubFor(get(urlEqualTo("/api/fail"))
    .willReturn(aResponse().withStatus(500)));
```

## 边界场景检查清单

- [ ] 空列表查询（返回空数组，非 null）
- [ ] 分页第 0 页 / 超出总页数
- [ ] 删除不存在的资源（404 / 幂等 204）
- [ ] 并发创建同名资源（唯一约束冲突 → 409）
- [ ] 请求体为空 / 字段缺失（400 + 详细字段错误）
- [ ] 超长字段（超出数据库列长度）
- [ ] 特殊字符输入（SQL 注入尝试、XSS 标签）
- [ ] 网络超时模拟（外部依赖不可达）
- [ ] 事务回滚验证（部分失败时数据一致性）
