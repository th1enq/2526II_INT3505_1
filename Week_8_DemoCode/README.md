# Flask Demo App with Automated Testing Pipeline

Project mẫu Flask đơn giản, tích hợp:

- Unit test bằng `pytest`
- API regression test bằng `newman` (Postman collection)
- Performance test bằng `k6`
- CI/CD bằng GitHub Actions để tự động chạy test trước khi deploy

## 1) Cấu trúc project

```text
.
├── app/
│   ├── __init__.py
│   └── routes.py
├── tests/
│   ├── conftest.py
│   └── test_app.py
├── performance/
│   └── k6-smoke.js
├── postman/
│   ├── flask-demo.postman_collection.json
│   └── local.postman_environment.json
├── .github/workflows/
│   └── ci-cd.yml
├── run.py
├── requirements.txt
├── package.json
└── README.md
```

## 2) Chạy local

### Cài Python dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Chạy Flask app

```bash
python run.py
```

App chạy tại: `http://localhost:5000`

### Unit test (pytest)

```bash
pytest -q
```

### API test (Newman)

Mở terminal mới, cài node dependencies và chạy:

```bash
npm install
npm run test:api
```

### Performance test (k6)

```bash
k6 run performance/k6-smoke.js
```

Nếu chưa cài `k6`, có thể chạy bằng Docker:

```bash
docker run --rm --network host -e BASE_URL=http://127.0.0.1:5000 -v "$PWD/performance:/scripts" grafana/k6 run /scripts/k6-smoke.js
```

Nếu app chạy ở URL khác:

```bash
BASE_URL=http://127.0.0.1:5000 k6 run performance/k6-smoke.js
```

## 3) API nhanh

- `GET /health`
- `POST /api/echo` với body JSON:

```json
{
  "message": "hello"
}
```

## 4) CI/CD

Workflow: `.github/workflows/ci-cd.yml`

Pipeline gồm 4 job:

1. `unit-tests`: chạy `pytest`
2. `api-tests-newman`: chạy Postman/Newman
3. `performance-tests-k6`: chạy `k6`
4. `deploy`: chỉ chạy khi tất cả test pass trên branch `main`

Bạn thay nội dung job `deploy` bằng lệnh deploy thực tế (Docker, VM, Kubernetes, v.v.).

## 5) Setup để push/deploy lên GitHub là tự chạy kiểm thử

### Bước 1: Push project lên GitHub

```bash
git init
git add .
git commit -m "init flask app with tests and ci-cd"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

Sau khi push, vào tab **Actions** của repo để thấy workflow `CI-CD Flask Demo` tự chạy.

### Bước 2: Bật rule bắt buộc phải pass test mới merge/deploy

Vào: `Settings` → `Branches` → `Add branch protection rule`

- Branch name pattern: `main`
- Bật `Require a pull request before merging`
- Bật `Require status checks to pass before merging`
- Chọn các checks:
  - `unit-tests`
  - `api-tests-newman`
  - `performance-tests-k6`

Khi đó, PR chỉ được merge nếu tất cả kiểm thử đều pass.

### Bước 3: Cấu hình deploy thật trong workflow

Trong file `.github/workflows/ci-cd.yml`, sửa job `deploy`:

- Thay lệnh placeholder bằng lệnh deploy thực tế.
- Nếu cần secrets (token, SSH key, cloud credentials), thêm tại:
  `Settings` → `Secrets and variables` → `Actions`.

Luồng chuẩn: Push/PR → test tự chạy → pass hết mới cho merge/deploy.
