# 前端特定模式

## React

| 场景 | 推荐 | 避免 |
|------|------|------|
| 跨组件状态 | Context + useReducer / Zustand | props drilling > 3 层 |
| 逻辑复用 | Custom Hooks | HOC 链 / render props 嵌套 |
| 异步数据 | React Query / SWR | 手写 loading/error/data |
| 复杂表单 | react-hook-form / FSM | 散落 useState |
| 大列表 | 虚拟化 (react-window) | 全量渲染 |
| 跨页通信 | URL 状态 / 路由参数 | 全局 store 存页面状态 |

## Vue

| 场景 | 推荐 | 避免 |
|------|------|------|
| 逻辑复用 | Composables | Mixins |
| 跨组件状态 | Pinia | Vuex（已过时） |
| 响应式转换 | computed / watchEffect | 能推导的存 state |
| 组件通信 | props + emit / provide-inject | 超 2 层用 provide-inject |

## 通用前端

- **样式组织**: CSS Modules / SCSS + BEM / Tailwind — 按团队统一
- **路由**: 按功能域分组，懒加载路由组件
- **错误边界**: React ErrorBoundary / Vue onErrorCaptured
