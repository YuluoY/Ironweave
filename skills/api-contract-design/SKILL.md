---
name: api-contract-design
description: >-
  API 接口契约与类型系统的详细设计工具。从领域模型和需求文档出发，生成 RESTful/GraphQL API 端点定义、Request/Response DTO 结构、错误响应标准、OpenAPI 规范以及类型代码骨架。
  务必在以下场景使用本 skill：用户需要设计 API 接口、定义数据传输对象(DTO)、编写接口文档、制定错误码规范，或者用户说"设计接口"、"定义 API"、"写接口契约"、"DTO 设计"、"接口规范"、"错误码"、"OpenAPI"、"Swagger"。
  当用户的任务涉及从业务模型到技术接口的转化时使用本 skill。
---

# API 契约设计

从领域模型 + 需求文档出发，产出完整的 API 接口契约。所有设计决策以 Mermaid 流程图表达。

---

## 设计流程

```mermaid
graph TB
    INPUT["领域模型 + 需求文档"] --> RESOURCE["资源识别<br>名词提取"]
    RESOURCE --> ENDPOINT["端点设计<br>RESTful 映射"]
    ENDPOINT --> DTO["DTO 结构<br>Request/Response"]
    DTO --> ERROR["错误响应<br>标准化设计"]
    ERROR --> VERSION["版本策略"]
    VERSION --> OUTPUT["输出 OpenAPI 规范"]

    style INPUT fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style RESOURCE fill:#e8eaf6,stroke:#283593,color:#1a237e
    style ENDPOINT fill:#e8eaf6,stroke:#283593,color:#1a237e
    style DTO fill:#e8eaf6,stroke:#283593,color:#1a237e
    style ERROR fill:#fff3e0,stroke:#e65100,color:#bf360c
    style VERSION fill:#f5f5f5,stroke:#616161,color:#212121
    style OUTPUT fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20
```

---

## 1. 资源识别

从领域模型中提取 API 资源：

| 领域概念 | API 资源 | 说明 |
|--|--|--|
| 聚合根 | 顶级资源 `/resources` | 直接暴露为 RESTful 资源 |
| 实体(非聚合根) | 子资源 `/resources/{id}/sub` | 通过父资源访问 |
| 值对象 | 内嵌在 DTO 中 | 不单独暴露 |
| 领域服务 | 动作端点 `/resources/{id}/actions/do` | 非 CRUD 操作 |

---

## 2. 端点设计规范

### RESTful 映射规则

```mermaid
graph LR
    CRUD{"操作类型?"} -->|"创建"| POST["POST /resources"]
    CRUD -->|"读取单个"| GET_ONE["GET /resources/{id}"]
    CRUD -->|"读取列表"| GET_LIST["GET /resources?filter"]
    CRUD -->|"全量更新"| PUT["PUT /resources/{id}"]
    CRUD -->|"部分更新"| PATCH["PATCH /resources/{id}"]
    CRUD -->|"删除"| DELETE["DELETE /resources/{id}"]
    CRUD -->|"非 CRUD 动作"| ACTION["POST /resources/{id}/actions/{verb}"]

    style POST fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20
    style GET_ONE fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style GET_LIST fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style PUT fill:#fff9c4,stroke:#f9a825,color:#e65100
    style PATCH fill:#fff9c4,stroke:#f9a825,color:#e65100
    style DELETE fill:#ffcdd2,stroke:#c62828,color:#b71c1c
    style ACTION fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c
```

### 命名规范
- 资源名：复数形式（`/users` 非 `/user`）
- 路径：kebab-case（`/migration-tasks`）
- 查询参数：camelCase（`?pageSize=20&sortBy=createdAt`）
- 嵌套不超过 2 层：`/resources/{id}/sub-resources/{subId}`

### 幂等性要求

| 方法 | 幂等? | 安全? | 说明 |
|--|--|--|--|
| GET | 是 | 是 | 只读，无副作用 |
| PUT | 是 | 否 | 全量替换，重复执行结果相同 |
| DELETE | 是 | 否 | 删除后再删返回 404/204 |
| POST | **否** | 否 | 需要额外机制保证幂等（Idempotency-Key） |
| PATCH | **否** | 否 | 视具体操作 |

---

## 3. DTO 设计规范

### 分层结构

