---
name: api-contract-design
description: >-
  A detailed design tool for API interface contracts and type systems. Starting from domain models and requirement documents, it generates RESTful/GraphQL API endpoint definitions, Request/Response DTO structures, error response standards, OpenAPI specifications, and type code scaffolds.
  Use this skill in the following scenarios: when users need to design API interfaces, define Data Transfer Objects (DTOs), write interface documentation, establish error code standards, or when users say "design API", "define API", "write API contract", "DTO design", "API specification", "error codes", "OpenAPI", "Swagger".
  Use this skill when the user's task involves transforming business models into technical interfaces.
---

# API Contract Design

Starting from domain models + requirement documents, produce complete API interface contracts. All design decisions are expressed as Mermaid flowcharts.

---

## Design Flow

```mermaid
graph TB
    INPUT["Domain Model + Requirements"] --> RESOURCE["Resource Identification<br>Noun Extraction"]
    RESOURCE --> ENDPOINT["Endpoint Design<br>RESTful Mapping"]
    ENDPOINT --> DTO["DTO Structure<br>Request/Response"]
    DTO --> ERROR["Error Response<br>Standardized Design"]
    ERROR --> VERSION["Versioning Strategy"]
    VERSION --> OUTPUT["Output OpenAPI Spec"]

    style INPUT fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style RESOURCE fill:#e8eaf6,stroke:#283593,color:#1a237e
    style ENDPOINT fill:#e8eaf6,stroke:#283593,color:#1a237e
    style DTO fill:#e8eaf6,stroke:#283593,color:#1a237e
    style ERROR fill:#fff3e0,stroke:#e65100,color:#bf360c
    style VERSION fill:#f5f5f5,stroke:#616161,color:#212121
    style OUTPUT fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20
```

---

## 1. Resource Identification

Extract API resources from the domain model:

| Domain Concept | API Resource | Notes |
|--|--|--|
| Aggregate Root | Top-level resource `/resources` | Directly exposed as RESTful resource |
| Entity (non-root) | Sub-resource `/resources/{id}/sub` | Accessed through parent resource |
| Value Object | Embedded in DTO | Not exposed independently |
| Domain Service | Action endpoint `/resources/{id}/actions/do` | Non-CRUD operations |

---

## 2. Endpoint Design Standards

### RESTful Mapping Rules

```mermaid
graph LR
    CRUD{"Operation Type?"} -->|"Create"| POST["POST /resources"]
    CRUD -->|"Read Single"| GET_ONE["GET /resources/{id}"]
    CRUD -->|"Read List"| GET_LIST["GET /resources?filter"]
    CRUD -->|"Full Update"| PUT["PUT /resources/{id}"]
    CRUD -->|"Partial Update"| PATCH["PATCH /resources/{id}"]
    CRUD -->|"Delete"| DELETE["DELETE /resources/{id}"]
    CRUD -->|"Non-CRUD Action"| ACTION["POST /resources/{id}/actions/{verb}"]

    style POST fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20
    style GET_ONE fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style GET_LIST fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style PUT fill:#fff9c4,stroke:#f9a825,color:#e65100
    style PATCH fill:#fff9c4,stroke:#f9a825,color:#e65100
    style DELETE fill:#ffcdd2,stroke:#c62828,color:#b71c1c
    style ACTION fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c
```

### Naming Conventions
- Resource names: Plural form (`/users` not `/user`)
- Paths: kebab-case (`/migration-tasks`)
- Query parameters: camelCase (`?pageSize=20&sortBy=createdAt`)
- Nesting max 2 levels: `/resources/{id}/sub-resources/{subId}`

### Idempotency Requirements

| Method | Idempotent? | Safe? | Notes |
|--|--|--|--|
| GET | Yes | Yes | Read-only, no side effects |
| PUT | Yes | No | Full replacement, repeated execution yields same result |
| DELETE | Yes | No | Delete again returns 404/204 |
| POST | **No** | No | Requires additional mechanism for idempotency (Idempotency-Key) |
| PATCH | **No** | No | Depends on the specific operation |

---

## 3. DTO Design Standards

### Layered Structure

