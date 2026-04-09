---
name: performance-arch-design
description: >-
  性能前置设计——在编码前从架构层面识别性能瓶颈并设计缓存分层、异步处理、数据库索引、限流和分区策略。将性能思维融入系统架构设计阶段，避免事后优化的高成本。
  务必在以下场景使用本 skill：用户提到性能优化、缓存设计、缓存策略、Redis、异步处理、消息队列、数据库索引、索引设计、限流、熔断、分库分表、分区、N+1 查询、慢查询、高并发、性能瓶颈、QPS、TPS、响应时间、吞吐量、性能基线、压测目标、热点数据、读写分离，或涉及 engineering-principles 和 tech-stack 产出的架构设计中的性能相关决策。
---

# 性能前置设计

在编码前从架构层面识别性能瓶颈，设计缓存分层、异步处理、索引策略和限流方案。

---

## 设计流程

```mermaid
graph TB
    INPUT["系统架构 + 业务场景"] --> BASELINE["性能基线<br>目标 QPS / 响应时间"]
    BASELINE --> HOTSPOT["热点识别<br>高频读 / 高频写 / 大数据量"]
    HOTSPOT --> CACHE["缓存分层<br>本地 / 分布式 / CDN"]
    HOTSPOT --> ASYNC["异步处理<br>消息队列 / 事件驱动"]
    HOTSPOT --> INDEX["索引策略<br>数据库索引 / 全文检索"]
    CACHE --> PROTECT["保护机制<br>限流 / 熔断 / 降级"]
    ASYNC --> PROTECT
    INDEX --> PROTECT
    PROTECT --> OUTPUT["输出性能方案"]

    style INPUT fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style BASELINE fill:#fff3e0,stroke:#e65100,color:#bf360c
    style HOTSPOT fill:#ffcdd2,stroke:#c62828,color:#b71c1c
    style CACHE fill:#e8eaf6,stroke:#283593,color:#1a237e
    style ASYNC fill:#e8eaf6,stroke:#283593,color:#1a237e
    style INDEX fill:#e8eaf6,stroke:#283593,color:#1a237e
    style PROTECT fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c
    style OUTPUT fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20
```

---

## 1. 性能基线定义

### 目标模板

| 指标 | 目标 | 测量方式 |
|--|--|--|
| P99 响应时间 | < 200ms (读) / < 500ms (写) | APM 工具 |
| QPS | 根据业务估算 | 压测工具 |
| 错误率 | < 0.1% | 监控告警 |
| 数据库查询 | < 50ms (单表) / < 200ms (联表) | 慢查询日志 |

### 估算公式

```
预估 QPS = 日活用户 × 人均请求数 / 有效时长(秒)
峰值 QPS = 预估 QPS × 3（峰值系数）
```

---

## 2. 热点识别

### 读热点

| 特征 | 示例 | 优化策略 |
|--|--|--|
| 同一数据被大量请求 | 商品详情、配置信息 | 缓存 |
| 列表查询频繁 | 首页数据、排行榜 | 预计算 + 缓存 |
| 大数据量全表扫描 | 搜索、报表 | 索引 / 全文检索 / 物化视图 |

### 写热点

| 特征 | 示例 | 优化策略 |
|--|--|--|
| 高并发写同一行 | 库存扣减、计数器 | 乐观锁 / 分桶计数 |
| 批量数据写入 | 日志写入、数据导入 | 异步 + 批量 |
| 大事务 | 多表级联操作 | 拆分事务 / Saga |

---

## 3. 缓存分层

```mermaid
graph LR
    REQ["请求"] --> L1["L1: 本地缓存<br>Caffeine / LRU<br>< 1ms"]
    L1 -->|"未命中"| L2["L2: 分布式缓存<br>Redis<br>1-5ms"]
    L2 -->|"未命中"| DB["数据库<br>10-100ms"]
    DB -->|"回填"| L2
    L2 -->|"回填"| L1

    style REQ fill:#f5f5f5,stroke:#616161,color:#212121
    style L1 fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20
    style L2 fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style DB fill:#ffe0b2,stroke:#e65100,color:#bf360c
```

### 缓存策略选择

