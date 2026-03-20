- TypeSpec không generate api spec từ code mà code được generate từ api spec (design-first).

# Hướng dẫn sử dụng TypeSpec:
- Cài đặt TypeSpec: `npm install -g @typespec/http @typespec/openapi3`
- Viết file `main.tsp` theo cú pháp TypeSpec
- Run `typespec compile main.tsp --emit openapi3 --output openapi.json` để tạo OpenAPI spec
- Sau đó có thể dùng OpenAPI spec này để tạo tài liệu hoặc code stub cho server