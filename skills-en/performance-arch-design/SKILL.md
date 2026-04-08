---
name: performance-arch-design
description: >-
  Performance-first design — identifies performance bottlenecks at the architecture level before coding, and designs caching layers, async processing, database indexing, rate limiting, and partitioning strategies. Embeds performance thinking into the system architecture phase to avoid costly post-hoc optimization.
  Use this skill when: the user mentions performance optimization, cache design, cache strategy, Redis, async processing, message queues, database indexes, index design, rate limiting, circuit breakers, sharding, partitioning, N+1 queries, slow queries, high concurrency, performance bottlenecks, QPS, TPS, response time, throughput, performance baselines, load testing targets, hot data, read-write separation, or involves performance-related decisions from steps/06 system architecture.
---

# Performance-First Design

Identify performance bottlenecks at the architecture level before coding: design caching layers, async processing, index strategies, and rate limiting.

---

## Design Flow

```mermaid
graph TB
    INPUT["System Architecture + Business Scenarios"] --> BASELINE["Performance Baseline<br>Target QPS / Response Time"]
    BASELINE --> HOTSPOT["Hotspot Identification<br>High-frequency Reads / Writes / Large Data"]
    HOTSPOT --> CACHE["Cache Layering<br>Local / Distributed / CDN"]
    HOTSPOT --> ASYNC["Async Processing<br>Message Queue / Event-Driven"]
    HOTSPOT --> INDEX["Index Strategy<br>DB Indexes / Full-text Search"]
    CACHE --> PROTECT["Protection Mechanisms<br>Rate Limiting / Circuit Breaker / Degradation"]
    ASYNC --> PROTECT
    INDEX --> PROTECT
    PROTECT --> OUTPUT["Output Performance Plan"]

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

## 1. Performance Baseline Definition

### Target Template

| Metric | Target | Measurement |
|--|--|--|
| P99 Response Time | < 200ms (read) / < 500ms (write) | APM tools |
| QPS | Estimate based on business | Load testing tools |
| Error Rate | < 0.1% | Monitoring & alerting |
| DB Query | < 50ms (single table) / < 200ms (join) | Slow query log |

### Estimation Formula

```
Estimated QPS = DAU x Avg requests per user / Active hours (seconds)
Peak QPS = Estimated QPS x 3 (peak factor)
```

---

## 2. Hotspot Identification

### Read Hotspots

| Pattern | Example | Optimization |
|--|--|--|
| Same data requested heavily | Product details, config | Cache |
| Frequent list queries | Homepage data, leaderboards | Pre-compute + cache |
| Full table scan on large data | Search, reports | Index / full-text search / materialized views |

### Write Hotspots

| Pattern | Example | Optimization |
|--|--|--|
| High-concurrency writes to same row | Inventory deduction, counters | Optimistic lock / bucketed counters |
| Bulk data writes | Log writing, data import | Async + batching |
| Large transactions | Multi-table cascading ops | Split transactions / Saga |

---

## 3. Cache Layering

```mermaid
graph LR
    REQ["Request"] --> L1["L1: Local Cache<br>Caffeine / LRU<br>< 1ms"]
    L1 -->|"miss"| L2["L2: Distributed Cache<br>Redis<br>1-5ms"]
    L2 -->|"miss"| DB["Database<br>10-100ms"]
    DB -->|"backfill"| L2
    L2 -->|"backfill"| L1

    style REQ fill:#f5f5f5,stroke:#616161,color:#212121
    style L1 fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20
    style L2 fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style DB fill:#ffe0b2,stroke:#e65100,color:#bf360c
