# 可观测性规则与配置模板

## 日志反模式

| 反模式 | 问题 | 正确做法 |
|--|--|--|
| 记录敏感信息 | 数据泄漏风险 | 脱敏或不记录 |
| 日志拼接字符串 | 性能浪费 | 使用占位符 `log.info("x={}", x)` |
| catch 中不记日志 | 问题不可追踪 | 至少记 WARN |
| 每个方法都记日志 | 日志爆炸 | 只在关键节点记录 |
| 日志无上下文 | 无法关联 | 带 traceId、userId、requestId |
| 日志格式不统一 | 无法解析 | 统一 JSON 格式 |
| DEBUG 日志在生产开 | 性能下降 | 生产默认 INFO，动态调级 |

## 脱敏规则

| 数据类型 | 脱敏方式 | 示例 |
|--|--|--|
| 手机号 | 中间 4 位 * | 138****1234 |
| 邮箱 | 用户名 * | a***@example.com |
| 身份证 | 中间 * | 110***********1234 |
| 银行卡 | 只显示后 4 位 | ****1234 |
| Token | 完全隐藏 | [REDACTED] |
| 密码 | 完全隐藏 | [REDACTED] |

## 请求/响应日志模板

### 请求日志（拦截器）

```java
@Component
public class RequestLoggingInterceptor implements HandlerInterceptor {

    @Override
    public boolean preHandle(HttpServletRequest request,
                             HttpServletResponse response,
                             Object handler) {
        log.info("请求开始 method={} path={} query={} userId={}",
            request.getMethod(),
            request.getRequestURI(),
            request.getQueryString(),
            getUserId(request));
        request.setAttribute("startTime", System.currentTimeMillis());
        return true;
    }

    @Override
    public void afterCompletion(HttpServletRequest request,
                                HttpServletResponse response,
                                Object handler, Exception ex) {
        long duration = System.currentTimeMillis() -
            (long) request.getAttribute("startTime");
        log.info("请求结束 method={} path={} status={} duration={}ms",
            request.getMethod(),
            request.getRequestURI(),
            response.getStatus(),
            duration);
    }
}
```

## Grafana Dashboard 模板

### API 概览面板（必备图表）

| 图表 | 类型 | PromQL |
|--|--|--|
| QPS | Time Series | `rate(http_requests_total[5m])` |
| 错误率 | Time Series | `rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])` |
| P50/P95/P99 延迟 | Time Series | `histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))` |
| 活跃连接数 | Gauge | `hikaricp_connections_active` |
| 数据库连接池 | Gauge | `hikaricp_connections{state="active"}` |

### 业务面板

| 图表 | 类型 | PromQL |
|--|--|--|
| 任务创建趋势 | Time Series | `rate(task_created_total[1h])` |
| 任务执行耗时 | Histogram | `task_execution_duration_seconds` |
| 活跃任务数 | Gauge | `task_active_count` |

## Docker Compose 可观测性栈

```yaml
services:
  otel-collector:
    image: otel/opentelemetry-collector-contrib:latest
    ports:
      - "4317:4317"  # gRPC
      - "4318:4318"  # HTTP

  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"  # UI

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"

  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
```

## 可观测性成熟度模型

| 级别 | 能力 | 工具 |
|--|--|--|
| L0 | 无监控 | - |
| L1 | 基础日志 + 健康检查 | 文件日志 + /health |
| L2 | 结构化日志 + 基础指标 | JSON 日志 + Prometheus |
| L3 | 分布式追踪 + 告警 | OpenTelemetry + Alertmanager |
| L4 | SLO 驱动 + 自动扩缩 | Grafana + HPA |
| L5 | AIOps + 自动修复 | 异常检测 + 自动 Runbook |

### 推荐路径
- **MVP 阶段**：L1（结构化日志 + 健康检查）
- **正式上线**：L2-L3（指标 + 追踪 + 告警）
- **规模化后**：L4+（SLO 驱动）
