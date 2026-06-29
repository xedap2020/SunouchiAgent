---
name: form-kadopita-negotiation
description: Sử dụng kỹ năng này để trích xuất dữ liệu có cấu trúc từ tệp PDF hóa đơn Kadopita Negotiation (invoice9) cho Sunouchi IT. Kích hoạt kỹ năng này khi người dùng yêu cầu xử lý/trích xuất/phân loại hóa đơn Kadopita Negotiation, hoặc khi tài liệu được phân loại là invoice9 / Kadopita Negotiation.
compatibility: Windows OS, Python 3.x với venv, cơ sở dữ liệu MySQL cục bộ.
---

# Sunouchi IT - Bộ trích xuất hóa đơn Kadopita Negotiation

Kỹ năng này cung cấp các quy tắc, schema và hướng dẫn để trích xuất dữ liệu có cấu trúc từ hóa đơn Kadopita Negotiation (invoice9).

## Các tài liệu tham khảo có sẵn
- **`references/extraction_rules.md`** — Chứa schema JSON mục tiêu và các quy tắc trích xuất/chuẩn hóa chi tiết cho hóa đơn Kadopita Negotiation.

## Danh sách kiểm tra quy trình
- [ ] **Bước 1: Lấy các quy tắc**
  - Đọc schema trích xuất và các hướng dẫn từ [references/extraction_rules.md](references/extraction_rules.md).
- [ ] **Bước 2: Thực hiện trích xuất**
  - Trích xuất văn bản và dữ liệu từ tệp PDF hóa đơn Kadopita Negotiation.
  - Định dạng đầu ra khớp với cấu trúc JSON và áp dụng các quy tắc chính xác được xác định trong tệp tham khảo.
  - **QUAN TRỌNG**: Kiểm tra tên tệp so với bảng ánh xạ bên dưới để giải quyết `customer_code`.

## Lưu ý & Trường hợp biên
- **Tên tệp quyết định `customer_code`**: Trước khi trích xuất dữ liệu, bạn **BẮT BUỘC** phải kiểm tra tên tệp PDF và đối chiếu để gán mã `customer_code` phù hợp theo bảng quy tắc tập trung tại [AGENTS.md](file:///e:/SunouchiAgent/.agents/AGENTS.md). **KHÔNG** tự ý ghi đè bằng logic khác.

