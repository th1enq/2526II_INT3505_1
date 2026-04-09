# Pagination Comparison (Flask + PostgreSQL)

Demo 3 chiến thuật pagination cho dữ liệu lớn:

1. `offset` (`/offset?offset=...&limit=...`)
2. `page-size` (`/page?page=...&size=...`)
3. `cursor` (`/cursor?cursor=...&limit=...`)

## 1) Cài đặt

```bash
cd /home/th1enq/Documents/2526II_INT3505_1/pagination_comparision
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## 2) Chạy PostgreSQL

```bash
docker compose up -d
```

## 3) Chạy API Flask

```bash
python app.py
```

API chạy tại `http://localhost:8000`

### Test nhanh các endpoint

```bash
curl "http://localhost:8000/health"
curl "http://localhost:8000/offset?offset=0&limit=5"
curl "http://localhost:8000/page?page=1&size=5"
curl "http://localhost:8000/cursor?limit=5"
```

## 4) Benchmark dữ liệu lớn

Mặc định script seed đến `1,000,000` rows rồi benchmark.

Demo nhanh (ít tốn thời gian hơn):

```bash
python benchmark.py --rows 200000 --page-size 50 --depths 10 100 1000 --runs 3
```

```bash
python benchmark.py --rows 1000000 --page-size 50 --depths 10 100 1000 5000 --runs 5
```

Kết quả JSON xuất ra: `docs/benchmark_results.json`.
Tổng hợp benchmark demo: `docs/BENCHMARK_SUMMARY.md`.

## 5) Ý nghĩa benchmark

- `offset`: truy vấn đơn lẻ đến trang sâu bằng `OFFSET`.
- `page-size`: thực chất là `OFFSET` dưới dạng `page` + `size`.
- `cursor`: không nhảy thẳng trang sâu, nhưng rất ổn định khi duyệt tuần tự.

Xem tổng hợp phân tích tại `docs/BENCHMARK_SUMMARY.md`.

## 6) Tự test nhược điểm OFFSET (data drift / lặp / thiếu)

Kịch bản: lấy page 1 bằng `offset`, sau đó chèn bản ghi mới, rồi lấy page 2 bằng `offset` cũ.
Khi dữ liệu mới được chèn lên đầu (sort `created_at DESC`), kết quả có thể bị **lặp** hoặc **thiếu** giữa các page.

Chạy các lệnh sau (API Flask phải đang chạy tại `localhost:8000`):

```bash
curl -s "http://localhost:8000/offset?offset=0&limit=5" > p1_before.json
```

```bash
curl -s -X POST "http://localhost:8000/insert" \
	-H "Content-Type: application/json" \
	-d '{"payload":"drift_test_new_row"}' > inserted.json
```

```bash
curl -s "http://localhost:8000/offset?offset=5&limit=5" > p2_after.json
```

```bash
curl -s "http://localhost:8000/offset?offset=0&limit=11" > top11_after.json
```

```bash
python - <<'PY'
import json

p1 = [x["id"] for x in json.load(open("p1_before.json"))["items"]]
p2 = [x["id"] for x in json.load(open("p2_after.json"))["items"]]
top11 = [x["id"] for x in json.load(open("top11_after.json"))["items"]]

observed = p1 + p2
expected_without_newest = top11[1:11]

dup_between_pages = sorted(set(p1) & set(p2))
missing = sorted(set(expected_without_newest) - set(observed))

print("page1_before:", p1)
print("page2_after :", p2)
print("duplicate_between_pages:", dup_between_pages)
print("missing_from_expected  :", missing)
PY
```

Diễn giải kết quả:

- `duplicate_between_pages` khác rỗng: có bản ghi bị lặp giữa 2 request.
- `missing_from_expected` khác rỗng: có bản ghi bị trôi/mất khỏi tập quan sát.
