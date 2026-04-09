# Benchmark Summary: Offset vs Page-size vs Cursor

## Mục tiêu

So sánh hiệu năng 3 chiến thuật pagination khi dữ liệu lớn trên PostgreSQL:

- `offset`
- `page-size`
- `cursor`

## Môi trường benchmark

- Stack: `Flask + psycopg + PostgreSQL`
- Bảng: `items(id BIGSERIAL, created_at TIMESTAMPTZ, payload TEXT)`
- Index: `(created_at DESC, id DESC)`
- Script: `benchmark.py`

## Kịch bản đo

1. **Deep jump** (đến trang sâu):
   - `offset`
   - `page-size`
2. **Sequential scan to depth** (duyệt tuần tự đến độ sâu):
   - `cursor`

## Cách chạy

```bash
python benchmark.py --rows 1000000 --page-size 50 --depths 10 100 1000 5000 --runs 5
```

Kết quả nằm ở `docs/benchmark_results.json`.

## Kỳ vọng xu hướng

- `offset` và `page-size` tăng độ trễ khi `depth` lớn do cần bỏ qua nhiều dòng hơn.
- `cursor` ổn định cho từng bước kế tiếp, phù hợp infinite scroll/feed.
- `cursor` không phù hợp cho "nhảy trực tiếp" tới trang số rất lớn.

## Kết luận khuyến nghị

- Dùng `offset`/`page-size` cho UI cần truy cập trang số trực tiếp.
- Dùng `cursor` cho dữ liệu lớn + luồng đọc tuần tự, cần độ trễ ổn định.
- Nếu khối lượng dữ liệu tăng nhanh, ưu tiên `cursor` cho API public/tải cao.

## Kết quả benchmark thực tế (demo run)

Lệnh đã chạy:

```bash
python benchmark.py --rows 200000 --page-size 50 --depths 10 100 1000 --runs 3
```

Tệp kết quả: `docs/benchmark_results.json`.

| Strategy | Scenario | Depth | Avg (ms) | P95 (ms) |
|---|---|---:|---:|---:|
| offset | deep_jump | 10 | 0.646 | 1.570 |
| page-size | deep_jump | 10 | 0.482 | 0.781 |
| cursor | sequential_scan_to_depth | 10 | 4.354 | 5.407 |
| offset | deep_jump | 100 | 0.784 | 0.972 |
| page-size | deep_jump | 100 | 0.758 | 0.768 |
| cursor | sequential_scan_to_depth | 100 | 28.705 | 30.271 |
| offset | deep_jump | 1000 | 4.557 | 4.857 |
| page-size | deep_jump | 1000 | 4.632 | 4.921 |
| cursor | sequential_scan_to_depth | 1000 | 239.858 | 253.855 |

## Phân tích nhanh

- `offset` và `page-size` gần như tương đương vì cùng cơ chế `OFFSET/LIMIT`.
- Khi depth tăng từ `10 -> 1000`, độ trễ `offset/page-size` tăng rõ rệt (từ ~`0.5-0.8ms` lên ~`4.5-4.6ms`).
- `cursor` không nhảy trực tiếp tới trang sâu; thời gian tăng gần tuyến tính theo số bước duyệt tuần tự.
- Với luồng infinite scroll/next page liên tục, cursor vẫn có lợi vì mỗi query đơn lẻ ổn định và tận dụng index tốt.

## Kịch bản tái hiện nhược điểm OFFSET (data drift)

Mục tiêu: chứng minh `OFFSET/LIMIT` có thể gây lặp hoặc mất bản ghi nếu có insert mới giữa các request.

Điều kiện: API Flask đang chạy tại `http://localhost:8000`.

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

Kết luận khi đọc output:

- `duplicate_between_pages` khác rỗng: xuất hiện bản ghi trùng giữa page 1 và page 2.
- `missing_from_expected` khác rỗng: có bản ghi bị trôi khỏi tập kết quả kỳ vọng.

## Mẫu bảng tổng hợp kết quả

| Strategy | Scenario | Depth | Avg (ms) | P95 (ms) |
|---|---|---:|---:|---:|
| offset | deep_jump | 10 | ... | ... |
| page-size | deep_jump | 10 | ... | ... |
| cursor | sequential_scan_to_depth | 10 | ... | ... |
| offset | deep_jump | 1000 | ... | ... |
| page-size | deep_jump | 1000 | ... | ... |
| cursor | sequential_scan_to_depth | 1000 | ... | ... |

> Sau khi chạy benchmark thực tế, điền số từ `docs/benchmark_results.json` vào bảng trên.
