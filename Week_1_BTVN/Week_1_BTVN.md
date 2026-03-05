# Tuần 1: Giới thiệu về API và Web Services

**Bài tập về nhà**: Tìm và phân tích 3 API công khai (GitHub, OpenWeather, v.v.)

# 1. Github REST API

## Mục đích

GitHub API cho phép truy cập dữ liệu GitHub như:

- Repository
- User
- Commit
- Pull request
- Issue
- Webhook

Được dùng để xây dựng:

- CI/CD tools
- Git analytics
- Automation bot

---

## Ví dụ endpoint

### Lấy thông tin repository

```
GET https://api.github.com/repos/{owner}/{repo}
```

Ví dụ:

```
GET https://api.github.com/repos/golang/go
```

---

## Ví dụ Response

```
{
  "id":23096959,
  "name":"go",
  "full_name":"golang/go",
  "private":false,
  "stargazers_count":120000,
  "forks_count":17000,
  "language":"Go"
}
```

---

## Authentication

GitHub hỗ trợ:

1. Personal Access Token

```
Authorization: Bearer <token>
```

1. OAuth App
2.  GitHub App (JWT)

---

## Rate Limit

| Type | Limit |
| --- | --- |
| Unauthenticated | 60 requests/hour |
| Authenticated | 5000 requests/hour |

API trả header:

```
X-RateLimit-Limit
X-RateLimit-Remaining
```

# 2. OpenWeather API

Cung cấp dữ liệu:

- Weather hiện tại
- Forecast
- Air pollution
- Historical weather

Ứng dụng:

- Mobile weather app
- Smart home
- Agriculture

---

## Ví dụ endpoint

### Current Weather

```
GET https://api.openweathermap.org/data/2.5/weather
```

Query parameters

```
?q=Hanoi
&appid=API_KEY
&units=metric
```

---

## Ví dụ Request

```
GET https://api.openweathermap.org/data/2.5/weather?q=Hanoi&appid=KEY
```

---

## Response

```
{
  "weather": [
    {
      "main":"Clouds",
      "description":"overcast clouds"
    }
  ],
  "main": {
    "temp":29.5,
    "humidity":80
  },
  "wind": {
    "speed":3.5
  },
  "name":"Hanoi"
}
```

---

## Authentication

Dùng **API Key**

```
appid=YOUR_API_KEY
```

---

## Rate Limit

Free plan:

```
60 calls/minute
1,000,000 calls/month
```

---

## REST Design

| REST Principle | Implementation |
| --- | --- |
| Resource | `/weather` |
| Query parameters | location |
| Stateless | mỗi request độc lập |
| Format | JSON |

---

# 3. Stripe API (Payment API)

**Website:** [https://stripe.com/docs/api](https://stripe.com/docs/api)

---

## Mục đích

Stripe API dùng để:

- Thanh toán online
- Subscription
- Billing
- Marketplace

Rất phổ biến trong SaaS.

---

## Ví dụ endpoint

### Create Payment Intent

```
POST https://api.stripe.com/v1/payment_intents
```

---

## Request

```
amount=2000
currency=usd
```

Header:

```
Authorization: Bearer SECRET_KEY
```

---

## Response

```
{
  "id":"pi_123456",
  "amount":2000,
  "currency":"usd",
  "status":"requires_payment_method"
}
```

---

## Authentication

Stripe dùng **API Secret Key**

```
Authorization: Bearer sk_test_xxx
```

---

## Rate Limit

Stripe không công bố cụ thể nhưng có:

```
~100 requests/sec
```

và có **idempotency key** để tránh double payment.

---

## REST Design

| Feature | Implementation |
| --- | --- |
| Resource | `/payment_intents` |
| HTTP methods | GET POST DELETE |
| Idempotency | Idempotency-Key |
| Webhook | payment events |