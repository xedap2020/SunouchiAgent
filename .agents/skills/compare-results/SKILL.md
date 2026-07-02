---
name: compare-results
description: Sử dụng kỹ năng này để tự động so sánh tệp JSON trích xuất từ PDF với tệp JSON correct trên ERP cho Sunouchi IT, tự động áp dụng các bộ lọc nghiệp vụ để chỉ hiển thị các lỗi nghiêm trọng thực sự cần sửa prompt.
compatibility: Windows OS, Python 3.x.
---

# Kỹ năng So sánh Kết quả JSON (Compare Results)

Kỹ năng này hướng dẫn trợ lý AI cách thực hiện so sánh tệp JSON trích xuất từ PDF với tệp JSON correct từ ERP, lọc bỏ các sai lệch không quan trọng theo nghiệp vụ và chỉ hiển thị các trường bị lỗi nghiêm trọng cần sửa lại prompt.

## Các bước thực hiện

Khi nhận được yêu cầu so sánh kết quả JSON của một mã đơn hàng (ví dụ: `J173192`):

### Bước 1: Xác định và đọc các tệp tin dữ liệu
1. Tìm tệp JSON trích xuất của đơn hàng trong thư mục `data/pdf/json/` (ví dụ: tìm tệp `*J173192*.json`).
2. Tìm tệp JSON correct của đơn hàng trong thư mục `data/pdf/Fixbug/` (ví dụ: tìm tệp `*J173192*correct.json`).
3. Sử dụng công cụ `view_file` để đọc nội dung của cả hai tệp JSON này.

### Bước 2: Thực hiện đối chiếu theo quy tắc lọc lỗi nghiệp vụ
Tiến hành đối chiếu từng trường dữ liệu trong phần `header` và bảng `items` (chỉ so sánh các trường cốt lõi của sản phẩm: `商品コード`, `長さ`, `員数`, `オーダーNo`, `工事名`).

Áp dụng các quy tắc lọc lỗi sau:

1. **Bỏ qua hoàn toàn (Không báo cáo, không cần quan tâm)**:
   * Trường `受注担当者` (trường này không cần dùng app ERP để nhập nên bỏ qua).
   * Trường `搬入口` (trường này không cần dùng app ERP để nhập nên bỏ qua).

2. **Bỏ qua sai lệch nhỏ (Không báo cáo, không cần sửa prompt)**:
   * Trường `オーダーNo`: Sai lệch nhỏ về khoảng trắng (ví dụ: `6B64` so với `6B 64`).
   * Trường `工事名`: Các sai lệch nhỏ do thuật toán rút gọn hoặc viết tắt ở PDF (ví dụ: lệch tiền tố viết tắt đầu dòng như `十` so với `ナ`, hoặc thiếu các từ bổ trợ như `第一種`, `建築物`, `市街地`...).

3. **Bỏ qua sai lệch của các trường phục vụ tra cứu nếu mã code đích đã khớp (Không báo cáo, không cần sửa prompt)**:
   * Các trường tên hoặc mã phụ như `customer_name1`, `customer_name2`, `matsumoto_customer` (mã khách hàng phụ) chỉ phục vụ cho việc tra cứu tìm mã khách hàng chính `customer_code`. Do đó, **nếu `customer_code` của tệp trích xuất PDF đã trùng khớp với tệp correct, mọi sai lệch của `customer_name1`, `customer_name2` và `matsumoto_customer` đều được bỏ qua**.
   * Trường `supplier_name` phục vụ cho việc tra cứu tìm mã nhà cung cấp `supplier_code`. Do đó, **nếu `supplier_code` của tệp trích xuất PDF đã trùng khớp với tệp correct, mọi sai lệch của `supplier_name` đều được bỏ qua**.
   * Các trường đại lý như `代理店`, `matsumoto_agent` chỉ phục vụ để tìm mã đại lý chính `agent`. Do đó, **nếu mã đại lý `agent` của tệp trích xuất PDF đã trùng khớp với tệp correct (chấp nhận lệch số 0 ở đầu hoặc khoảng trắng), mọi sai lệch của `代理店` và `matsumoto_agent` đều được bỏ qua**.

4. **Xác định lỗi nghiêm trọng (BẮT BUỘC báo cáo và yêu cầu sửa prompt)**:
   * Sai lệch mã khách hàng `customer_code` hoặc mã nhà cung cấp `supplier_code`.
   * Sai lệch mã đại lý `agent` (ngoại trừ trường hợp chỉ lệch số 0 ở đầu hoặc khoảng trắng).
   * Sai lệch mã sản phẩm `商品コード` ở các dòng sản phẩm.
   * Sai lệch số lượng `員数` hoặc chiều dài `長さ` của sản phẩm.
   * Thừa hoặc thiếu dòng sản phẩm (lệch số lượng các item).
   * Sai lệch trường `受注区分` hoặc `出荷倉庫` / `shipping_warehouse`.

### Bước 3: Phản hồi kết quả cho người dùng
* Chỉ hiển thị danh sách các lỗi nghiêm trọng thực sự cần sửa (các lỗi thuộc nhóm 4).
* Trình bày ngắn gọn, ghi rõ: Tên trường/Dòng sản phẩm bị lệch, giá trị trích xuất từ PDF (Anti) và giá trị nhập thực tế trên ERP (Correct).
* Nếu không phát hiện lỗi nghiêm trọng nào, thông báo: *"Khớp hoàn toàn hoặc không phát hiện lỗi nghiêm trọng nào cần sửa prompt."*
