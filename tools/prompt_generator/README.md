# 🛠️ Bộ Công Cụ Hỗ Trợ Thiết Lập Form Mới (Prompt & Skill Tools)

Thư mục này chứa các công cụ hỗ trợ chuẩn bị dữ liệu hình ảnh, so khớp đơn hàng mẫu và tự động sinh prompt/quy tắc trích xuất dành cho các form hóa đơn mới.

---

## 📁 Cấu Trúc Thư Mục

```text
tools/prompt_generator/
├── onboard_prep.py        # Kịch bản tiền xử lý (ghép cặp PDF-ERP, xuất ảnh PDF, tạo file request)
├── prompt_generator.py    # Kịch bản tự động gọi API Gemini để sinh prompt (dùng khóa API ngoài)
├── config.py              # Cấu hình API Key và Model cho prompt_generator.py
├── requirements.txt       # Các thư viện phụ thuộc
├── README.md              # Tài liệu hướng dẫn này
└── output/                # Nơi lưu các tệp quy tắc sinh ra từ prompt_generator.py
```

---

## 🚀 Các Công Cụ Chi Tiết

### 1. Script Tiền Xử Lý Khớp Cặp & Convert Ảnh (`onboard_prep.py`)
Script này giúp tự động hóa quá trình chuẩn bị dữ liệu trước khi gửi cho Agent phân tích. **Script này không cần API Key.**

* **Cách thức hoạt động**:
  1. Quét thư mục `data/pdf/NewForm/` để tìm các tệp PDF và ảnh chụp ERP.
  2. Gom nhóm các tệp có tên khớp nhau hoặc chứa chung mã đơn hàng (`Jxxxxxx`).
  3. Chuyển đổi toàn bộ trang PDF thành ảnh JPG lưu vào thư mục tạm `data/temp_onboard/[Tên_Đơn]/`.
  4. Tạo tệp tổng hợp yêu cầu `data/temp_onboard/onboard_request.json`.
* **Cách thực thi**:
  ```bash
  venv/Scripts/python.exe tools/prompt_generator/onboard_prep.py
  ```

---

### 2. Script Tự Động Sinh Quy Tắc Qua API (`prompt_generator.py`)
Script độc lập dành cho lập trình viên muốn sinh nhanh tệp quy tắc và hệ thống prompt mẫu thông qua API Key Gemini của cá nhân.

* **Cách thực thi**:
  * Chạy cho toàn bộ các cặp mẫu trong thư mục:
    ```bash
    venv/Scripts/python.exe tools/prompt_generator/prompt_generator.py
    ```
  * Chạy riêng cho một mã đơn hàng chỉ định:
    ```bash
    venv/Scripts/python.exe tools/prompt_generator/prompt_generator.py --sample_code J167465
    ```
  * Kết quả xuất ra tại: `tools/prompt_generator/output/extraction_rules_<mã_đơn>.md`.

---

## 💡 Quy Trình Phối Hợp Giữa Script và Agent (Khuyên Dùng)

Để đạt hiệu quả cao nhất và không tốn chi phí gọi API cá nhân:
1. Người dùng đặt tệp mẫu vào `data/pdf/NewForm/`.
2. Chạy script tiền xử lý:
   ```bash
   venv/Scripts/python.exe tools/prompt_generator/onboard_prep.py
   ```
3. Yêu cầu Agent trực tiếp trên khung chat đọc file `onboard_request.json`, tự xem ảnh bằng công cụ `view_file` và tự động đóng gói Skill mới cho đối tác.
