# Observability Rules and Configuration Templates

## Logging Anti-Patterns

| Anti-Pattern | Problem | Correct Approach |
|--|--|--|
| Logging sensitive information | Data leak risk | Mask or don't log |
| String concatenation in logs | Performance waste | Use placeholders `log.info("x={}", x)` |
| No logging in catch blocks | Issues become untraceable | Log at least WARN |
| Logging in every method | Log explosion | Log only at critical checkpoints |
| Logs without context | Cannot correlate | Include traceId, userId, requestId |
| Inconsistent log format | Cannot parse | Use unified JSON format |
| DEBUG logs on in production | Performance degradation | Production defaults to INFO, dynamic level adjustment |

## Data Masking Rules

| Data Type | Masking Method | Example |
|--|--|--|
| Phone number | Mask middle 4 digits | 138****1234 |
| Email | Mask username | a***@example.com |
| National ID | Mask middle | 110***********1234 |
| Bank card | Show last 4 only | ****1234 |
| Token | Fully hidden | [REDACTED] |
| Password | Fully hidden | [REDACTED] |

## Request/Response Log Template

### Request Logging (Interceptor)

```java
@Component
public class RequestLoggingInterceptor implements HandlerInterceptor {

    @Override
    public boolean preHandle(HttpServletRequest request,
                             HttpServletResponse response,
                             Object handler) {
        log.info("Request started method={} path={} query={} userId={}",
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
        log.info("Request completed method={} path={} status={} duration={}ms",
            request.getMethod(),
            request.getRequestURI(),
            response.getStatus(),
            duration);
    }
}
```

## Grafana Dashboard Templates

### API Overview Panel (Essential Charts)

| Chart | Type | PromQL |
|--|--|--|
| QPS | Time Series | `rate(http_requests_total[5m])` |
| Error rate | Time Series | `rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])` |
| P50/P95/P99 latency | Time Series | `histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))` |
| Active connections | Gauge | `hikaricp_connections_active` |
| DB connection pool | Gauge | `hikaricp_connections{state="active"}` |

### Business Panel

| Chart | Type | PromQL |
|--|--|--|
| Task creation trend | Time Series | `rate(task_created_total[1h])` |
| Task execution duration | Histogram | `task_execution_duration_seconds` |
| Active task count | Gauge | `task_active_count` |

## Docker Compose Observability Stack

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

## Observability Maturity Model

| Level | Capability | Tools |
|--|--|--|
| L0 | No monitoring | - |
| L1 | Basic logs + health checks | File logs + /health |
| L2 | Structured logs + basic metrics | JSON logs + Prometheus |
| L3 | Distributed tracing + alerting | OpenTelemetry + Alertmanager |
| L4 | SLO-driven + auto-scaling | Grafana + HPA |
| L5 | AIOps + auto-remediation | Anomaly detection + automated runbooks |

### Recommended Path
- **MVP phase**: L1 (structured logs + health checks)
- **Production launch**: L2-L3 (metrics + tracing + alerting)
- **At scale**: L4+ (SLO-driven)
