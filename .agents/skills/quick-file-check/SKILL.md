---
name: quick-file-check
description: Sử dụng kỹ năng này để nhanh chóng hiển thị danh sách các tệp PDF đầu vào mới nhất trong thư mục `data/pdf/PDF/` khi người dùng hỏi các câu hỏi như "hiện tại tôi có những file nào", "hiển thị các file theo cập nhật mới nhất", "danh sách file",... Kỹ năng này đảm bảo hiển thị đúng tệp và đúng định dạng mà không cần AI tự suy luận phức tạp.
compatibility: Windows OS, Python 3.x với venv.
---

# Kỹ năng Quick File Check

Kỹ năng này cung cấp một kịch bản tự động để liệt kê tất cả các tệp PDF hiện có trong thư mục đầu vào `data/pdf/PDF/` theo thứ tự thời gian cập nhật mới nhất.

## Hướng dẫn sử dụng

Kích hoạt kỹ năng này khi người dùng yêu cầu:
- Kiểm tra danh sách file hiện có.
- Xem danh sách tệp PDF đầu vào.
- Hiển thị danh sách file theo cập nhật mới nhất.

## Các bước thực hiện

- [ ] **Bước 1: Chạy kịch bản liệt kê tệp**
  - Chạy lệnh sau để nhận danh sách tệp chính xác và định dạng URL chuẩn:
    ```bash
    venv/Scripts/python.exe .agents/skills/quick-file-check/scripts/list_files.py
    ```
- [ ] **Bước 2: Phản hồi trực tiếp cho người dùng**
  - In trực tiếp kết quả đầu ra của lệnh trên mà không cần tự suy luận danh sách tệp hoặc thay đổi định dạng mẫu.
