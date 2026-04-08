# 代码骨架生成规则与检查清单

## 骨架生成顺序

严格按以下顺序生成，确保依赖方向正确：

1. **构建配置** — build.gradle / pom.xml / package.json
2. **公共模块** — 统一异常、统一响应、全局配置
3. **领域层** — Entity → Value Object → Repository 接口 → Domain Service
4. **应用层** — Application Service（引用 Repository 接口）
5. **基础设施层** — Repository 实现 → Mapper → 外部适配器
6. **表现层** — Controller → DTO（Request/Response）
7. **测试骨架** — 测试基类 → 单元测试 → 集成测试

## 命名规范

### Java / Spring Boot

| 类型 | 后缀 | 包位置 |
|--|--|--|
| Controller | `XxxController` | `module/controller/` |
| Application Service | `XxxAppService` | `module/application/` |
| Domain Service | `XxxDomainService` | `module/domain/service/` |
| Entity | `XxxEntity` 或直接领域名 | `module/domain/entity/` |
| Value Object | `XxxVO` (领域) / `XxxVo` (DTO) | `module/domain/vo/` |
| Repository 接口 | `XxxRepository` | `module/domain/repository/` |
| Repository 实现 | `XxxRepositoryImpl` | `module/infrastructure/repository/` |
| Mapper | `XxxMapper` | `module/infrastructure/mapper/` |
| Request DTO | `XxxRequest` | `module/dto/request/` |
| Response DTO | `XxxResponse` | `module/dto/response/` |

### TypeScript / NestJS

| 类型 | 命名 | 文件位置 |
|--|--|--|
| Controller | `xxx.controller.ts` | `modules/xxx/` |
| Service | `xxx.service.ts` | `modules/xxx/` |
| Entity | `xxx.entity.ts` | `modules/xxx/entities/` |
| DTO | `create-xxx.dto.ts` | `modules/xxx/dto/` |
| Repository | `xxx.repository.ts` | `modules/xxx/` |
| Module | `xxx.module.ts` | `modules/xxx/` |
| Test | `xxx.service.spec.ts` | `modules/xxx/__tests__/` |

## 依赖注入规则

### Spring Boot
- 使用**构造器注入**（不用 `@Autowired` 字段注入）
- 单个依赖可省略 `@Autowired`（Spring 4.3+）
- 依赖 > 5 个时考虑拆分 Service

### NestJS
- 使用**构造器注入** + `@Injectable()`
- 模块间通信通过 `exports` / `imports`

## 构建配置模板

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

## 配置文件模板

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

## 骨架完成检查清单

- [ ] 所有聚合根都有对应 Entity 类
- [ ] 所有 Entity 都有 Repository 接口
- [ ] 所有 Repository 接口都有 Implementation
- [ ] 所有用例都有 ApplicationService 方法（可为 TODO）
- [ ] 所有资源都有 Controller 端点
- [ ] 所有端点都有 Request/Response DTO
- [ ] 统一异常处理器已创建
- [ ] 统一响应封装已创建
- [ ] 构建配置完整，可编译通过
- [ ] 测试框架已配置，样板测试可运行
- [ ] 数据库迁移脚本目录已创建
- [ ] 目录结构符合分层约束（无反向依赖）
