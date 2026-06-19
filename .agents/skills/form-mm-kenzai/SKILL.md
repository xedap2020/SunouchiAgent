---
name: form-mm-kenzai
description: Sử dụng kỹ năng này để trích xuất dữ liệu có cấu trúc từ tệp PDF hóa đơn MM Kenzai (invoice3) cho Sunouchi IT. Kích hoạt kỹ năng này khi người dùng yêu cầu xử lý/trích xuất/phân loại hóa đơn MM Kenzai, hoặc khi tài liệu được phân loại là invoice3 / MM Kenzai.
compatibility: Windows OS, Python 3.x với venv, cơ sở dữ liệu MySQL cục bộ.
---

# Sunouchi IT - Bộ trích xuất hóa đơn MM Kenzai

Kỹ năng này cung cấp các quy tắc, schema và hướng dẫn để trích xuất dữ liệu có cấu trúc từ hóa đơn MM Kenzai (invoice3).

## Các tài liệu tham khảo có sẵn
- **`references/extraction_rules.md`** — Chứa schema JSON mục tiêu và các quy tắc trích xuất/chuẩn hóa chi tiết cho hóa đơn MM Kenzai.

## Danh sách kiểm tra quy trình
- [ ] **Bước 1: Lấy các quy tắc**
  - Đọc schema trích xuất và các hướng dẫn từ [references/extraction_rules.md](references/extraction_rules.md).
- [ ] **Bước 2: Thực hiện trích xuất**
  - Trích xuất văn bản và dữ liệu từ tệp PDF hóa đơn MM Kenzai.
  - Định dạng đầu ra khớp với cấu trúc JSON và áp dụng các quy tắc chính xác được xác định trong tệp tham khảo.
  - **QUAN TRỌNG**: Mã `customer_code` sẽ được hệ thống tự động đối chiếu dựa trên tên tệp.

## Lưu ý & Trường hợp biên
- **Tên tệp quyết định `customer_code`**: Mã `customer_code` sẽ được tự động đối chiếu và gán chính xác từ tên tệp PDF thông qua cơ chế của script `db_helper.py` dựa trên tệp cấu hình `.agents/skills/sunouchi-it/customer_mapping.json`. Agent không cần tự điền mã này từ danh sách từ khóa trong Prompt, hệ thống sẽ tự động xử lý ở bước đối chiếu DB (Resolve DB).
