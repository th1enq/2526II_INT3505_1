# Hướng Dẫn Test Tính Năng API Versioning & Deprecation

Tài liệu này giúp bạn test nhanh toàn bộ feature:
- Versioning theo **URL**, **header**, **query param**
- **Deprecation** headers và **sunset**
- **Breaking changes** từ v1 -> v2
- Case test cho API thanh toán
- OpenAPI + Swagger UI

## 1) Chuẩn bị môi trường

```bash
cd /home/th1enq/Documents/2526II_INT3505_1/Week_9_DemoCode
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Server mặc định: `http://127.0.0.1:5000`

## 2) Smoke test

```bash
curl -i http://127.0.0.1:5000/health
```

Kỳ vọng:
- Status code `200`
- Body có `status: ok`

## 3) Test versioning theo URL

### 3.1 V1 users (deprecated)
```bash
curl -i http://127.0.0.1:5000/api/v1/users
```

Kỳ vọng:
- Status `200`
- Body có `version: "v1"`
- User object có field `name`
- Header có:
  - `Deprecation: true`
  - `Sunset: Tue, 30 Sep 2026 00:00:00 GMT`
  - `Warning: 299 - "API v1 is deprecated..."`

### 3.2 V2 users
```bash
curl -i http://127.0.0.1:5000/api/v2/users
```

Kỳ vọng:
- Status `200`
- Body có `version: "v2"`
- User object có `full_name`, `email`, `status`
- Không còn field `name` (breaking change)

### 3.3 URL version không hỗ trợ
```bash
curl -i http://127.0.0.1:5000/api/v3/users
```

Kỳ vọng:
- Status `400`
- Body có `error: "Unsupported API version"`

## 4) Test versioning theo Header

### 4.1 Qua `X-API-Version`
```bash
curl -i -H 'X-API-Version: v2' http://127.0.0.1:5000/api/users
```

Kỳ vọng:
- Status `200`
- Body trả `version: "v2"`

### 4.2 Qua `Accept` media type
```bash
curl -i -H 'Accept: application/vnd.demo.v2+json' http://127.0.0.1:5000/api/users
```

Kỳ vọng:
- Status `200`
- Body trả `version: "v2"`

### 4.3 Header không hợp lệ
```bash
curl -i -H 'X-API-Version: abc' http://127.0.0.1:5000/api/users
```

Kỳ vọng:
- Vì app fallback default, response sẽ là `v1` (deprecated)

## 5) Test versioning theo Query Param

### 5.1 Query version = 2
```bash
curl -i 'http://127.0.0.1:5000/api/users?version=2'
```

Kỳ vọng:
- Status `200`
- Body trả `version: "v2"`

### 5.2 Query version không hợp lệ
```bash
curl -i 'http://127.0.0.1:5000/api/users?version=hello'
```

Kỳ vọng:
- Status `400`
- Body có `Unsupported API version`

## 6) Test deprecation + breaking changes (payment)

### 6.1 Payment v1 (deprecated nhưng còn chạy)
```bash
curl -i -X POST http://127.0.0.1:5000/api/v1/payments \
  -H 'Content-Type: application/json' \
  -d '{"amount":100,"currency":"USD"}'
```

Kỳ vọng:
- Status `201`
- Body có `version: "v1"`, `payment_id`
- Header có `Deprecation`, `Sunset`, `Warning`

### 6.2 Payment v2 thiếu field bắt buộc
```bash
curl -i -X POST http://127.0.0.1:5000/api/v2/payments \
  -H 'Content-Type: application/json' \
  -d '{"amount":100}'
```

Kỳ vọng:
- Status `400`
- Body có `fields` chứa `currency`, `customer_id`

### 6.3 Payment v2 hợp lệ
```bash
curl -i -X POST http://127.0.0.1:5000/api/v2/payments \
  -H 'Content-Type: application/json' \
  -d '{"amount":100,"currency":"USD","customer_id":"cus_123"}'
```

Kỳ vọng:
- Status `201`
- Body có `version: "v2"`, `id`, `links.capture`

## 7) Test OpenAPI & Swagger UI

### 7.1 Lấy OpenAPI JSON runtime
```bash
curl -s http://127.0.0.1:5000/openapi.json | python -m json.tool
```

Kỳ vọng:
- Có `openapi: "3.0.3"`
- Có path `/api/v{version}/users`, `/api/v2/payments`

### 7.2 Mở Swagger UI
Truy cập: `http://127.0.0.1:5000/docs`

Kỳ vọng:
- Swagger UI hiển thị đầy đủ endpoints
- Có thể thử request trực tiếp trên UI

## 8) Chạy test tự động (pytest)

```bash
cd /home/th1enq/Documents/2526II_INT3505_1/Week_9_DemoCode
source .venv/bin/activate
pytest -q
```

Kỳ vọng:
- Tất cả test pass

## 9) Checklist kiểm thử nhanh trước demo lớp

- [ ] `/health` trả `200`
- [ ] `/api/v1/users` có header deprecation
- [ ] `/api/v2/users` phản ánh breaking changes schema
- [ ] `/api/users` hoạt động với cả header/query versioning
- [ ] `/api/v1/payments` còn hoạt động nhưng có cảnh báo deprecation
- [ ] `/api/v2/payments` bắt buộc `customer_id`
- [ ] `/openapi.json` trả spec hợp lệ
- [ ] `/docs` mở được Swagger UI
