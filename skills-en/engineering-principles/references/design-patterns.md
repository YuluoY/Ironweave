# Design Patterns Guide

> Core philosophy: **Design serves constraints, not textbooks.** Complexity must pay for itself — if simple code solves the problem, don't introduce a pattern.

## Pattern Selection Master Table

| Signal | Recommended Pattern | Avoid |
|--------|-------------------|-------|
| Multiple `if/else` selecting different behaviors | Strategy / Polymorphism | Flat switch-case |
| Complex creation logic or need flexible switching | Factory | Repeated `new` everywhere |
| Multi-step construction, parameters > 5 | Builder | Ultra-long constructors |
| Multiple objects responding to the same event | Observer / Event Bus | Direct tightly-coupled calls |
| Incompatible interfaces need adapting | Adapter | Modifying third-party source code |
| Add functionality without modifying original class | Decorator / HOC | Deepening inheritance chains |
| Control instance count (connection pools) | Object Pool / DI Container | Manual global singletons |
| Unified operations on tree structures | Composite | Special handling per level |
| State transitions with clear rules | State Machine | Scattered if-else |
| Operations need undo/redo | Command | Manual reversal |
| Deeply nested conditions | Guard Clause early return | Multi-level if-else |
| Linear data transformation pipeline | Pipe/Compose | Temporary variable chains |
| External calls may fail | Circuit Breaker + Exponential Backoff | Infinite retry |

## Browse by Scale

| Scale | File | Content |
|-------|------|---------|
| Function-level | `patterns-small-scale.md` | Guard Clause, Pipe/Compose, Table-Driven, Null Object, Lazy Evaluation, Closure |
| Class/Object-level | `patterns-classic.md` | GoF Creational (Factory/Builder/Singleton), Structural (Decorator/Composite/Facade/Adapter/Proxy), Behavioral (Strategy/Observer/State Machine/Command/Chain of Responsibility) |
| Module-level | `patterns-module.md` | Pipeline/Middleware, Worker Pool, Circuit Breaker, Repository, FSM |
| Frontend | `patterns-frontend.md` | React/Vue pattern selection, styling/routing/error boundaries |
| Backend | `patterns-backend.md` | CQRS, Saga, Event Sourcing, Specification, RBAC/ABAC |
| Cross-domain | `patterns-crosscut.md` | Plugin system, exponential backoff retry, caching strategy, structured logging, DI |
| System-level | `patterns-architecture.md` | Layered/Hexagonal/Clean Architecture/Microkernel/Modular Monolith/Microservices/Event-Driven/Serverless |
| Code quality | `anti-patterns.md` | 10 anti-pattern identification signals + improvement strategies + refactoring priority |
