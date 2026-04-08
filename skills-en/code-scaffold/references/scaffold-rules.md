# Code Scaffold Generation Rules and Checklist

## Scaffold Generation Order

Generate strictly in the following order to ensure correct dependency direction:

1. **Build configuration** — build.gradle / pom.xml / package.json
2. **Common modules** — Unified exceptions, unified responses, global configuration
3. **Domain layer** — Entity → Value Object → Repository interface → Domain Service
4. **Application layer** — Application Service (references Repository interfaces)
5. **Infrastructure layer** — Repository implementation → Mapper → External adapters
6. **Presentation layer** — Controller → DTO (Request/Response)
7. **Test scaffold** — Test base class → Unit tests → Integration tests

## Naming Conventions

### Java / Spring Boot

| Type | Suffix | Package Location |
|--|--|--|
| Controller | `XxxController` | `module/controller/` |
| Application Service | `XxxAppService` | `module/application/` |
| Domain Service | `XxxDomainService` | `module/domain/service/` |
| Entity | `XxxEntity` or domain name directly | `module/domain/entity/` |
| Value Object | `XxxVO` (domain) / `XxxVo` (DTO) | `module/domain/vo/` |
| Repository interface | `XxxRepository` | `module/domain/repository/` |
| Repository implementation | `XxxRepositoryImpl` | `module/infrastructure/repository/` |
| Mapper | `XxxMapper` | `module/infrastructure/mapper/` |
| Request DTO | `XxxRequest` | `module/dto/request/` |
| Response DTO | `XxxResponse` | `module/dto/response/` |

### TypeScript / NestJS

| Type | Naming | File Location |
|--|--|--|
| Controller | `xxx.controller.ts` | `modules/xxx/` |
| Service | `xxx.service.ts` | `modules/xxx/` |
| Entity | `xxx.entity.ts` | `modules/xxx/entities/` |
| DTO | `create-xxx.dto.ts` | `modules/xxx/dto/` |
| Repository | `xxx.repository.ts` | `modules/xxx/` |
| Module | `xxx.module.ts` | `modules/xxx/` |
| Test | `xxx.service.spec.ts` | `modules/xxx/__tests__/` |

## Dependency Injection Rules

### Spring Boot
- Use **constructor injection** (not `@Autowired` field injection)
- Single dependency can omit `@Autowired` (Spring 4.3+)
- When dependencies > 5, consider splitting the Service

### NestJS
- Use **constructor injection** + `@Injectable()`
- Inter-module communication via `exports` / `imports`

## Build Configuration Templates

### Gradle (Kotlin DSL)

```kotlin
plugins {
    java
    id("org.springframework.boot") version "3.x.x"
    id("io.spring.dependency-management") version "1.x.x"
}

java {
    sourceCompatibility = JavaVersion.VERSION_17
}

dependencies {
    // Web
    implementation("org.springframework.boot:spring-boot-starter-web")
    // Validation
    implementation("org.springframework.boot:spring-boot-starter-validation")
    // MyBatis
    implementation("org.mybatis.spring.boot:mybatis-spring-boot-starter:3.x.x")
    // Database
    runtimeOnly("org.xerial:sqlite-jdbc")
    // Test
    testImplementation("org.springframework.boot:spring-boot-starter-test")
}
```

### package.json (NestJS)

```json
{
  "scripts": {
    "build": "nest build",
    "start:dev": "nest start --watch",
    "test": "vitest",
    "test:e2e": "vitest run --config vitest.e2e.config.ts"
  }
}
```

## Configuration File Templates

### application.yml

```yaml
spring:
  application:
    name: project-name
  datasource:
    url: jdbc:sqlite:data/app.db
    driver-class-name: org.sqlite.JDBC

mybatis:
  mapper-locations: classpath:mapper/**/*.xml
  configuration:
    map-underscore-to-camel-case: true

server:
  port: 8080
```

## Scaffold Completion Checklist

- [ ] All aggregate roots have corresponding Entity classes
- [ ] All Entities have Repository interfaces
- [ ] All Repository interfaces have implementations
- [ ] All use cases have ApplicationService methods (may be TODO)
- [ ] All resources have Controller endpoints
- [ ] All endpoints have Request/Response DTOs
- [ ] Unified exception handler created
- [ ] Unified response wrapper created
- [ ] Build configuration complete, compiles successfully
- [ ] Test framework configured, boilerplate test runs
- [ ] Database migration script directory created
- [ ] Directory structure follows layering constraints (no reverse dependencies)
