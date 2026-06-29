---
name: sunouchi-it
description: Sử dụng kỹ năng này để phân loại tài liệu PDF/hình ảnh (hóa đơn, đơn đặt hàng, bản vẽ) cho Sunouchi IT, trích xuất dữ liệu có cấu trúc, tra cứu mã cơ sở dữ liệu (sản phẩm, khách hàng, nhà cung cấp) từ MySQL cục bộ, và tự động nhập/điền dữ liệu JSON đã tra cứu vào ứng dụng ERP Nhật Bản bằng cách mô phỏng bàn phím/chuột ở cấp hệ điều hành. Kích hoạt kỹ năng này khi người dùng yêu cầu xử lý, trích xuất hoặc phân loại tệp PDF hóa đơn/đơn đặt hàng, so khớp mã với cơ sở dữ liệu hoặc chạy công cụ tự động nhập liệu ERP Auto-Typer.
compatibility: Windows OS, Python 3.x với venv, cơ sở dữ liệu MySQL cục bộ và môi trường tương thích PyAutoGUI.
---

# Kỹ năng Agent Sunouchi IT

Kỹ năng này đăng ký các công cụ và hướng dẫn tùy chỉnh cho quy trình Phân loại & Trích xuất PDF và ERP Auto-Typer trong không gian làm việc Sunouchi IT.

---

## Các kịch bản có sẵn

Kỹ năng này cung cấp các kịch bản Python sau đây nằm trong thư mục `scripts/`. Khi chạy các kịch bản này, hãy đảm bảo môi trường ảo Python của không gian làm việc đã được kích hoạt hoặc sử dụng `venv/Scripts/python.exe`.

- **`scripts/run_pipeline.py`**
  - **Mục đích**: Tự động hóa và tối ưu hóa quy trình phân loại & trích xuất PDF hàng loạt, giúp nén và đối chiếu cơ sở dữ liệu cho nhiều tệp cùng lúc để giảm số lượt tương tác của Agent.
  - **Sử dụng**:
    - Nén tất cả hoặc các PDF đầu vào được chọn:
      ```bash
      # Nén tất cả PDF đầu vào
      venv/Scripts/python.exe scripts/run_pipeline.py --action compress_all
      # Hoặc chỉ nén các PDF cụ thể (cách nhau bởi dấu phẩy)
      venv/Scripts/python.exe scripts/run_pipeline.py --action compress_all --files "file1.pdf,file2.pdf"
      ```
    - Giải quyết đối chiếu mã DB hàng loạt:
      ```bash
      venv/Scripts/python.exe scripts/run_pipeline.py --action resolve_batch --json_file <đường_dẫn_batch_json>
      ```
- **`scripts/db_helper.py`**
  - **Mục đích**: Kết nối với cơ sở dữ liệu MySQL cục bộ để tra cứu và khớp mã (sản phẩm, khách hàng, nhà cung cấp) cho dữ liệu JSON hóa đơn đã trích xuất.
  - **Sử dụng**:
    ```bash
    venv/Scripts/python.exe scripts/db_helper.py --action resolve --json_file <đường_dẫn_json>
    ```
- **`scripts/autoType.py`**
  - **Mục đích**: Tự động nhập dữ liệu JSON đã đối chiếu vào ứng dụng desktop ERP Nhật Bản bằng cách mô phỏng bàn phím và chuột cấp hệ điều hành.
  - **Sử dụng**:
    ```bash
    venv/Scripts/python.exe scripts/autoType.py --json_file <đường_dẫn_json_đã_đối_chiếu> [--open_new_form]
    ```
- **`scripts/compress_pdf.py`**
  - **Mục đích**: Nén file PDF thành dạng ảnh chất lượng trung bình (120 DPI, 70% quality) để tối ưu dung lượng và tăng tốc xử lý cho Agent.
  - **Sử dụng**:
    ```bash
    venv/Scripts/python.exe scripts/compress_pdf.py --input <đường_dẫn_pdf_gốc> --output <đường_dẫn_pdf_nén>
    ```
