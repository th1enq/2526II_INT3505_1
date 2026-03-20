# API Blueprint Format

- API Blueprint không có thư viện chính thức nào để tự động generate spec từ Flask app.
- Cách duy nhất là viết file `.apib` thủ công dựa trên code Flask, sau đó dùng công cụ như `aglio` để tạo tài liệu HTML.
- Hoặc generate OpenAPI spec từ Flask app (như trong 0_OpenAPI), sau đó convert sang API Blueprint bằng công cụ online như https://mermade.org.uk/api-spec-converter/ (không hoàn hảo, có thể cần chỉnh sửa thủ công).