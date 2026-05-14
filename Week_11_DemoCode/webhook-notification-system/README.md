# Webhook Notification System Demo

Hệ thống demo webhook với hai dịch vụ: **Dịch vụ thanh toán** (Payment Service) và **Dịch vụ thông báo** (Notification Service). Notification Service dùng Redis làm message queue để gửi email đăng ký thành công theo luồng bất đồng bộ.

## 📋 Mô tả hệ thống

### Kiến trúc
```
┌─────────────────────────────────────────────────────────────┐
│                                                               │
│  Payment Service (Port 5000)                                │
│  ├─ POST /api/pay          → Process payment               │
│  ├─ GET /api/payments      → Get all payments              │
│  ├─ GET /api/payments/<id> → Get payment detail            │
│  └─ GET /health            → Service health check          │
│                     │                                        │
│                     │ (Webhook POST)                         │
│                     ↓                                        │
│  Notification Service (Port 5001)                          │
│  ├─ POST /webhook/payment    → Receive payment webhook     │
│  ├─ POST /webhook/customer   → Queue registration email    │
│  ├─ GET /api/notifications  → Get all notifications        │
│  ├─ GET /api/email-jobs     → Get queued email jobs        │
│  ├─ GET /api/notifications/<id> → Get notification detail  │
│  └─ GET /health             → Service health check         │
│                     │                                        │
│                     │ (Redis queue)                          │
│                     ↓                                        │
│  Email Worker → Send registration success email             │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Luồng hoạt động
1. **Khách hàng gửi thanh toán** → POST /api/pay
2. **Payment Service xử lý** → Lưu dữ liệu thanh toán
3. **Gửi webhook event** → POST /webhook/payment (Notification Service)
4. **Notification Service nhận** → Xử lý và gửi thông báo (Email/SMS/Push)
5. **Khách hàng nhận thông báo**

### Luồng email đăng ký bất đồng bộ
1. **Customer Service/User Service gửi webhook** → POST /webhook/customer
2. **Notification Service nhận `customer.registered`** → Đẩy email job vào Redis queue
3. **Email Worker lấy job từ Redis** → Gửi email chào mừng
4. Nếu payload không có `customer_email`/`email`, email mặc định là `thienchy3305@gmail.com`

## 🚀 Cách sử dụng

### 1. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 2. Chạy Redis
```bash
docker run --rm -p 6379:6379 redis:7-alpine
```

Hoặc dùng Redis đang chạy sẵn và cấu hình:
```bash
export REDIS_URL=redis://localhost:6379/0
export DEFAULT_CUSTOMER_EMAIL=thienchy3305@gmail.com
```

### 3. Chạy Notification Service (Terminal 1)
```bash
python notification_service.py
```
Output:
```
🚀 Notification Service starting on port 5001...
⏳ Waiting for webhook events from payment service...
🔌 Redis URL: redis://localhost:6379/0
📮 Email worker listening on Redis queue: notification:email_queue
```

### 4. Chạy Payment Service (Terminal 2)
```bash
python payment_service.py
```
Output:
```
🚀 Payment Service starting on port 5000...
📍 Webhook will be sent to: http://localhost:5001/webhook/payment
```

### 5. Chạy test script (Terminal 3)
```bash
python test_webhook.py
```

## 📊 API Endpoints

### Payment Service (Port 5000)

#### 1. Xử lý thanh toán
```bash
curl -X POST http://localhost:8080/api/pay \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST001",
    "customer_name": "Nguyễn Văn A",
    "amount": 500000,
    "order_id": "ORD001"
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "Payment processed successfully",
  "payment_id": "PAY20240514120530",
  "data": {
    "payment_id": "PAY20240514120530",
    "customer_id": "CUST001",
    "customer_name": "Nguyễn Văn A",
    "amount": 500000,
    "order_id": "ORD001",
    "status": "success",
    "timestamp": "2024-05-14T12:05:30.123456",
    "method": "credit_card"
  }
}
```

#### 2. Lấy danh sách thanh toán
```bash
GET /api/payments
```

#### 3. Lấy chi tiết thanh toán
```bash
GET /api/payments/{payment_id}
```

#### 4. Kiểm tra trạng thái
```bash
GET /health
```

### Notification Service (Port 5001)

#### 1. Webhook nhận sự kiện thanh toán
```bash
POST /webhook/payment
Content-Type: application/json

