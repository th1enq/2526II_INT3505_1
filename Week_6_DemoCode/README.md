# Week 6 Demo: Flask Authentication + Authorization

Demo này triển khai:
- Authentication bằng JWT
- Refresh token để cấp lại access token
- OAuth2 (`password grant`, `refresh_token grant`)
- Authorization theo `roles` và `scopes`
- Swagger UI để test API trực tiếp

## Kiến trúc Layer

- `app.py`: entrypoint, chỉ khởi tạo và chạy app
- `core/__init__.py`: application factory, wiring các dependency
- `core/api/*`: presentation layer (REST endpoints)
- `core/services/*`: business logic layer
- `core/repositories/*`: data access layer (in-memory cho demo)
- `core/auth/decorators.py`: authorization decorators theo role/scope
- `core/config.py`, `core/extensions.py`: cấu hình và extension

## 1. Cài đặt

```bash
cd Week_6_DemoCode
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Chạy ứng dụng

```bash
python app.py
```

Server chạy tại: `http://localhost:5000`

Swagger UI: `http://localhost:5000/swagger`

## 3. Tài khoản demo

- `alice / alice123`
  - roles: `user`
  - scopes: `profile:read`, `books:read`
- `bob / bob123`
  - roles: `user`, `librarian`
  - scopes: `profile:read`, `books:read`, `books:write`
- `admin / admin123`
  - roles: `admin`
  - scopes: `profile:read`, `books:read`, `books:write`, `admin:read`

OAuth2 demo client:
- `client_id`: `demo-client`
- `client_secret`: `demo-secret`

## 4. Quy trình test trên Swagger

1. Gọi `POST /auth/login` với username/password để lấy `access_token` và `refresh_token`.
2. Nhấn nút **Authorize** trên Swagger UI.
3. Dán token theo format:
   - `Bearer <access_token>` khi gọi endpoint cần access token.
   - `Bearer <refresh_token>` khi gọi `POST /auth/refresh`.
4. Test các endpoint:
  - `GET /api/me` cần scope `profile:read`
  - `GET /api/books` cần scope `books:read`
  - `POST /api/books` cần scope `books:write` + role `librarian` hoặc `admin`
  - `GET /api/admin/reports` cần role `admin` + scope `admin:read`

## 5. Quy trình test OAuth2

1. Gọi `POST /oauth/token` với form-data:
   - Password grant:
     - `grant_type=password`
     - `client_id=demo-client`
     - `client_secret=demo-secret`
     - `username=bob`
     - `password=bob123`
     - `scope=books:read books:write profile:read` (tuỳ chọn)
2. Lấy `access_token` và `refresh_token` từ response OAuth2.
3. Dùng `Bearer <access_token>` để gọi endpoint protected (`/api/*`).
4. Khi cần cấp lại access token, gọi `POST /oauth/token` với:
   - `grant_type=refresh_token`
   - `client_id=demo-client`
   - `client_secret=demo-secret`
   - `refresh_token=<refresh_token>`

## 6. Danh sách endpoint

- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`
- `POST /oauth/token`
- `GET /api/me`
- `GET /api/books`
- `POST /api/books`
- `GET /api/admin/reports`

## 7. Ghi chú

- Demo dùng in-memory data (user, books, revoked tokens), phù hợp mục đích học tập.
- Trong production cần:
  - Mã hóa password (bcrypt/argon2)
  - Lưu revoked tokens vào Redis/DB
  - Quản lý secret key qua biến môi trường
  - Dùng HTTPS và cấu hình CORS phù hợp
