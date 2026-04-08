# Difficulty Scoring Guide (1-10 Scale)

## Dimension Scoring Criteria

### Scope — Weight 30%

| Score | Criteria |
|-------|---------|
| 1 | Micro-modification within a single file (≤ 5 lines, text/value only) |
| 2 | Local modification within a single file (≤ 20 lines) |
| 3 | Larger single-file modification or small changes across 2-3 closely related files |
| 4 | 3-5 files within a single module |
| 5 | 5-8 files within a single module, or a few files across 2 modules |
| 6 | Across 2-3 modules, involving 8-12 files |
| 7 | Across 3-4 modules, involving 12-20 files |
| 8 | Across 4+ modules, involving 20+ files |
| 9 | Most modules affected, may require batch modifications |
| 10 | Global change, nearly all modules need modification |

### Depth — Weight 25%

| Score | Criteria |
|-------|---------|
| 1 | No logic change (pure text replacement) |
| 2 | Minimal logic (config value changes, style adjustments) |
| 3 | Simple logic (conditional branches, field mapping) |
| 4 | CRUD template operations (add/edit/delete/list pages, formulaic) |
| 5 | Medium logic (form validation, API integration, component state management) |
| 6 | Moderately complex logic (access control, workflows, optimistic updates) |
| 7 | Complex logic (state machines, concurrency handling, caching strategies) |
| 8 | Highly complex (custom build processes, performance-critical path optimization) |
| 9 | Algorithm-intensive (complex data structures, distributed coordination) |
| 10 | System-level complexity (compilers/interpreters, real-time computation engines) |

### Coupling — Weight 20%

| Score | Criteria |
|-------|---------|
| 1 | Completely independent, no external dependencies |
| 2 | Uses external modules but doesn't modify their interfaces |
| 3 | Modifies internal module implementation, interface unchanged |
| 4 | Modifies module interface, known callers ≤ 3 |
| 5 | Modifies module interface, callers 3-5 |
| 6 | Modifies public interface, callers 5-10 |
| 7 | Modifies public interface, call chain > 3 levels deep |
| 8 | Modifies infrastructure components (routing, middleware) |
| 9 | Modifies core abstractions (ORM base class, shared component library) |
| 10 | Modifies underlying framework/runtime, affects all modules globally |

### Risk — Weight 15%

| Score | Criteria |
|-------|---------|
| 1 | Fully reversible, no impact if wrong |
| 2 | Reversible, minimal impact if wrong (dev environment config) |
| 3 | Reversible but requires extra work (feature rollback) |
| 4 | Moderate rollback cost (requires test verification) |
| 5 | Partially irreversible (DB schema with down migration) |
| 6 | Difficult to roll back (production config changes, third-party API integration) |
| 7 | Involves user data format changes |
| 8 | Involves security policies or encryption schemes |
| 9 | Involves payment/financial/compliance flows |
| 10 | Irreversible and high-risk (deleting production data, key rotation) |

### Cognition — Weight 10%

| Score | Criteria |
|-------|---------|
| 1 | Purely mechanical, no domain knowledge required |
| 2 | Requires understanding a single config item or API |
| 3 | Requires understanding one technical concept's basic usage |
| 4 | Requires understanding a complete technical solution (e.g., JWT auth flow) |
| 5 | Requires understanding business domain rules (permission models, billing logic) |
| 6 | Requires understanding complex business processes (workflows, approval chains) |
| 7 | Requires cross-domain knowledge (frontend + backend + database) |
| 8 | Requires cross-domain + business (technical solution + security + business compliance) |
| 9 | Requires expert-level single-domain knowledge (cryptography, distributed consistency) |
| 10 | Requires multiple expert-level domain knowledge (compilation + security + industry regulations) |

## Weighted Average → Level Mapping

```
Weighted Score = Scope×0.30 + Depth×0.25 + Coupling×0.20 + Risk×0.15 + Cognition×0.10
```

| Weighted Score Range | Level | Name |
|---------------------|-------|------|
| 1.0 - 2.0 | L1 | Trivial |
| 2.1 - 4.0 | L2 | Simple |
| 4.1 - 6.0 | L3 | Moderate |
| 6.1 - 8.0 | L4 | Complex |
| 8.1 - 10.0 | L5 | Major |

## Bias Uplift Rule

Instead of full-level uplift, apply a **+0.5 bias to the weighted score**:

```
IF Scope ≤ 2 AND Depth ≤ 2 AND Coupling ≤ 2 AND Risk ≤ 3:
    → Exempt from bias (explicitly note the reason)
ELSE:
    → Weighted score += 0.5 (capped at 10.0)
```

**Effect Examples:**

| Original Weighted | Original Level | After +0.5 | Final Level | Level Changed? |
|-------------------|---------------|------------|-------------|----------------|
| 1.5 | L1 | 2.0 | L1 | No |
| 1.9 | L1 | 2.4 | L2 | Yes (boundary) |
| 3.2 | L2 | 3.7 | L2 | No |
| 3.8 | L2 | 4.3 | L3 | Yes (boundary) |
| 5.5 | L3 | 6.0 | L3 | No |

## Edge Case Handling

| Situation | Handling |
|-----------|---------|
| Vague task description (< 20 words) | Cognition +1, Scope +1 |
| Involves legacy code | Coupling +1 |
| First time working with the module | Cognition +1 |
| User explicitly says "simple" | Don't reduce score for this — assess based on reality |
| Cannot access project context | All dimensions floor +1 |