{
  "event": "payment.success",
  "timestamp": "2024-05-14T12:05:30.123456",
  "data": {
    "payment_id": "PAY20240514120530",
    "customer_id": "CUST001",
    "customer_name": "Nguyễn Văn A",
    "amount": 500000,
    "order_id": "ORD001",
    "status": "success",
    "method": "credit_card"
  }
}
```

#### 2. Webhook nhận sự kiện khách hàng đăng ký thành công
```bash
POST /webhook/customer
Content-Type: application/json

{
  "event": "customer.registered",
  "data": {
    "customer_id": "CUST999",
    "customer_name": "Khách hàng mới"
  }
}
```

Nếu không truyền `customer_email` hoặc `email`, hệ thống sẽ gửi về email mặc định `thienchy3305@gmail.com`.

**Response:**
```json
{
  "status": "success",
  "message": "Registration email job queued",
  "job_id": "EMAIL20240514120530123456"
}
```

#### 3. Lấy danh sách thông báo
```bash
GET /api/notifications
```

#### 4. Lấy danh sách email job
```bash
GET /api/email-jobs
```

#### 5. Lấy chi tiết thông báo
```bash
GET /api/notifications/{notification_id}
```

#### 6. Kiểm tra trạng thái
```bash
GET /health
```

## 🧪 Ví dụ sử dụng với cURL

### Gửi thanh toán
```bash
curl -X POST http://localhost:5000/api/pay \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST001",
    "customer_name": "Nguyễn Văn A",
    "amount": 500000,
    "order_id": "ORD001"
  }'
```

### Lấy danh sách thanh toán
```bash
curl http://localhost:5000/api/payments
```

### Lấy danh sách thông báo
```bash
curl http://localhost:5001/api/notifications
```

### Queue email đăng ký thành công
```bash
curl -X POST http://localhost:5001/webhook/customer \
  -H "Content-Type: application/json" \
  -d '{
    "event": "customer.registered",
    "data": {
      "customer_id": "CUST999",
      "customer_name": "Khách hàng mới"
    }
  }'
```

### Lấy danh sách email job
```bash
curl http://localhost:5001/api/email-jobs
```

## 📁 Cấu trúc tệp

```
webhook-notification-system/
├── payment_service.py          # Dịch vụ thanh toán
├── notification_service.py     # Dịch vụ thông báo
├── test_webhook.py             # Script test
├── requirements.txt            # Dependencies
└── README.md                   # Hướng dẫn
```

## 🔑 Khái niệm chính

### Webhook
- Webhook là một cơ chế để một hệ thống tự động gửi dữ liệu tới hệ thống khác khi có sự kiện xảy ra
- Thay vì polling (liên tục kiểm tra), webhook là push-based (chủ động đẩy)

### Event-Driven Architecture
- Payment Service là **producer** (tạo sự kiện)
- Notification Service là **consumer** (tiêu thụ sự kiện)
- Redis queue là message broker cho luồng email bất đồng bộ
- Sự kiện: `payment.success`, `customer.registered`

### Ưu điểm
✅ Real-time notification - Thông báo ngay lập tức
✅ Decoupled services - Các dịch vụ độc lập
✅ Scalable - Dễ thêm các consumer mới
✅ Reliable - Có thể retry nếu thất bại

## 🔧 Tùy chỉnh

### Thay đổi port
Sửa trong file service:
```python
app.run(debug=True, port=5000)  # Payment Service
app.run(debug=True, port=5001)  # Notification Service
```

### Thêm sự kiện mới
Trong `notification_service.py`, thêm vào hàm `receive_payment_webhook()`:
```python
elif event_type == 'payment.failed':
    handle_payment_failure(event_data)
```

### Lưu database thật
Thay thế các `_db` dictionaries bằng MongoDB, PostgreSQL, MySQL, v.v.

## ⚠️ Ghi chú

- Demo sử dụng in-memory database (mất khi restart)
- Webhook sử dụng HTTP, nên không bảo mật (dùng HTTPS cho production)
- Không có xác thực/authorization (nên thêm API key hoặc JWT)
- Debug mode bật (tắt trong production)

## 🎯 Bài tập mở rộng

1. Thêm xác thực webhook bằng HMAC signature
2. Thêm retry logic nếu webhook thất bại
3. Thêm logging và monitoring
4. Thêm database thực (MongoDB/PostgreSQL)
5. Thêm xử lý lỗi thanh toán
6. Thêm dashboard web để xem lịch sử

---

**Created**: May 14, 2024
**Tech Stack**: Flask, Python, Webhook, Event-Driven Architecture