```mermaid
graph LR
    CLIENT["客户端"] -->|"Request DTO"| CONTROLLER["Controller"]
    CONTROLLER -->|"Command/Query"| SERVICE["Service"]
    SERVICE -->|"Entity"| REPO["Repository"]
    REPO -->|"Entity"| SERVICE
    SERVICE -->|"Response DTO"| CONTROLLER
    CONTROLLER -->|"Response DTO"| CLIENT

    style CLIENT fill:#f5f5f5,stroke:#616161,color:#212121
    style CONTROLLER fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style SERVICE fill:#e8eaf6,stroke:#283593,color:#1a237e
    style REPO fill:#ffe0b2,stroke:#e65100,color:#bf360c
```

### DTO 设计原则
- **Request DTO ≠ Entity**：不暴露内部字段（如 id、createdAt 由服务端生成）
- **Response DTO ≠ Entity**：按需裁剪字段，避免过度暴露
- **列表 DTO 精简**：列表接口返回摘要，详情接口返回完整
- **嵌套扁平化**：避免 > 3 层嵌套，可用 ID 引用代替

### 分页标准

```typescript
// 请求
interface PaginationQuery {
  page?: number;       // 默认 1
  pageSize?: number;   // 默认 20，最大 100
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

// 响应
interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
  };
}
```

---

## 4. 错误响应标准化

### 统一错误格式

```typescript
interface ErrorResponse {
  code: string;        // 业务错误码: "RESOURCE_NOT_FOUND"
  message: string;     // 人类可读信息
  details?: Array<{    // 字段级错误（验证失败时）
    field: string;
    message: string;
  }>;
  traceId?: string;    // 链路追踪 ID
}
```

### HTTP 状态码映射

```mermaid
graph TB
    ERR{"错误类型?"} -->|"参数校验失败"| E400["400 Bad Request<br>+ details 数组"]
    ERR -->|"未认证"| E401["401 Unauthorized"]
    ERR -->|"无权限"| E403["403 Forbidden"]
    ERR -->|"资源不存在"| E404["404 Not Found"]
    ERR -->|"业务规则冲突"| E409["409 Conflict"]
    ERR -->|"请求过多"| E429["429 Too Many Requests"]
    ERR -->|"服务器内部错误"| E500["500 Internal Server Error"]

    style E400 fill:#fff9c4,stroke:#f9a825,color:#e65100
    style E401 fill:#ffcdd2,stroke:#c62828,color:#b71c1c
    style E403 fill:#ffcdd2,stroke:#c62828,color:#b71c1c
    style E404 fill:#ffe0b2,stroke:#e65100,color:#bf360c
    style E409 fill:#ffe0b2,stroke:#e65100,color:#bf360c
    style E429 fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c
    style E500 fill:#ffcdd2,stroke:#c62828,color:#b71c1c
```

### 错误码命名规范
- 全大写 + 下划线：`RESOURCE_NOT_FOUND`
- 前缀按模块：`USER_NOT_FOUND`、`ORDER_ALREADY_PAID`
- 不用数字编码，用语义化字符串

---

## 5. 版本管理策略

```mermaid
graph TB
    STRAT{"版本策略选择"} -->|"内部系统/MVP"| NO_V["不版本化<br>直接演进"]
    STRAT -->|"公开 API"| URL_V["URL 版本<br>/api/v1/resources"]
    STRAT -->|"微服务间"| HEADER_V["Header 版本<br>Accept: application/vnd.app.v2+json"]

    NO_V --> COMPAT["向后兼容原则:<br>只加字段不删字段"]
    URL_V --> COMPAT
    HEADER_V --> COMPAT

    style NO_V fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20
    style URL_V fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style HEADER_V fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c
    style COMPAT fill:#fff3e0,stroke:#e65100,color:#bf360c
```

### 弃用期管理
- 新版本上线后，旧版本至少保留 **6 个月**
- 响应头添加 `Deprecation: true` + `Sunset: <date>`
- 文档标注弃用状态

---

## 6. 输出清单

设计完成后产出以下制品：

| 制品 | 格式 | 说明 |
|--|--|--|
| API 端点清单 | Markdown 表格 | 路径、方法、说明、是否幂等 |
| Request/Response DTO | TypeScript/Java 接口定义 | 每个端点的 DTO |
| 错误码目录 | Markdown 表格 | code + HTTP status + 使用场景 |
| OpenAPI 规范 | YAML | 可导入 Swagger UI |
| 契约测试用例 | 描述 | Consumer-Provider 验证点 |

---

## 参考

详细规范参见 `references/` 目录：
- `api-design-rules.md` — RESTful 设计详细规则与反模式
