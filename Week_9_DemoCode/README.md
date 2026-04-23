# Flask API Versioning Demo

Demo web server bằng Flask để minh họa:
- API versioning theo **URL**, **header**, **query param**
- Cách xử lý **breaking changes**, **deprecation**, **sunset**
- Kế hoạch migration từ v1 sang v2
- Case study nâng cấp API thanh toán

## 1) Cài đặt
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2) Chạy server
```bash
python app.py
```
Server chạy mặc định tại `http://127.0.0.1:5000`.

## 3) Demo API versioning
### URL versioning
```bash
curl -i http://127.0.0.1:5000/api/v1/users
curl -i http://127.0.0.1:5000/api/v2/users
```

### Header versioning
```bash
curl -i -H 'X-API-Version: v2' http://127.0.0.1:5000/api/users
curl -i -H 'Accept: application/vnd.demo.v2+json' http://127.0.0.1:5000/api/users
```

### Query param versioning
```bash
curl -i 'http://127.0.0.1:5000/api/users?version=2'
```

### Payment v1/v2
```bash
curl -i -X POST http://127.0.0.1:5000/api/v1/payments \
  -H 'Content-Type: application/json' \
  -d '{"amount":100,"currency":"USD"}'

curl -i -X POST http://127.0.0.1:5000/api/v2/payments \
  -H 'Content-Type: application/json' \
  -d '{"amount":100,"currency":"USD","customer_id":"cus_123"}'
```

## 4) Chạy test
```bash
pytest -q
```

## 5) Generate OpenAPI tự động từ code
### Xem spec runtime
```bash
curl -s http://127.0.0.1:5000/openapi.json | python -m json.tool
```

### Swagger UI
Mở trình duyệt tại `http://127.0.0.1:5000/docs`.

### Xuất spec ra file
```bash
python scripts/generate_openapi.py
```
File được tạo tại `docs/openapi.json`.

## 6) Tài liệu
- Migration plan: `docs/migration-plan.md`
- Case study payment: `docs/payment-v1-to-v2-case-study.md`
- Deprecation notice: `docs/deprecation-notice.md`
- Testing guide: `docs/testing-guide.md`
- OpenAPI spec (generated): `docs/openapi.json`