| 场景 | 策略 | TTL | 说明 |
|--|--|--|--|
| 基本不变的数据 | Cache-Aside | 24h | 配置、字典表 |
| 频繁读少量写 | Cache-Aside + 写失效 | 1h | 用户信息、商品详情 |
| 读写均衡 | Write-Through | 30min | 会话数据 |
| 写多读少 | Write-Behind | N/A | 日志、统计 |
| 排行榜/计数 | Redis 原生结构 | 持久化 | SortedSet / HyperLogLog |

### 缓存问题防护

| 问题 | 原因 | 解决方案 |
|--|--|--|
| 缓存穿透 | 查询不存在的数据 | 布隆过滤器 / 缓存空值(短 TTL) |
| 缓存击穿 | 热点 Key 过期 | 互斥锁加载 / 永不过期+异步刷新 |
| 缓存雪崩 | 大量 Key 同时过期 | TTL 加随机偏移 / 多级缓存 |

---

## 4. 异步处理

### 适用场景判定

```mermaid
graph TB
    DECIDE{"该操作是否?"} -->|"用户需要即时结果"| SYNC["同步处理"]
    DECIDE -->|"耗时 > 2s"| ASYNC_YES["异步 + 轮询/推送"]
    DECIDE -->|"不影响主流程"| ASYNC_FIRE["异步 Fire-and-Forget"]
    DECIDE -->|"需要多步编排"| SAGA["Saga / 工作流"]

    style SYNC fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20
    style ASYNC_YES fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style ASYNC_FIRE fill:#fff9c4,stroke:#f9a825,color:#e65100
    style SAGA fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c
```

### 消息队列选型

| 队列 | 适用 | 特点 |
|--|--|--|
| Redis Stream | 轻量级、单机 | 简单、不持久化 |
| RabbitMQ | 中小型、需要路由 | 灵活路由、可靠投递 |
| Kafka | 大数据量、日志流 | 高吞吐、持久化、分区 |

---

## 5. 数据库索引策略

### 索引设计原则

| 原则 | 说明 |
|--|--|
| 高选择性字段优先 | 唯一值多的列效果好 |
| 查询条件即索引 | WHERE / ORDER BY / JOIN 的列 |
| 复合索引最左前缀 | 遵循查询模式排列列顺序 |
| 覆盖索引 | 索引包含查询所有列，避免回表 |
| 避免过度索引 | 每增加一个索引，写入性能下降 |

### N+1 查询防护

| 场景 | ORM 解法 | SQL 解法 |
|--|--|--|
| 关联查询 | Eager Loading / Join Fetch | LEFT JOIN |
| 批量查询 | `findAllById(ids)` | `WHERE id IN (...)` |
| 分页+关联 | 先查 ID 再批量加载 | 子查询分页 |

### 慢查询预防清单
- [ ] 所有 WHERE 条件都有索引覆盖
- [ ] 无全表 COUNT(*)（用近似计数或缓存）
- [ ] 无 `SELECT *`（只查需要的列）
- [ ] 分页用游标/Keyset 而非 OFFSET
- [ ] 大 IN 列表拆分为批次（< 1000 条）

---

## 6. 限流策略

| 算法 | 适用 | 特点 |
|--|--|--|
| 固定窗口 | 简单限流 | 有边界突刺问题 |
| 滑动窗口 | 一般 API | 平滑、内存稍多 |
| 令牌桶 | 允许突发 | 可积累令牌应对突发 |
| 漏桶 | 严格匀速 | 流量平滑 |

### 限流维度

| 维度 | 示例 |
|--|--|
| 用户级 | 每用户 100 次/分 |
| IP 级 | 每 IP 200 次/分 |
| API 级 | 某接口全局 1000 次/秒 |
| 服务级 | 上游调用方配额 |

---

## 7. 输出清单

| 制品 | 说明 |
|--|--|
| 性能基线文档 | 目标 QPS、响应时间、错误率 |
| 热点分析表 | 读热点 + 写热点 + 优化策略 |
| 缓存设计方案 | 分层策略、TTL、防护措施 |
| 异步处理方案 | 场景列表 + 队列选型 |
| 索引设计清单 | 每张表的索引定义 |
| 限流配置 | 维度 + 算法 + 阈值 |

---

## 参考

详细规则参见 `references/` 目录：
- `performance-rules.md` — 性能设计详细规则与反模式
