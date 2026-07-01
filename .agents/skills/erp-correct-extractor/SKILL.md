---
name: erp-correct-extractor
description: Sử dụng kỹ năng này để trích xuất hoặc đọc dữ liệu JSON đúng từ ảnh chụp màn hình ERP (Correct ERP Screenshot) cho Sunouchi IT bằng cách sử dụng cấu trúc Shape Chung (Universal Shape).
compatibility: Windows OS, Python 3.x.
---

# Kỹ năng Đọc JSON Đúng từ Ảnh ERP (ERP Correct Extractor)

Kỹ năng này cung cấp cấu trúc **Shape Chung (Universal Shape)** và các quy tắc nghiệp vụ để trích xuất dữ liệu từ ảnh chụp màn hình ERP nhằm tạo ra file `J*_correct.json` chuẩn xác.

---

## I. Cấu trúc Shape Chung (Universal Shape)

Khi người dùng yêu cầu đọc JSON đúng từ ảnh chụp ERP, hãy sử dụng chính xác cấu trúc Shape dưới đây để gán các trường dữ liệu:

```json
{
  "header": {
    "受注区分": null,
    "搬入口": null,
    "代理店": null,
    "出荷日": null,
    "納期": null,
    "出荷倉庫": null,
    "オーダーNo": null,
    "工事名": null,
    "受注担当者": null,
    "customer_name1": null,
    "customer_name2": null,
    "customer_code": null,
    "matsumoto_customer": null,
    "supplier_name": null,
    "supplier_code": null,
    "supplier_postal_code": null,
    "supplier_tel": null,
    "shipping_warehouse": null,
    "agent": null,
    "matsumoto_agent": null,
    "comment": null
  },
  "tables": {
    "items": [
      {
        "商品コード": null,
        "長さ": null,
        "員数": null,
        "オーダーNo": null,
        "工事名": null,
        "product_title": null,
        "product_type": null,
        "product_size": null,
        "is_processing": null
      }
    ]
  }
}
```

---

## II. Quy tắc trích xuất & Nghiệp vụ đặc biệt

Khi đọc dữ liệu từ ảnh ERP và điền vào cấu trúc Shape Chung, bạn phải tuân thủ nghiêm ngặt các quy tắc sau:

### 1. Quy tắc hiển thị thực tế trên ERP (QUAN TRỌNG)
* **KHÔNG áp dụng Blacklist của PDF**: Khi đọc từ ảnh ERP, **tuyệt đối không** áp dụng các quy tắc cấm trích xuất (Explicit Blacklist) của file PDF gốc. 
* **Nhập đúng dữ liệu thực tế**: Màn hình ERP hiển thị giá trị gì cho các ô nhập liệu (`受注区分`, `受注担当者`, `出荷倉庫`...) thì ta **phải ghi nhận đúng giá trị đó** vào file JSON correct. Chỉ để `null` nếu ô đó trên ERP bị trống hoặc không có thông tin.

### 2. Quy tắc cho phần sản phẩm (Table Items)
* **Chỉ quan tâm đến `商品コード`**: 
  * Hãy đọc mã sản phẩm hiển thị trên cột **商品コード** của ERP (ví dụ: `"0000000000000440055"` hoặc `"000000000000483127"`).
  * Đối với các trường **`product_title`**, **`product_type`**, và **`product_size`** ở bảng sản phẩm -> **BẮT BUỘC gán giá trị `null`** cho tất cả các dòng.
* **Loại bỏ dòng phí vận chuyển ở cuối**:
  * Nếu dòng cuối cùng của bảng sản phẩm chứa mã `"0000000000000000001"` hoặc có tên sản phẩm là `"スノウチ 送料"`, `"運賃"`, `"送料"` -> **BẮT BUỘC loại bỏ dòng này** ra khỏi danh sách `items` (không trích xuất dòng này).

### 3. Quy tắc cho phần Header
* **Các trường Code và Mapping thực tế**:
  * Đọc các mã số thực tế hiển thị trên màn hình ERP như: `customer_code` (Mã khách hàng chính), `matsumoto_customer` (Mã khách hàng phụ), `supplier_code` (Mã nhà cung cấp), `matsumoto_agent` (Mã đại lý), `agent` (Mã đại lý/đối tác trên ERP).
  * Đối với các trường tên như `customer_name1`, `customer_name2`, `supplier_name`... nếu trên ERP có hiển thị dữ liệu thì trích xuất và chuẩn hóa chính xác. Nếu không có hoặc để trống thì gán `null`.
* **Trường trống**:
  * Bất kỳ trường nào trong Shape Chung không hiển thị dữ liệu hoặc để trống trên màn hình ERP -> Gán giá trị `null`.

### 4. Quy tắc phản hồi (TUYỆT ĐỐI TUÂN THỦ)
* **Phạm vi đọc tệp**: Chỉ đọc trực tiếp tệp hình ảnh ERP được yêu cầu. Tuyệt đối không tìm kiếm hoặc mở bất kỳ tệp JSON nào khác trong thư mục `data/pdf/json/` để làm tài liệu tham khảo.
* **Chỉ gửi thông báo hoàn thành**: Khi được yêu cầu sử dụng kỹ năng này, Agent **BẮT BUỘC CHỈ** tạo/ghi tệp JSON correct và hiển thị thông báo hoàn thành việc ghi tệp cho người dùng. **KHÔNG** hiển thị nội dung JSON đã trích xuất trong phản hồi, và **TUYỆT ĐỐI KHÔNG** tự ý thực hiện so sánh, đối chiếu kết quả với tệp trích xuất PDF hoặc hiển thị thêm bất kỳ phân tích lỗi so sánh nào.

