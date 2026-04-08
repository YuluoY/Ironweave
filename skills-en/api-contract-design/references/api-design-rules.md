# RESTful API Design Rules and Anti-Patterns

## Naming Anti-Patterns

| Anti-Pattern | Correct Form | Reason |
|--|--|--|
| `/getUsers` | `GET /users` | Verb goes in the method, not the path |
| `/user/list` | `GET /users` | Use plural nouns |
| `/user_roles` | `/user-roles` | Paths use kebab-case |
| `/Users` | `/users` | Paths are all lowercase |
| `/users/{id}/tasks/{taskId}/comments/{commentId}/replies` | Max 2 levels of nesting | Deep nesting reduces usability |

## Query Parameter Standards

### Filtering
```
GET /users?status=active&role=admin
GET /orders?createdAfter=2026-01-01&createdBefore=2026-12-31
```

### Sorting
```
GET /users?sortBy=createdAt&sortOrder=desc
GET /users?sort=-createdAt,+name  (compact style)
```

### Search
```
GET /users?q=keyword  (full-text search)
GET /users?name.contains=john  (field search)
```

### Field Selection
```
GET /users?fields=id,name,email  (slim response)
```

## Batch Operations Design

### Batch Create
```
POST /users/batch
Body: { items: [...] }
Response: { succeeded: [...], failed: [...] }
```

### Batch Delete
```
DELETE /users/batch
Body: { ids: [1, 2, 3] }
```

### Batch Operation Limits
- Maximum items per request: **100**
- Return per-item results (use 207 Multi-Status for partial success)

## Idempotency-Key Mechanism

For non-idempotent operations (POST), the client sends an `Idempotency-Key` request header:

```
POST /orders
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
```

Server-side flow:
1. Receive request → Check if Key has been processed
2. Already processed → Return cached result (no re-execution)
3. Not processed → Execute → Store result → Return
4. Key expiration: **24 hours**

## HATEOAS (Optional)

For public APIs, hypermedia links can be added:

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

## Rate Limiting Response Headers

```
X-RateLimit-Limit: 100        # Max requests per window
X-RateLimit-Remaining: 87     # Remaining available requests
X-RateLimit-Reset: 1619472000 # Window reset time (Unix timestamp)
```

Return 429 + `Retry-After` header when limit exceeded.

## Security Requirements

- **Authentication**: Bearer Token (JWT / OAuth2)
- **CORS**: Explicitly list allowed Origins, never use `*`
- **Input validation**: Validate all input at the Controller layer
- **Output filtering**: Don't return internal fields (database ID strategies, password hashes, etc.)
- **SQL injection protection**: Never concatenate SQL from query parameters
- **Request size limit**: Body max 1MB (except file uploads)