- **`scripts/update_fields.py`**
  - **Mục đích**: Sửa lỗi/nhập lại các trường thông tin Header bị sai trên màn hình ERP đang mở mà không cần nhập lại toàn bộ đơn.
  - **Sử dụng**:
    - Truyền trực tiếp chuỗi JSON:
      ```bash
      venv/Scripts/python.exe scripts/update_fields.py --fields "{\"work_name\": \"(仮称)イオンモール郡山...\"}"
      ```
    - Truyền qua file JSON:
      ```bash
      venv/Scripts/python.exe scripts/update_fields.py --json_file <đường_dẫn_file_json>
      ```
- **`tools/prompt_generator/onboard_prep.py`**
  - **Mục đích**: Tự động ghép cặp PDF-ERP mẫu, convert các trang PDF sang ảnh và sinh file request phục vụ quy trình Onboarding.
  - **Sử dụng**:
    ```bash
    venv/Scripts/python.exe tools/prompt_generator/onboard_prep.py
    ```
---

## 1. Bộ phân loại & Trích xuất PDF

Thực hiện phân loại và trích xuất dữ liệu từ các tài liệu PDF/hình ảnh (hóa đơn, đơn đặt hàng, bản vẽ) bằng ngữ cảnh mô hình của Agent, sau đó ánh xạ dữ liệu trích xuất với mã cơ sở dữ liệu (sản phẩm, khách hàng, nhà cung cấp) bằng cách kết nối trực tiếp với cơ sở dữ liệu MySQL cục bộ.

### Cách sử dụng
Là người dùng, bạn có thể yêu cầu:
- *"Chạy PDF Classifier cho file <đường dẫn file>"* (chạy tool phân loại và trích xuất dựa trên đường dẫn file cục bộ)
- *"Tôi có những tool gì?"* (xem danh sách công cụ hiện có)

### Danh sách kiểm tra quy trình (Tối ưu hóa hàng loạt - Khuyên dùng)
Làm theo danh sách kiểm tra này để xử lý các tài liệu một cách hiệu quả và tiết kiệm lượt tương tác:

