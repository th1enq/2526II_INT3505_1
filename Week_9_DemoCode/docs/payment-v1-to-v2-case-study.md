# Case Study: Nâng cấp API Thanh toán từ v1 sang v2

## Bối cảnh
V1 chỉ hỗ trợ payload tối giản (`amount`, `currency`) và trả trạng thái `created`.
Khi mở rộng hệ thống chống gian lận + xác thực khách hàng, v2 cần:
- Trường bắt buộc `customer_id`
- Trạng thái phân tách rõ ràng (`authorized` trước khi `capture`)
- Hypermedia links để client biết bước tiếp theo

## Thiết kế v1 (legacy)
`POST /api/v1/payments`

Request:
```json
{
  "amount": 100,
  "currency": "USD"
}
```

Response (201):
```json
{
  "version": "v1",
  "payment_id": "pay_legacy_001",
  "amount": 100,
  "currency": "USD",
  "status": "created"
}
```

## Thiết kế v2 (target)
`POST /api/v2/payments`

Request:
```json
{
  "amount": 100,
  "currency": "USD",
  "customer_id": "cus_123"
}
```

Response (201):
```json
{
  "version": "v2",
  "id": "pay_2026_001",
  "amount": 100,
  "currency": "USD",
  "customer_id": "cus_123",
  "status": "authorized",
  "links": {
    "self": "/api/v2/payments/pay_2026_001",
    "capture": "/api/v2/payments/pay_2026_001/capture"
  }
}
```

## Rủi ro & giảm thiểu
- **Rủi ro:** Client cũ thiếu `customer_id` -> lỗi 400.
- **Giảm thiểu:** Cho phép chạy song song v1/v2 trong 6 tháng + gửi warning header tự động.

- **Rủi ro:** Client parse `payment_id` nhưng v2 đổi thành `id`.
- **Giảm thiểu:** Cung cấp bảng mapping field và contract test mẫu.

## KPI migration
- < 10% traffic còn ở v1 sau 3 tháng.
- 0 incident P1 liên quan migration trong tháng sunset.
- 100% team thanh toán hoàn thành checklist trước T0 + 5 tháng.
