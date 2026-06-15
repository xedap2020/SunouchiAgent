# 🤖 Sunouchi IT Agent - Hướng Dẫn Sử Dụng Hệ Thống

Chào mừng bạn đến với hệ thống trợ lý ảo **Sunouchi IT Agent**. Hệ thống này giúp tự động hóa quy trình phân loại, trích xuất dữ liệu từ hóa đơn PDF và tự động nhập liệu vào phần mềm ERP Nhật Bản.

Dưới đây là tài liệu hướng dẫn nhanh dành cho người sử dụng.

---

## ⚡ WORKFLOW 1: Trích Xuất Dữ Liệu & Nhập Liệu Tự Động Hàng Ngày

Khi bạn có các tệp PDF hóa đơn mới từ đối tác cần trích xuất dữ liệu và nhập vào ERP:

### 1. Chuẩn bị tệp tin
* Đặt các file PDF hóa đơn mới vào thư mục: 📂 `data/pdf/PDF/`

### 2. Ra lệnh cho Agent trên Khung Chat
Bạn có thể trò chuyện với Agent bằng các câu lệnh tự nhiên sau:
* **Xem danh sách tệp tin**:
  > *"Tôi đang có những file nào cần trích xuất?"* hoặc *"Hiển thị các file mới nhất"*
* **Trích xuất dữ liệu tự động**:
  > *"Trích xuất dữ liệu"* hoặc *"Trích xuất file J167095 cho tôi"*
* **Chạy Auto-Typer điền dữ liệu vào ERP**:
  > *"Chạy ERP Auto-Typer"* hoặc *"Chạy ERP Auto-Typer cho file [Tên_File.json]"*

---

## ⚡ WORKFLOW 2: Tự Động Thiết Lập & Đóng Gói Form Hóa Đơn Mới (Onboarding)

Khi bạn nhận được hóa đơn từ một đối tác mới có bố cục (layout) chưa từng xuất hiện trong hệ thống, bạn có thể "dạy" Agent nhận diện form đó chỉ qua 3 bước:

### 1. Chuẩn bị tệp tin mẫu
Bạn hãy đặt file PDF đơn hàng gốc và ảnh chụp màn hình ERP đã nhập mẫu vào thư mục:
📂 `data/pdf/NewForm/`

> [!IMPORTANT]
> **Quy tắc đặt tên**: Đặt tên tệp PDF và tệp ảnh ERP giống nhau hoàn toàn để hệ thống tự khớp cặp (ví dụ: `Don_Kagaya_J167095.pdf` đi kèm với `Don_Kagaya_J167095.png`).

### 2. Chạy lệnh tiền xử lý
Mở khung chat và yêu cầu Agent:
> *"Chạy script chuẩn bị form mới"*

*(Agent sẽ tự động chạy công cụ `onboard_prep.py` để chuyển đổi PDF thành ảnh và tạo danh sách yêu cầu).*

### 3. Đóng gói Skill mới
Ra lệnh cho Agent tiến hành phân tích hình ảnh và tạo luật trích xuất:
> *"Hãy tự động phân tích các mẫu đã chuẩn bị và đóng gói thành Skill mới cho [Tên_Đối_Tác]"*

Agent sẽ tự động xem ảnh đơn hàng và ERP, tự viết quy tắc trích xuất tiếng Việt, đăng ký Skill mới và chạy thử nghiệm đối chiếu DB để nghiệm thu trước khi bàn giao cho bạn.

---

## 📁 Sơ Đồ Tổ Chức Thư Mục Chính

* 📂 `data/pdf/PDF/`: Nơi chứa các tệp PDF hóa đơn cần trích xuất hàng ngày.
* 📂 `data/pdf/NewForm/`: Nơi đặt các cặp tệp PDF và ảnh ERP để dạy form mới.
* 📂 `data/pdf/json/`: Kết quả JSON sau khi trích xuất và đối chiếu Database thành công (dùng làm đầu vào cho Auto-Typer).
* 📂 `.agents/skills/`: Nơi lưu trữ các Kỹ năng trích xuất đã được đóng gói cho từng khách hàng (ví dụ: `form-kagaya`, `form-furusato`).
* 📂 `tools/prompt_generator/`: Bộ công cụ hỗ trợ chuẩn bị dữ liệu và sinh quy tắc trích xuất.

---

> [!TIP]
> **Mẹo nâng cao độ chính xác**: Khi thiết lập form mới, bạn nên cung cấp từ **2 đến 3 cặp đơn hàng mẫu** khác nhau của cùng đối tác đó. Việc phân tích chéo nhiều mẫu sẽ giúp Agent tạo ra bộ quy tắc trích xuất hoàn hảo đạt độ chính xác gần như 100%.
