# Performance Design Rules and Anti-Patterns

## Performance Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--|--|--|
| N+1 queries | Row-by-row queries in loops | Batch queries / JOIN |
| SELECT * | Returns unneeded columns | Explicitly list fields |
| Large transactions | Holds locks for too long | Split transactions, reduce scope |
| OFFSET pagination | Poor performance for deep pages | Keyset cursor pagination |
| Full table scan without index | Query is O(n) | Add appropriate indexes |
| Cache key without TTL | Memory grows indefinitely | Set TTL on all keys |
| Long synchronous call chain | Latency accumulates | Async non-critical paths |
| Database as queue | Polling overhead | Use message queue |
| Serializing large objects in logs | Impacts throughput | Log only key fields |
| No connection pool | Connection creation overhead | Configure connection pool (HikariCP) |

## Cache Key Design Standards

### Naming Format
```
{app}:{module}:{entity}:{id}[:suffix]
```

Examples:
- `myapp:user:profile:12345`
- `myapp:order:list:user:12345:page:1`
- `myapp:config:system:global`

### Rules
- Key length < 128 bytes
- No spaces or special characters
- Use `:` to separate hierarchy levels
- Use `{hash_tag}` for batch operations to ensure same slot

## Redis Data Structure Selection

| Scenario | Data Structure | Example |
|--|--|--|
| Object caching | String (JSON) | User info |
| Counter | String (INCR) | API call count |
| Set deduplication | Set | Online user list |
| Leaderboard | Sorted Set | Score ranking |
| Approximate count | HyperLogLog | UV statistics |
| Bloom filter | Bloom Filter (module) | Cache penetration protection |
| Rate limiting | String + Lua script | Sliding window counter |
| Distributed lock | String + NX + PX | Redisson |

## Connection Pool Configuration Reference

### HikariCP (Java)

| Parameter | Recommended Value | Description |
|--|--|--|
| maximumPoolSize | CPU cores * 2 + 1 | Database connection upper limit |
| minimumIdle | Same as maximumPoolSize | Fixed connection count for optimal performance |
| connectionTimeout | 30000ms | Timeout for acquiring a connection |
| idleTimeout | 600000ms (10min) | Idle connection survival time |
| maxLifetime | 1800000ms (30min) | Maximum connection lifetime |

## Keyset Pagination vs OFFSET Pagination

### OFFSET Pagination (Not Recommended for Deep Pages)
```sql
SELECT * FROM orders ORDER BY id LIMIT 20 OFFSET 10000;
-- Database must scan 10020 rows then discard the first 10000
```

### Keyset Pagination (Recommended)
```sql
SELECT * FROM orders WHERE id > :lastId ORDER BY id LIMIT 20;
-- Seeks directly via index, constant performance
```

### Frontend Integration
```json
{
  "data": [...],
  "pagination": {
    "nextCursor": "eyJpZCI6MTAyMH0=",
    "hasMore": true
  }
}
```

## Load Testing Checklist

- [ ] Target QPS and P99 response time defined
- [ ] Test data volume matches production (or same order of magnitude)
- [ ] Load test covers hotspot endpoints (read + write)
- [ ] Monitor database connection pool utilization
- [ ] Monitor CPU / memory / network IO
- [ ] Monitor slow queries and slow logs
- [ ] No OOM or connection leaks during testing
- [ ] Data consistency verification after testing
