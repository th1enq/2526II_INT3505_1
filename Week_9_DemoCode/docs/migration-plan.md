# API Migration Plan: v1 -> v2

## 1) Mục tiêu
- Giảm rủi ro khi thay đổi **breaking changes**.
- Duy trì backward compatibility trong giai đoạn chuyển đổi.
- Cung cấp timeline rõ ràng cho client teams.

## 2) Phạm vi breaking changes
### Users API
- `name` (v1) -> `full_name` (v2)
- Bổ sung trường bắt buộc/quan trọng hơn: `email`, `status`

### Payments API
- Endpoint: `/api/v1/payments` -> `/api/v2/payments`
- `customer_id` trở thành trường bắt buộc trong v2.
- Trạng thái trả về chi tiết hơn (`authorized`, link hành động `capture`).

## 3) Chính sách versioning
- URL versioning: `/api/v1/...`, `/api/v2/...`
- Header versioning: `X-API-Version: v2` hoặc media type `Accept: application/vnd.demo.v2+json`
- Query param versioning: `?version=2`

## 4) Timeline đề xuất
- **T0 (2026-04-23):** Release v2 + công bố deprecation v1.
- **T0 + 1 tháng:** Dashboard/metrics theo dõi tỷ lệ client còn dùng v1.
- **T0 + 2 tháng:** Nhắc lần 2 và gửi checklist migration theo team.
- **T0 + 4 tháng:** Chặn tính năng mới trên v1, chỉ fix bug nghiêm trọng.
- **T0 + 5 tháng:** Chạy migration rehearsal / sandbox bắt buộc.
- **T0 + 6 tháng (2026-09-30):** Sunset v1.

## 5) Cơ chế deprecation runtime
Với mọi response từ v1, trả thêm headers:
- `Deprecation: true`
- `Sunset: Tue, 30 Sep 2026 00:00:00 GMT`
- `Warning: 299 - "API v1 is deprecated..."`
- `Link: </docs/migration-plan>; rel="deprecation"; type="text/markdown"`

## 6) Checklist cho client
1. Cập nhật SDK/client gọi version v2.
2. Mapping field `name -> full_name`.
3. Bổ sung `customer_id` khi gọi payment v2.
4. Cập nhật parser cho response payment mới (`id`, `links`, status mới).
5. Chạy regression test và contract test trước production.

## 7) Rollback strategy
- Duy trì v1 read/write trong giai đoạn grace period.
- Có feature flag để route lại v1 nếu lỗi nghiêm trọng ở v2.
- Theo dõi error rate 4xx/5xx theo version để quyết định rollback nhanh.
