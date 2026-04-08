# RESTful API 设计规则与反模式

## 命名反模式

| 反模式 | 正确写法 | 原因 |
|--|--|--|
| `/getUsers` | `GET /users` | 动词在方法中，不在路径中 |
| `/user/list` | `GET /users` | 用复数名词 |
| `/user_roles` | `/user-roles` | 路径用 kebab-case |
| `/Users` | `/users` | 路径全小写 |
| `/users/{id}/tasks/{taskId}/comments/{commentId}/replies` | 最多 2 层嵌套 | 过深嵌套降低可用性 |

## 查询参数标准

### 过滤
```
GET /users?status=active&role=admin
GET /orders?createdAfter=2026-01-01&createdBefore=2026-12-31
```

### 排序
```
GET /users?sortBy=createdAt&sortOrder=desc
GET /users?sort=-createdAt,+name  (简洁风格)
```

### 搜索
```
GET /users?q=keyword  (全文搜索)
GET /users?name.contains=john  (字段搜索)
```

### 字段选择
```
GET /users?fields=id,name,email  (精简返回)
```

## 批量操作设计

### 批量创建
```
POST /users/batch
Body: { items: [...] }
Response: { succeeded: [...], failed: [...] }
```

### 批量删除
```
DELETE /users/batch
Body: { ids: [1, 2, 3] }
```

### 批量操作限制
- 单次最大条目：**100**
- 返回逐条结果（部分成功时返回 207 Multi-Status）

## Idempotency-Key 机制

对非幂等操作（POST），客户端发送 `Idempotency-Key` 请求头：

```
POST /orders
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
```

服务端流程：
1. 收到请求 → 检查 Key 是否已处理
2. 已处理 → 返回缓存结果（不重复执行）
3. 未处理 → 执行 → 存储结果 → 返回
4. Key 过期时间：**24 小时**

## HATEOAS（可选）

对公开 API 可添加超媒体链接：

```json
{
  "id": 1,
  "name": "Task 1",
  "status": "pending",
  "_links": {
    "self": { "href": "/tasks/1" },
    "approve": { "href": "/tasks/1/actions/approve", "method": "POST" },
    "collection": { "href": "/tasks" }
  }
}
```

## 速率限制响应头

```
X-RateLimit-Limit: 100        # 窗口内最大请求数
X-RateLimit-Remaining: 87     # 剩余可用次数
X-RateLimit-Reset: 1619472000 # 窗口重置时间（Unix timestamp）
```

超出限制时返回 429 + `Retry-After` 头。

## 安全要求

- **认证**：Bearer Token（JWT / OAuth2）
- **CORS**：明确列出允许的 Origin，不用 `*`
- **输入验证**：所有输入在 Controller 层验证
- **输出过滤**：不返回内部字段（数据库 ID 策略、密码哈希等）
- **SQL 注入防护**：查询参数不拼接 SQL
- **请求大小限制**：Body 最大 1MB（文件上传除外）
