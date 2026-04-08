# 性能设计规则与反模式

## 性能反模式

| 反模式 | 问题 | 解决方案 |
|--|--|--|
| N+1 查询 | 循环中逐条查询 | 批量查询 / JOIN |
| SELECT * | 返回不需要的列 | 显式列出字段 |
| 大事务 | 长时间持锁 | 拆分事务、减小范围 |
| OFFSET 分页 | 深分页性能差 | Keyset 游标分页 |
| 无索引全表扫描 | 查询 O(n) | 添加合适索引 |
| 缓存 key 无 TTL | 内存持续增长 | 所有 key 设置 TTL |
| 同步调用链过长 | 延迟累加 | 异步化非关键路径 |
| 数据库当队列用 | 轮询开销大 | 使用消息队列 |
| 日志中序列化大对象 | 影响吞吐 | 只记关键字段 |
| 无连接池 | 连接创建开销 | 配置连接池(HikariCP) |

## 缓存 Key 设计规范

### 命名格式
```
{app}:{module}:{entity}:{id}[:suffix]
```

示例：
- `myapp:user:profile:12345`
- `myapp:order:list:user:12345:page:1`
- `myapp:config:system:global`

### 规则
- Key 长度 < 128 字节
- 不包含空格和特殊字符
- 使用 `:` 分隔层级
- 批量操作用 `{hash_tag}` 保证同槽

## Redis 数据结构选型

| 场景 | 数据结构 | 示例 |
|--|--|--|
| 对象缓存 | String (JSON) | 用户信息 |
| 计数器 | String (INCR) | API 调用次数 |
| 集合去重 | Set | 用户在线列表 |
| 排行榜 | Sorted Set | 积分排行 |
| 近似计数 | HyperLogLog | UV 统计 |
| 布隆过滤 | Bloom Filter (module) | 缓存穿透防护 |
| 限流 | String + Lua 脚本 | 滑动窗口计数 |
| 分布式锁 | String + NX + PX | Redisson |

## 连接池配置参考

### HikariCP (Java)

| 参数 | 推荐值 | 说明 |
|--|--|--|
| maximumPoolSize | CPU 核心数 * 2 + 1 | 数据库连接上限 |
| minimumIdle | 与 maximumPoolSize 相同 | 固定连接数性能最优 |
| connectionTimeout | 30000ms | 获取连接超时 |
| idleTimeout | 600000ms (10min) | 空闲连接存活时间 |
| maxLifetime | 1800000ms (30min) | 连接最大存活时间 |

## Keyset 分页 vs OFFSET 分页

### OFFSET 分页（不推荐深分页）
```sql
SELECT * FROM orders ORDER BY id LIMIT 20 OFFSET 10000;
-- 数据库需要扫描 10020 行再丢弃前 10000 行
```

### Keyset 分页（推荐）
```sql
SELECT * FROM orders WHERE id > :lastId ORDER BY id LIMIT 20;
-- 直接从索引定位，性能恒定
```

### 前端配合
```json
{
  "data": [...],
  "pagination": {
    "nextCursor": "eyJpZCI6MTAyMH0=",
    "hasMore": true
  }
}
```

## 压测检查清单

- [ ] 已确定目标 QPS 和 P99 响应时间
- [ ] 压测数据量与生产一致（或同量级）
- [ ] 压测覆盖热点接口（读 + 写）
- [ ] 观察数据库连接池使用率
- [ ] 观察 CPU / 内存 / 网络 IO
- [ ] 观察慢查询和慢日志
- [ ] 压测期间无 OOM 或连接泄漏
- [ ] 压测后数据一致性验证
