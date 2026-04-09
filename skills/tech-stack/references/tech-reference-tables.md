# 参考技术表

以下表格**仅作选型参考**，每个分类标注了「推荐」项作为默认建议方案，但**推荐不等于强制**——用户可根据团队实际情况选择其他技术（包括表中未列出的），只需在文档中说明选择理由。写入最终文档时需对每项标注「采用 / 不采用 / 待定」并说明理由。

---

## 运行时与包管理

| 分类 | 技术 | 说明 |
|------|------|------|
| 运行时 | Node.js | 建议采用当前**稳定的 LTS**（非最新版）；写明版本或 semver 范围，确保 ≥ 工具链最低要求 |
| 包管理 | pnpm | 写明精确版本，通过 `packageManager` 字段锁定（如 `"packageManager": "pnpm@10.12.0"`）；使用 Corepack 同步；Monorepo 配合 `pnpm-workspace.yaml` |

> **版本一致性检查**：确认 `package.json` 的 `engines`/`packageManager`、`.nvmrc`、CI 配置、Docker 基础镜像中的 Node 版本都指向同一版本。

---

## 前端 · 跨框架通用

| 分类 | 技术 | 说明 |
|------|------|------|
| 构建 | Vite | 极速冷启动，原生 ESM；Vue / React 模板均成熟 |
| 包管理 | pnpm + Monorepo | 节省磁盘，统一多包管理；**pnpm 具体版本见「运行时与包管理」** |
| 样式 | Sass + BEM | 可维护的样式架构 |
| 样式校验 | Stylelint | Sass/CSS 风格一致性 |
| HTTP 请求 | axios | 接口请求封装 |
| 图标库 | Font Awesome | 丰富的矢量图标，支持按需引入 |
| 工具库（通用） | lodash-es | 与框架无关的常用工具函数 |
| 单元测试 | Vitest | 与 Vite 生态一体化 |
| 端到端测试 | Playwright | 全链路 E2E 测试 |
| 库打包（`packages/` 内 TS） | tsdown | 可发布/内部 TS 库的构建与类型声明；**用 tsdown 替代 tsup**，与 tsup 主要选项兼容、便于迁移 |
| 客户端存储 | IndexedDB (via Dexie.js / idb) | 浏览器端大容量结构化存储；Dexie.js 提供简洁的 Promise API，idb 是轻量级封装；适用于离线缓存、草稿暂存、本地数据同步等场景 |

---

## 前端 · Vue 路线（选用时写入）

| 分类 | 技术 | 说明 |
|------|------|------|
| 框架 | Vue 3 + TypeScript | 渐进式框架，类型安全 |
| 路由 | Vue Router | 官方路由方案 |
| 状态管理 | Pinia | 轻量，完整 TypeScript 支持 |
| 组合式工具 | VueUse | 常用组合式函数封装 |
| 国际化 | vue-i18n | 多语言支持（按需引入） |

---

## 前端 · React 路线（选用时写入）

| 分类 | 技术 | 说明 |
|------|------|------|
| 框架 | React 18+ + TypeScript | 组件模型与生态成熟 |
| 路由 | React Router / TanStack Router | 按项目规模与数据加载需求选用 |
| 状态管理 | Zustand、Jotai、Redux Toolkit 等 | 按数据流复杂度选用 |
| 国际化 | react-i18next 等 | 多语言支持（按需引入） |
| 全栈 / SSR（可选） | Next.js、Remix 等 | 需要 SSR 或全栈能力时纳入选型 |

---

## 前端 · UI 与组件库

| 分类 | 技术 | 说明 |
|------|------|------|
| 第三方组件库（Vue） | Element Plus、Ant Design Vue、Naive UI、Vuetify 等 | 按设计规范、无障碍与授权协议选用 |
| 第三方组件库（React） | Ant Design、MUI、Chakra UI、Mantine、Radix 系 + 样式方案 等 | 同上 |
| 自研组件库 | Monorepo 内独立包（如 `packages/ui`） | 与 Design Tokens、文档站、无障碍规范对齐；可与第三方并存或渐进替换 |

