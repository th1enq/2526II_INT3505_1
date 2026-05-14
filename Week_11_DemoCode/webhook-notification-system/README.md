# Webhook Notification System Demo

Hệ thống demo webhook với hai dịch vụ: **Dịch vụ thanh toán** (Payment Service) và **Dịch vụ thông báo** (Notification Service).

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
│  ├─ GET /api/notifications  → Get all notifications        │
│  ├─ GET /api/notifications/<id> → Get notification detail  │
│  └─ GET /health             → Service health check         │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Luồng hoạt động
1. **Khách hàng gửi thanh toán** → POST /api/pay
2. **Payment Service xử lý** → Lưu dữ liệu thanh toán
3. **Gửi webhook event** → POST /webhook/payment (Notification Service)
4. **Notification Service nhận** → Xử lý và gửi thông báo (Email/SMS/Push)
5. **Khách hàng nhận thông báo**

## 🚀 Cách sử dụng

### 1. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 2. Chạy Notification Service (Terminal 1)
```bash
python notification_service.py
```
Output:
```
🚀 Notification Service starting on port 5001...
⏳ Waiting for webhook events from payment service...
```

### 3. Chạy Payment Service (Terminal 2)
```bash
python payment_service.py
```
Output:
```
🚀 Payment Service starting on port 5000...
📍 Webhook will be sent to: http://localhost:5001/webhook/payment
```

### 4. Chạy test script (Terminal 3)
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

#### 2. Lấy danh sách thông báo
```bash
GET /api/notifications
```

#### 3. Lấy chi tiết thông báo
```bash
GET /api/notifications/{notification_id}
```

#### 4. Kiểm tra trạng thái
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
- Sự kiện: `payment.success`

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