```

### Cache Strategy Selection

| Scenario | Strategy | TTL | Description |
|--|--|--|--|
| Rarely changing data | Cache-Aside | 24h | Config, dictionary tables |
| Frequent reads, few writes | Cache-Aside + write-invalidate | 1h | User info, product details |
| Balanced read-write | Write-Through | 30min | Session data |
| Write-heavy, read-light | Write-Behind | N/A | Logs, statistics |
| Leaderboards / counters | Native Redis structures | Persistent | SortedSet / HyperLogLog |

### Cache Problem Prevention

| Problem | Cause | Solution |
|--|--|--|
| Cache Penetration | Querying non-existent data | Bloom filter / cache null values (short TTL) |
| Cache Breakdown | Hot key expires | Mutex lock loading / never-expire + async refresh |
| Cache Avalanche | Mass key expiration | TTL with random offset / multi-level cache |

---

## 4. Async Processing

### Scenario Decision

```mermaid
graph TB
    DECIDE{"Is the operation?"} -->|"User needs immediate result"| SYNC["Synchronous"]
    DECIDE -->|"Takes > 2s"| ASYNC_YES["Async + polling/push"]
    DECIDE -->|"Doesn't affect main flow"| ASYNC_FIRE["Async Fire-and-Forget"]
    DECIDE -->|"Requires multi-step orchestration"| SAGA["Saga / Workflow"]

    style SYNC fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20
    style ASYNC_YES fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style ASYNC_FIRE fill:#fff9c4,stroke:#f9a825,color:#e65100
    style SAGA fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c
```

### Message Queue Selection

| Queue | Use Case | Characteristics |
|--|--|--|
| Redis Stream | Lightweight, single-node | Simple, non-persistent |
| RabbitMQ | Small-medium, routing needed | Flexible routing, reliable delivery |
| Kafka | High volume, log streaming | High throughput, persistent, partitioned |

---

## 5. Database Index Strategy

### Index Design Principles

| Principle | Description |
|--|--|
| High-selectivity columns first | Columns with many unique values work best |
| Query conditions = indexes | Columns in WHERE / ORDER BY / JOIN |
| Composite index leftmost prefix | Arrange column order to match query patterns |
| Covering index | Index includes all queried columns, avoids table lookups |
| Avoid over-indexing | Each additional index degrades write performance |

### N+1 Query Prevention

| Scenario | ORM Solution | SQL Solution |
|--|--|--|
| Associated queries | Eager Loading / Join Fetch | LEFT JOIN |
| Batch queries | `findAllById(ids)` | `WHERE id IN (...)` |
| Pagination + association | Query IDs first, then batch load | Subquery pagination |

### Slow Query Prevention Checklist
- [ ] All WHERE conditions covered by indexes
- [ ] No full-table COUNT(*) (use approximate counts or cache)
- [ ] No `SELECT *` (query only needed columns)
- [ ] Pagination uses cursor/Keyset instead of OFFSET
- [ ] Large IN lists split into batches (< 1000 items)

---

## 6. Rate Limiting Strategy

| Algorithm | Use Case | Characteristics |
|--|--|--|
| Fixed Window | Simple limiting | Has boundary burst issues |
| Sliding Window | General APIs | Smooth, slightly more memory |
| Token Bucket | Allow bursts | Accumulates tokens for bursts |
| Leaky Bucket | Strict even rate | Smooths traffic |

### Rate Limiting Dimensions

| Dimension | Example |
|--|--|
| Per-user | 100 requests/min per user |
| Per-IP | 200 requests/min per IP |
| Per-API | 1000 requests/sec globally for an endpoint |
| Per-service | Upstream caller quotas |

---

## 7. Output Checklist

| Deliverable | Description |
|--|--|
| Performance Baseline Doc | Target QPS, response time, error rate |
| Hotspot Analysis Table | Read hotspots + write hotspots + optimization strategies |
| Cache Design Plan | Layering strategy, TTL, protection measures |
| Async Processing Plan | Scenario list + queue selection |
| Index Design Checklist | Index definitions per table |
| Rate Limiting Config | Dimensions + algorithms + thresholds |

---

## References

See `references/` directory for detailed rules:
- `performance-rules.md` — Detailed performance design rules and anti-patterns