---

## 后端（Node.js 系）

| 分类 | 技术 | 说明 |
|------|------|------|
| 框架（推荐） | **NestJS** | 模块化、装饰器驱动的 Node.js 框架，适合中大型项目 |
| 框架（备选） | Express | 最成熟的 Node.js Web 框架，生态丰富，适合轻量级项目 |
| 框架（备选） | Koa | Express 团队打造，更精简的中间件模型，适合对中间件流程有较高控制需求的场景 |
| API 风格 | RESTful | 标准 HTTP 语义接口 |
| 接口文档 | Swagger / OpenAPI | 自动生成，NestJS 官方集成 |
| 参数校验 | class-validator + class-transformer | DTO 层数据校验，NestJS 标配 |
| 认证 | 双 Token + Passport.js | 访问令牌 + 刷新令牌 |
| 权限 | RBAC | 基于角色的访问控制 |
| ORM（推荐） | **TypeORM** | 支持装饰器，与 NestJS 深度集成 |
| ORM（备选） | Prisma | 类型安全的 Schema-first ORM，迁移体验佳 |
| ORM（备选） | Drizzle | 轻量级 TypeScript-first ORM，SQL-like API |
| 数据库（推荐） | **PostgreSQL** | 关系型，生产级稳定性，功能丰富（JSON、全文检索、窗口函数等） |
| 数据库（备选） | MySQL | 广泛使用的关系型数据库，社区成熟 |
| 数据库（备选） | MongoDB | 文档型数据库，适合半结构化数据型场景 |
| 缓存 | Redis | 令牌存储、热点数据缓存 |
| 日志 | Winston / pino | 结构化日志输出 |

---

## 后端（Java 系，备选路线）

| 分类 | 技术 | 说明 |
|------|------|------|
| 框架 | Spring Boot | Java 生态事实标准，企业级项目首选 |
| API 风格 | RESTful / Spring MVC | 控制器 + 服务层标准分层 |
| 接口文档 | SpringDoc (OpenAPI 3) | 注解驱动自动生成，替代旧版 Springfox |
| 参数校验 | Jakarta Validation (Bean Validation) | 注解式校验，Spring Boot 内置支持 |
| 认证 | Spring Security + JWT | 成熟的安全框架，支持多种认证方式 |
| 权限 | RBAC / Spring Security | 基于角色或权限表达式的访问控制 |
| ORM | MyBatis-Plus / JPA (Hibernate) | MyBatis-Plus 灵活控制 SQL；JPA 适合领域驱动设计 |
| 数据库 | 同 Node.js 系 | PostgreSQL（推荐）/ MySQL / MongoDB |
| 缓存 | Redis + Spring Cache | 抽象缓存层，无缝集成 Redis |
| 日志 | SLF4J + Logback | Spring Boot 默认日志框架 |
| 构建 | Maven / Gradle | Maven 稳定成熟，Gradle 构建速度快 |

---

## 运维 & 基础设施（可选）

| 分类 | 技术 | 说明 |
|------|------|------|
| 反向代理 | Nginx | 静态资源托管、接口转发 |
| 容器化（可选） | Docker + Docker Compose | 环境一致性，本地与生产对齐；根据项目部署需求决定是否采用 |

---

## 工程规范

| 分类 | 技术 | 说明 |
|------|------|------|
| 代码校验 | oxlint + oxfmt | 基于 Oxc 的高性能 Lint 与格式化 |
| Git 钩子 | Husky + lint-staged | 提交前自动校验暂存文件 |
| 提交规范 | commitlint | 约束提交信息格式（如 Conventional Commits） |
| 版本管理 | Changesets | monorepo 多包版本与发布管理 |
| CLI 工具 | Commander + Inquirer | 命令行脚手架开发（命令解析 + 交互式问答） |
| CLI 美化 | chalk / picocolors + ora + boxen | 终端彩色输出（picocolors 更轻量零依赖）、加载动画、信息框 |
| CLI 参数解析（备选） | yargs / citty | 功能更丰富的参数解析方案 |
