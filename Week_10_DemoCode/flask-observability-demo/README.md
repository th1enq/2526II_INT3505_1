# Flask Observability Demo (logs/metrics/tracing) + Rate limit + Circuit breaker

Demo nhỏ bằng Python Flask:
- API đơn giản: `/health`, `/v1/echo`, `/v1/items`, `/v1/external`
- Observability:
  - Logs + **audit logs** (JSON)
  - Metrics Prometheus: `/metrics`
  - Tracing OpenTelemetry (OTLP nếu cấu hình, không thì in ra console)
- Rate limiting (Flask-Limiter)
- Circuit breaker (pybreaker) cho dependency ngoài

> Ghi chú: **Winston** là logger cho Node.js; trong Python demo này dùng `logging` + `python-json-logger`.

## Chạy local

```bash
cd /home/th1enq/Documents/UET_Archives/2526II_INT3505_1/Week_10_DemoCode/flask-observability-demo
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -r requirements.txt
python app.py
```

Nếu gặp lỗi `ModuleNotFoundError: No module named 'pkg_resources'` (hay gặp trên Python 3.13 venv), cài thêm:

```bash
pip install -U setuptools
```

Test nhanh:

```bash
curl -s http://localhost:8000/health | jq
curl -s "http://localhost:8000/v1/echo?msg=hi" | jq
curl -s -X POST http://localhost:8000/v1/items -H 'Content-Type: application/json' -d '{"name":"book"}' | jq
curl -s http://localhost:8000/metrics | head
```

## Prometheus (tuỳ chọn)

Chạy Prometheus để scrape `/metrics` (Linux):

```bash
docker compose down
docker compose up -d
open http://localhost:9090
```

Vào `http://localhost:9090/targets` để kiểm tra target `flask_api` đang **UP**.

Query thử trong tab **Graph**:
- `http_requests_total`
- `rate(http_requests_total[1m])`
- `histogram_quantile(0.95, sum by (le, path) (rate(http_request_duration_seconds_bucket[5m])))`

Nếu bạn chạy Flask không phải trên `localhost:8000`, hãy sửa `targets` trong `prometheus.yml`.

## Grafana (tuỳ chọn)

Chạy Grafana (đã provision sẵn datasource Prometheus + dashboard):

```bash
docker compose up -d
open http://localhost:3000
```

Đăng nhập:
- user: `admin`
- pass: `admin`

Mở dashboard **Flask API Observability** để xem:
- Request rate theo `path`
- P95 latency theo `path`
- 5xx rate

Ghi chú: `docker-compose.yml` đang dùng `network_mode: host` (phù hợp Linux). Nếu bạn dùng Docker Desktop (macOS/Windows), cách này có thể không hoạt động; khi đó hãy chuyển về bridge network và dùng `host.docker.internal`/gateway IP.

## Production (gợi ý)

Chạy bằng Gunicorn:

```bash
gunicorn -c gunicorn.conf.py "app:create_app()"
```

Rate limit storage production nên dùng Redis:
- `RATE_LIMIT_STORAGE_URI=redis://localhost:6379/0`

Tracing export sang OTLP collector:
- `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318`

## Bảo mật/quan sát trong production (tóm tắt)

- **WAF**: thường đặt ngoài app (Nginx+ModSecurity, Cloudflare/AWS WAF). App chỉ nên tin `X-Forwarded-For` khi đứng sau proxy tin cậy.
- **Rate limiting**: nên enforce ở edge (WAF/ingress) + trong app (Flask-Limiter) để defense-in-depth.
- **Audit logs**: demo đã log event `http_request` (method/path/status/ip/ua/latency/request_id). Production nên ship logs sang ELK/Loki/Splunk.
- **Metrics & tracing**: scrape `/metrics` bởi Prometheus; tracing gửi OTLP tới collector (Tempo/Jaeger/OTel Collector).