- [ ] **Bước 1: Xác định và hiển thị các tệp đầu vào**
  - Thư mục đầu vào chứa các tệp PDF gốc: `data/pdf/PDF/`.
  - **BẮT BUỘC**: Phải phản hồi theo đúng cấu trúc mẫu cố định sau đây để đảm bảo tính nhất quán (không tự ý thêm bớt từ ngữ ngoài mẫu này):
    
    ---
    Tôi đã mở công cụ **Sunouchi IT**.

    Dưới đây là danh sách các tệp PDF đầu vào cần xử lý trong thư mục `data/pdf/PDF/`:
    - [Tên_File_1.pdf](file:///<đường_dẫn_thư_mục_gốc_dự_án_đã_url_encode>/data/pdf/PDF/Tên_File_1_đã_url_encode.pdf)
    - [Tên_File_2.pdf](file:///<đường_dẫn_thư_mục_gốc_dự_án_đã_url_encode>/data/pdf/PDF/Tên_File_2_đã_url_encode.pdf)
    ...
    (* LƯU Ý: Phải thay thế <đường_dẫn_thư_mục_gốc_dự_án_đã_url_encode> bằng đường dẫn tuyệt đối của thư mục gốc dự án thực tế trên máy chạy, ví dụ: file:///d:/SunouchiAgent/ *)

    Vui lòng phản hồi ("trích xuất",...) và cho biết bạn muốn xử lý bao nhiêu file để bắt đầu bước tiếp theo.
    ---
  - **BẮT BUỘC**: Chờ người dùng gửi xác nhận đồng ý (ví dụ: "đồng ý", "ok", "trích xuất",...) rồi mới được thực hiện chạy các lệnh nén hay trích xuất ở Bước 2.
- [ ] **Bước 2: Nén các tệp PDF đầu vào cần xử lý**
  - Chạy lệnh nén để chuyển đổi các tệp PDF cần xử lý sang thư mục tạm:
    - Nếu xử lý tất cả các tệp đầu vào:
      ```bash
      venv/Scripts/python.exe scripts/run_pipeline.py --action compress_all
      ```
    - Nếu người dùng chỉ yêu cầu xử lý (các) tệp cụ thể (ví dụ: `file1.pdf` và `file2.pdf`):
      ```bash
      venv/Scripts/python.exe scripts/run_pipeline.py --action compress_all --files "file1.pdf,file2.pdf"
      ```
- [ ] **Bước 3: Đọc và Trích xuất hàng loạt (Batch Extraction)**
  - Liệt kê các tệp trong `data/temp_compress/` (chỉ xử lý các tệp tương ứng với yêu cầu).
  - Với mỗi tệp PDF tạm thời cần xử lý:
    - Sử dụng `view_file` để đọc nội dung của tệp.
    - Phân loại tài liệu theo mẫu từ `invoice1` đến `invoice13`.
    - Trích xuất dữ liệu thô (raw JSON) tuân thủ chính xác theo schema của mẫu hóa đơn đó.
  - Gộp tất cả dữ liệu trích xuất thô vào một tệp cấu trúc JSON duy nhất tại `data/batch_raw.json` theo định dạng sau:
    ```json
    {
      "Tên_file_gốc_1.pdf": { <Dữ liệu JSON thô của file 1> },
      "Tên_file_gốc_2.pdf": { <Dữ liệu JSON thô của file 2> }
    }
    ```
- [ ] **Bước 4: Chạy Đối chiếu DB hàng loạt và Dọn dẹp**
  - Chạy lệnh đối chiếu DB tự động cho tất cả dữ liệu thô trong `data/batch_raw.json`. Lệnh này sẽ tự động lưu các file JSON đã giải quyết mã vào `data/pdf/json/`, đồng thời tự động xóa thư mục file tạm:
    ```bash
    venv/Scripts/python.exe scripts/run_pipeline.py --action resolve_batch --json_file data/batch_raw.json
    ```
- [ ] **Bước 5: Hiển thị kết quả tóm tắt cho người dùng**
  - **BẮT BUỘC**: Phải phản hồi theo đúng cấu trúc mẫu cố định sau đây để đảm bảo tính nhất quán (không tự ý thêm bớt từ ngữ ngoài mẫu này):

    ---
    Tôi đã hoàn thành quy trình Phân loại & Trích xuất dữ liệu.

    Dưới đây là danh sách các tệp JSON đã được xuất thành công:
    - [Tên_File_1.json](file:///<đường_dẫn_thư_mục_gốc_dự_án_đã_url_encode>/data/pdf/json/Tên_File_1_đã_url_encode.json) (Loại tài liệu: [Loại_Tài_Liệu_1])
    - [Tên_File_2.json](file:///<đường_dẫn_thư_mục_gốc_dự_án_đã_url_encode>/data/pdf/json/Tên_File_2_đã_url_encode.json) (Loại tài liệu: [Loại_Tài_Liệu_2])
    ...
    (* LƯU Ý: Phải thay thế <đường_dẫn_thư_mục_gốc_dự_án_đã_url_encode> bằng đường dẫn tuyệt đối của thư mục gốc dự án thực tế trên máy chạy, ví dụ: file:///d:/SunouchiAgent/ *)

    Bạn có muốn chạy công cụ **ERP Auto-Typer** để tự động nhập dữ liệu từ các tệp JSON này vào ứng dụng ERP không?
    ---

---

## 2. ERP Auto-Typer

Tự động nhập dữ liệu JSON đã đối chiếu vào ứng dụng ERP Nhật Bản bằng cách mô phỏng bàn phím/chuột cấp hệ điều hành.

### Cách sử dụng
Là người dùng, bạn có thể yêu cầu:
- *"Chạy ERP Auto-Typer"* (tự động quét và điền toàn bộ file JSON trong thư mục data/pdf/json)
- *"Chạy ERP Auto-Typer cho file <đường dẫn JSON>"* (chạy nhập liệu cho riêng file được chỉ định)

### Danh sách kiểm tra quy trình
Làm theo danh sách kiểm tra này để thực thi Auto-Typer:

- [ ] **Bước 1: Xác định các tệp JSON**
  - Nếu một đường dẫn tệp cụ thể được cung cấp, bỏ qua và chuyển đến **Bước 3**.
  - Nếu không, xác định thư mục hoạt động: `data/pdf/json/`.
- [ ] **Bước 2: Thực hiện tự động nhập hàng loạt**
  - Liệt kê tất cả các tệp `.json` trong thư mục `data/pdf/json/`. Nếu không có tệp nào tồn tại, thông báo cho người dùng.
  - Khuyên người dùng rằng quá trình tự động nhập hàng loạt đang chạy và họ **KHÔNG ĐƯỢC** sử dụng bàn phím/chuột.
  - Chạy kịch bản tuần tự cho tất cả các tệp:
    ```powershell
    Get-ChildItem "data/pdf/json/*.json" | ForEach-Object {
        venv\Scripts\python.exe scripts\autoType.py --json_file $_.FullName
    }
    ```
- [ ] **Bước 3: Thực hiện tệp đơn lẻ**
  - Đọc tệp JSON được chỉ định và xác minh định dạng của nó (ví dụ: có `customer_code`, `slip_date`, `slip_number`, `detail_list`, v.v.).
  - Khuyên người dùng rằng quá trình tự động nhập đang bắt đầu và họ **KHÔNG ĐƯỢC** sử dụng bàn phím/chuột.
  - Chạy kịch bản (thêm `--open_new_form` nếu được yêu cầu mở một biểu mẫu mới):
    ```bash
    venv/Scripts/python.exe scripts/autoType.py --json_file <đường_dẫn_tệp_json_đã_đối_chiếu>
    ```

---

## 3. Bộ thiết lập và Đóng gói Form Mới (Onboarding)

Hướng dẫn Agent cách hỗ trợ người dùng khi họ muốn thiết lập quy tắc trích xuất và đóng gói Kỹ năng xử lý cho biểu mẫu hóa đơn mới.

### Cách sử dụng & Kích hoạt
Khi người dùng yêu cầu:
- *"Tôi muốn thiết lập form mới"*, *"Tạo prompt cho hóa đơn mới"* hoặc hỏi các câu tương tự liên quan đến cách dạy/thiết lập form mới:
  -> Agent **BẮT BUỘC** phải gửi hướng dẫn chuẩn bị tài liệu cho người dùng trước tiên:
     1. Đặt các tệp PDF đơn hàng gốc và ảnh chụp ERP tương ứng vào thư mục `data/pdf/NewForm/`.
     2. Đặt tên tệp giống nhau hoàn toàn để hệ thống tự khớp cặp (ví dụ: `TenĐốiTác_J123456.pdf` và `TenĐốiTác_J123456.png`).
     3. Khuyên họ dùng từ 2-3 tệp mẫu để có độ chính xác cao nhất.
     4. Bảo người dùng phản hồi *"Chạy script chuẩn bị"* sau khi đã để các file vào đúng chỗ.

- *"Chạy script chuẩn bị form mới"* hoặc *"Chuẩn bị các tệp đơn hàng mới"* -> Chạy script `onboard_prep.py`.
- *"Hãy phân tích các mẫu đã chuẩn bị và đóng gói thành Skill mới cho [Tên_Đối_Tác]"* -> Agent tự thực hiện phân tích và sinh Skill mới.

### Danh sách kiểm tra quy trình (Dành cho Agent)
Khi nhận lệnh đóng gói Skill mới từ người dùng:

- [ ] **Bước 1: Đọc tệp tin yêu cầu đã được chuẩn bị**
  - Đọc nội dung tệp `data/temp_onboard/onboard_request.json` để biết danh sách các tệp đơn hàng mẫu đã được chuẩn bị (gồm đường dẫn ảnh trang PDF và ảnh ERP tương ứng).
  
- [ ] **Bước 2: Phân tích hình ảnh đối chiếu**
  - Sử dụng công cụ `view_file` để mở và xem các ảnh trang PDF của đơn hàng và ảnh chụp ERP.
  - Phân tích và so sánh đối chiếu giá trị hiển thị trên ERP với các vị trí, định dạng trên PDF để hiểu quy luật trích xuất và ánh xạ trường dữ liệu.
  
- [ ] **Bước 3: Tạo thư mục Skill và Đăng ký**
  - Tạo thư mục Skill mới: `.agents/skills/form-[tên_đối_tác_viết_thường]/`.
  - Tạo tệp `SKILL.md` để đăng ký kỹ năng với cấu trúc:
    ```yaml
    ---
    name: form-[tên_đối_tác]
    description: Sử dụng kỹ năng này để trích xuất dữ liệu có cấu trúc từ tệp PDF hóa đơn [Tên_Đối_Tác] (invoice[X]) cho Sunouchi IT.
    compatibility: Windows OS, Python 3.x với venv, cơ sở dữ liệu MySQL cục bộ.
    ---
    ```
  
- [ ] **Bước 4: Tạo tài liệu Quy tắc trích xuất**
  - Tạo tệp `references/extraction_rules.md` chứa cấu trúc JSON chuẩn và hướng dẫn trích xuất chi tiết bằng Tiếng Việt cho từng trường dựa trên phân tích hình ảnh ở Bước 2.
  - Đảm bảo gán đúng mã `customer_code` cố định nếu có quy định, và để `null` cho các trường tự động điền trên ERP (như `単価`, `金額`, `商品コード`).
  
- [ ] **Bước 5: Chạy thử nghiệm nghiệm thu (Dry-run)**
  - Chạy thử trích xuất trên PDF đơn mẫu đó, lưu kết quả thô vào `data/batch_raw.json`.
  - Thực thi lệnh đối chiếu cơ sở dữ liệu để tìm mã sản phẩm thực tế:
    ```bash
    venv/Scripts/python.exe scripts/run_pipeline.py --action resolve_batch --json_file data/batch_raw.json
    ```
  - Xác nhận kết quả JSON sinh ra khớp chính xác với ảnh ERP chụp màn hình.

---

## Lưu ý & Trường hợp biên

- **Tên tệp quyết định `customer_code`**: Trước khi trích xuất dữ liệu, bạn **BẮT BUỘC** phải kiểm tra tên tệp PDF và đối chiếu để gán mã `customer_code` phù hợp theo bảng quy tắc tập trung tại [AGENTS.md](file:///e:/SunouchiAgent/.agents/AGENTS.md). **KHÔNG** tự ý ghi đè bằng logic khác.


- **Không can thiệp vào quá trình Autotype**: ERP Auto-Typer thực hiện tự động hóa GUI cấp hệ điều hành bằng cách nhấp chuột và nhập bàn phím. Khuyên người dùng tránh xa bàn phím/chuột và không chuyển đổi cửa sổ đang hoạt động trong khi quy trình đang chạy.
- **Kết nối cơ sở dữ liệu MySQL**: Quy trình tra cứu đối chiếu mã (`db_helper.py`) kết nối trực tiếp với thực thể MySQL cục bộ. Nếu cơ sở dữ liệu ngoại tuyến hoặc không được cấu hình chính xác trong các biến môi trường, bước tra cứu mã sẽ thất bại.
- **Thực thi không tương tác**: Cả hai kịch bản xử lý PDF và nhập liệu ERP phải chạy trong môi trường shell không tương tác. Không mong đợi bất kỳ lời nhắc tương tác nào hoặc yêu cầu nhập thông tin trong quá trình thực thi.