```mermaid
graph LR
    CLIENT["Client"] -->|"Request DTO"| CONTROLLER["Controller"]
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

### DTO Design Principles
- **Request DTO ≠ Entity**: Don't expose internal fields (e.g., id, createdAt are server-generated)
- **Response DTO ≠ Entity**: Trim fields as needed, avoid over-exposure
- **List DTO is slim**: List endpoints return summaries, detail endpoints return full data
- **Flatten nesting**: Avoid > 3 levels of nesting, use ID references instead

### Pagination Standard

```typescript
// Request
interface PaginationQuery {
  page?: number;       // Default 1
  pageSize?: number;   // Default 20, max 100
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

// Response
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

## 4. Error Response Standardization

### Unified Error Format

```typescript
interface ErrorResponse {
  code: string;        // Business error code: "RESOURCE_NOT_FOUND"
  message: string;     // Human-readable message
  details?: Array<{    // Field-level errors (on validation failure)
    field: string;
    message: string;
  }>;
  traceId?: string;    // Distributed trace ID
}
```

### HTTP Status Code Mapping

```mermaid
graph TB
    ERR{"Error Type?"} -->|"Validation Failure"| E400["400 Bad Request<br>+ details array"]
    ERR -->|"Not Authenticated"| E401["401 Unauthorized"]
    ERR -->|"No Permission"| E403["403 Forbidden"]
    ERR -->|"Resource Not Found"| E404["404 Not Found"]
    ERR -->|"Business Rule Conflict"| E409["409 Conflict"]
    ERR -->|"Too Many Requests"| E429["429 Too Many Requests"]
    ERR -->|"Internal Server Error"| E500["500 Internal Server Error"]

    style E400 fill:#fff9c4,stroke:#f9a825,color:#e65100
    style E401 fill:#ffcdd2,stroke:#c62828,color:#b71c1c
    style E403 fill:#ffcdd2,stroke:#c62828,color:#b71c1c
    style E404 fill:#ffe0b2,stroke:#e65100,color:#bf360c
    style E409 fill:#ffe0b2,stroke:#e65100,color:#bf360c
    style E429 fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c
    style E500 fill:#ffcdd2,stroke:#c62828,color:#b71c1c
```

### Error Code Naming Conventions
- All uppercase + underscore: `RESOURCE_NOT_FOUND`
- Prefix by module: `USER_NOT_FOUND`, `ORDER_ALREADY_PAID`
- Use semantic strings, not numeric codes

---

## 5. Versioning Strategy

```mermaid
graph TB
    STRAT{"Version Strategy?"} -->|"Internal System/MVP"| NO_V["No Versioning<br>Evolve Directly"]
    STRAT -->|"Public API"| URL_V["URL Versioning<br>/api/v1/resources"]
    STRAT -->|"Between Microservices"| HEADER_V["Header Versioning<br>Accept: application/vnd.app.v2+json"]

    NO_V --> COMPAT["Backward Compatibility:<br>Only add fields, never remove"]
    URL_V --> COMPAT
    HEADER_V --> COMPAT

    style NO_V fill:#c8e6c9,stroke:#2e7d32,color:#1b5e20
    style URL_V fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style HEADER_V fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c
    style COMPAT fill:#fff3e0,stroke:#e65100,color:#bf360c
```

### Deprecation Management
- After a new version launches, keep the old version for at least **6 months**
- Add `Deprecation: true` + `Sunset: <date>` response headers
- Mark deprecation status in documentation

---

## 6. Output Checklist

After design is complete, produce the following artifacts:

| Artifact | Format | Notes |
|--|--|--|
| API endpoint list | Markdown table | Path, method, description, idempotent? |
| Request/Response DTOs | TypeScript/Java interface definitions | DTOs for each endpoint |
| Error code catalog | Markdown table | code + HTTP status + usage scenario |
| OpenAPI specification | YAML | Importable into Swagger UI |
| Contract test cases | Description | Consumer-Provider verification points |

---

## Reference

For detailed specifications, see the `references/` directory:
- `api-design-rules.md` — Detailed RESTful design rules and anti-patterns
