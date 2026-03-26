# Week 5 Demo - Library Data Model + Pagination (Flask)

This demo supports a lecture on:

- Resource tree design for a domain (`/users/{id}/loans`)
- Pagination strategies: `offset/limit`, `page-based`, and `cursor`
- Search endpoints with pagination for a library management system

## Project Structure (production-style)

```text
Week_5_DemoCode/
├── app.py
├── app/
│   ├── __init__.py            # App factory
│   ├── config.py              # App config
│   ├── extensions.py          # Swagger extension
│   ├── api/
│   │   ├── health.py          # /health
│   │   ├── users.py           # /users/{id}/loans
│   │   └── books.py           # /books* endpoints
│   ├── services/
│   │   └── library_service.py # Business logic
│   ├── repositories/
│   │   └── library_repository.py # Data access (in-memory)
│   └── utils/
│       └── pagination.py      # parse int, cursor encode/decode
├── requirements.txt
└── README.md
```

## 1) Setup

```bash
cd Week_5_DemoCode
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open:

- API base: `http://127.0.0.1:5000`
- Swagger UI: `http://127.0.0.1:5000/apidocs`

## 2) Data Model (in-memory)

- `User(id, name)`
- `Book(id, title, author, category)`
- `Loan(id, user_id, book_id, loan_date, due_date, status)`

Relationship examples:

- One user has many loans
- One book can appear in many loans over time

## 3) Endpoints

- `GET /health`
- `GET /users/{id}/loans?status=active&offset=0&limit=10`
- `GET /books?q=python&offset=0&limit=10` (offset/limit)
- `GET /books/page?q=python&page=1&size=10` (page-based)
- `GET /books/cursor?q=python&limit=10&cursor=<token>` (cursor)

## 4) Pagination Comparison

### Offset/Limit

Pros:

- Easy to implement and understand
- Easy random jump with offset math

Cons:

- Slow on very large offsets in many databases
- Can skip/duplicate rows when data changes rapidly

### Page-based

Pros:

- User-friendly (`page=2`, `size=20`)
- Good for UI tables with page numbers

Cons:

- Same deep-page performance issue as offset/limit
- Data drift between pages if records are inserted/deleted

### Cursor

Pros:

- Stable for continuously changing data
- Fast for next-page traversal on large datasets

Cons:

- Harder to jump to arbitrary page
- Cursor encoding/decoding adds complexity

## 5) Suggested Exercises

- Add `POST /users/{id}/loans` for borrowing flow
- Persist data in SQLite instead of in-memory lists
- Add validation and standardized error schema
