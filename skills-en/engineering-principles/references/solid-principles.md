# SOLID Principles

## SRP — Single Responsibility Principle

A class/function should have only one reason to change.

- **DO**: Split `UserService` into `UserAuthService` + `UserProfileService`
- **DON'T**: A single `UserService` handling login, registration, profile updates, and email sending

Rule of thumb: If you need the word "and" to describe a class's responsibility, it likely violates SRP.

## OCP — Open/Closed Principle

Open for extension, closed for modification. Implement new behavior through interfaces/abstract classes rather than modifying existing code.

- **DO**: Define a `PaymentStrategy` interface, add new payment methods as new classes
- **DON'T**: Add `if/else` branches in the `pay()` method for each payment type

Signal: When you find yourself adding another `else if` branch, consider OCP.

## LSP — Liskov Substitution Principle

Subtypes must be substitutable for their base types without altering program correctness.

- **DO**: `Square extends Rectangle` behaves consistently wherever `Rectangle` is used
- **DON'T**: Subclass overrides a method and throws exceptions the parent's callers don't expect

Signal: When a subclass needs to restrict or force certain parent behaviors, the inheritance relationship may be inappropriate.

## ISP — Interface Segregation Principle

Clients should not be forced to depend on interfaces they don't use. Many small interfaces are better than one large interface.

- **DO**: Separate `Readable`, `Writable`, `Closable` interfaces
- **DON'T**: A single `FileOperations` interface with 20 methods where implementers only use 3

Signal: Implementations with many empty methods or `throw new NotImplementedError()`.

## DIP — Dependency Inversion Principle

High-level modules should not depend on low-level modules; both should depend on abstractions.

- **DO**: `OrderService` depends on `OrderRepository` (interface), with concrete implementation injected
- **DON'T**: `OrderService` directly calls `new MySQLOrderRepository()`

Signal: `new` keyword appearing in business classes (should be replaced with dependency injection).
