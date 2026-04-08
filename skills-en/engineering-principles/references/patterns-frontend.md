# Frontend-Specific Patterns

## React

| Scenario | Recommended | Avoid |
|----------|-------------|-------|
| Cross-component state | Context + useReducer / Zustand | Props drilling > 3 levels |
| Logic reuse | Custom Hooks | HOC chains / render props nesting |
| Async data | React Query / SWR | Hand-written loading/error/data |
| Complex forms | react-hook-form / FSM | Scattered useState |
| Large lists | Virtualization (react-window) | Full rendering |
| Cross-page communication | URL state / route params | Global store for page state |

## Vue

| Scenario | Recommended | Avoid |
|----------|-------------|-------|
| Logic reuse | Composables | Mixins |
| Cross-component state | Pinia | Vuex (deprecated) |
| Reactive derivation | computed / watchEffect | Storing derivable values in state |
| Component communication | props + emit / provide-inject | Use provide-inject beyond 2 levels |

## General Frontend

- **Style organization**: CSS Modules / SCSS + BEM / Tailwind — align with team standards
- **Routing**: Group by feature domain, lazy-load route components
- **Error boundaries**: React ErrorBoundary / Vue onErrorCaptured
