# Target JSON Schema
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
    "supplier_name": null,
    "supplier_code": null,
    "supplier_postal_code": null,
    "supplier_tel": null,
    "agent": null
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
        "col_maker": null,
        "mat_size": null,
        "category_small": null,
        "is_processing": null
      }
    ]
  }
}
```

# Extraction Rules

Các quy tắc trích xuất dưới đây mô tả cách ánh xạ các trường từ tài liệu PDF sang cấu trúc JSON, sử dụng ảnh chụp màn hình ERP làm tham chiếu để xác định dữ liệu cần trích xuất. Các trường không có trong PDF hoặc không thể suy ra theo quy tắc sẽ được đặt là `null`.

## Header Fields

1.  **`受注区分` (Loại đơn đặt hàng)**:
    *   **Quy tắc**: Không có trong PDF.
    *   **Giá trị**: `null`.
2.  **`搬入口` (Cửa giao hàng)**:
    *   **Quy tắc**: Trích xuất chuỗi văn bản nằm sau "武道工場" trong trường "納入場所" trên PDF Trang 2 và 3.
    *   **Ví dụ**: "タイコ班" (từ P2) hoặc "大組立て" (từ P3). Nếu không có chuỗi cụ thể, hãy trích xuất toàn bộ "武道工場".
3.  **`代理店` (Đại lý)**:
    *   **Quy tắc**: Không có trong PDF.
    *   **Giá trị**: `null`.
4.  **`出荷日` (Ngày xuất hàng)**:
    *   **Quy tắc**: Ánh xạ từ "受注日" trong ERP, là "2026/03/30". Mặc dù PDF có "作成日: 2026年 3月 12日", chúng ta sẽ tuân theo ánh xạ từ ERP.
    *   **Định dạng**: YYYY/MM/DD.
    *   **Giá trị**: "2026/03/30".
5.  **`納期` (Ngày giao hàng)**:
    *   **Quy tắc**: Trích xuất từ "希望納期は3/31" trên PDF Trang 1 hoặc từ trường "納期" trên PDF Trang 2 và 3.
    *   **Định dạng**: YYYY/MM/DD.
    *   **Ví dụ**: "2026/03/31".
6.  **`出荷倉庫` (Kho xuất hàng)**:
    *   **Quy tắc**: Không có trong PDF. (Trong ERP là "未指定").
    *   **Giá trị**: `null`.
7.  **`オーダーNo` (Số đơn hàng)**:
    *   **Quy tắc**: Trích xuất từ trường "NO." trên PDF Trang 2 và 3. Chỉ lấy phần mã sau dấu gạch ngang.
    *   **Ví dụ**: "Y4" (từ "NO. -Y4") hoặc "Y5" (từ "NO. -Y5").
8.  **`工事名` (Tên công trình)**:
    *   **Quy tắc**: Trích xuất từ trường "工事名" trên PDF Trang 2 và 3, kết hợp với các chi tiết liên quan từ "件名" trên PDF Trang 1 và "品名" trên PDF Trang 2 và 3.
    *   **Ví dụ**: "メープルツリー北上金ヶ崎 ロジスティクスセンター新築工事". (Chi tiết "①工区 (2～4節) Hタイコウラ当て" sẽ được thêm vào `工事名` của từng mục hàng).
9.  **`受注担当者` (Người phụ trách đơn hàng)**:
    *   **Quy tắc**: Trích xuất tên người từ trường "発注担当" trên PDF Trang 2 và 3.
    *   **Ví dụ**: "澤口".
10. **`customer_name1` (Tên khách hàng 1)**:
    *   **Quy tắc**: Trích xuất tên công ty từ trường "宛先" trên PDF Trang 1 hoặc "発注先" trên PDF Trang 2 và 3.
    *   **Ví dụ**: "(株)スノウチ".
11. **`customer_name2` (Tên khách hàng 2)**:
    *   **Quy tắc**: Không có trong PDF.
    *   **Giá trị**: `null`.
12. **`customer_code` (Mã khách hàng)**:
    *   **Quy tắc**: Không có trong PDF. (Có trong ERP là "J00169896").
    *   **Giá trị**: `null`.
13. **`supplier_name` (Tên nhà cung cấp)**:
    *   **Quy tắc**: Kết hợp tên công ty từ "差出人" trên PDF Trang 1 và địa điểm từ "納入場所" trên PDF Trang 2 và 3.
    *   **Ví dụ**: "(株)カガヤ 武道工場".
14. **`supplier_code` (Mã nhà cung cấp)**:
    *   **Quy tắc**: Không có trong PDF. (Có trong ERP là "130447").
    *   **Giá trị**: `null`.
15. **`supplier_postal_code` (Mã bưu chính nhà cung cấp)**:
    *   **Quy tắc**: Trích xuất mã bưu chính từ thông tin liên hệ của (株)カガヤ trên PDF Trang 1.
    *   **Định dạng**: Chỉ các chữ số và dấu gạch ngang.
    *   **Ví dụ**: "028-4131".
16. **`supplier_tel` (Số điện thoại nhà cung cấp)**:
    *   **Quy tắc**: Trích xuất số điện thoại từ thông tin liên hệ của (株)カガヤ trên PDF Trang 1.
    *   **Định dạng**: Chỉ các chữ số và dấu gạch ngang.
    *   **Ví dụ**: "019-683-2829".
17. **`agent` (Đại lý)**:
    *   **Quy tắc**: Không có trong PDF.
    *   **Giá trị**: `null`.

## Table Items Fields (Mỗi hàng trong bảng trên PDF Trang 2 và 3)

1.  **`商品コード` (Mã sản phẩm)**:
    *   **Quy tắc**: Trích xuất từ trường "符号" trong bảng trên PDF Trang 2 và 3.
    *   **Ví dụ**: "CR-F".
2.  **`長さ` (Chiều dài)**:
    *   **Quy tắc**: Trích xuất giá trị số từ cột "本数" trong bảng trên PDF Trang 2 và 3. (Lưu ý: "本数" trong PDF ánh xạ đến "長さ" trong ERP).
    *   **Định dạng**: Giá trị số nguyên.
    *   **Ví dụ**: 590, 290.
3.  **`員数` (Số lượng kiện/thùng)**:
    *   **Quy tắc**: Không có trong PDF. (Có trong ERP là số lượng kiện/thùng).
    *   **Giá trị**: `null`.
4.  **`オーダーNo` (Số đơn hàng)**:
    *   **Quy tắc**: Áp dụng `オーダーNo` được trích xuất từ phần header của trang PDF (P2 cho Y4, P3 cho Y5) cho tất cả các mục hàng trên trang đó.
    *   **Ví dụ**: "Y4" cho các mục trên P2, "Y5" cho các mục trên P3.
5.  **`工事名` (Tên công trình)**:
    *   **Quy tắc**: Kết hợp `工事名` từ header tài liệu với các chi tiết từ trường "品名" của mục hàng cụ thể. Lấy phần "①工区 (2～4節) Hタイコウラ当て" hoặc "Hシャフトウラ当て".
    *   **Ví dụ**: "メープルツリー北上金ヶ崎 ロジスティクスセンター新築工事 ①工区 (2～4節) Hタイコウラ当て".
6.  **`product_title` (Tiêu đề sản phẩm)**:
    *   **Quy tắc**: Trích xuất phần mô tả chính từ trường "品名" trong bảng.
    *   **Ví dụ**: "Hタイコ" (từ "Hタイコウラ当て") hoặc "Hシャフト" (từ "Hシャフトウラ当て").
7.  **`product_type` (Loại sản phẩm)**:
    *   **Quy tắc**: Kết hợp giá trị từ "符号" ("CR-F"), kích thước định dạng "FB-9*25" (chuyển `*` thành `X` và đặt "X" sau số cuối nếu có), và "長さ" (từ cột "長さ" của mục hàng) theo định dạng "CR-F 9X 25X155".
    *   **Ví dụ**: Từ "符号: CR-F", "FB-9*25", "長さ: 155" -> "CR-F 9X 25X155".
8.  **`product_size` (Kích thước sản phẩm)**:
    *   **Quy tắc**: Kết hợp giá trị kích thước từ "FB-9*25" (chuyển `*` thành `x`) và "長さ" (từ cột "長さ" của mục hàng).
    *   **Định dạng**: "9x25x155".
    *   **Ví dụ**: Từ "FB-9*25" và "長さ: 155" -> "9x25x155".
9.  **`col_maker` (Nhà sản xuất/Vật liệu)**:
    *   **Quy tắc**: Trích xuất từ trường "材質" trong bảng trên PDF Trang 2 và 3.
    *   **Ví dụ**: "SN490B".
10. **`mat_size` (Kích thước vật liệu)**:
    *   **Quy tắc**: Không có trong PDF ở định dạng rõ ràng (ví dụ: "90.0" trong ERP).
    *   **Giá trị**: `null`.
11. **`category_small` (Danh mục nhỏ)**:
    *   **Quy tắc**: Không có trong PDF.
    *   **Giá trị**: `null`.
12. **`is_processing` (Có gia công không)**:
    *   **Quy tắc**: Không có trong PDF (Trong ERP là một checkbox "加工").
    *   **Giá trị**: `null`.

# LLM System Prompt

Bạn là một chuyên gia kỹ sư gợi ý AI có kinh nghiệm, chuyên về tự động hóa ERP Nhật Bản. Nhiệm vụ của bạn là phân tích tài liệu PDF đơn đặt hàng mới được cung cấp và trích xuất thông tin liên quan theo cấu trúc JSON định trước. Bạn phải tuân thủ nghiêm ngặt các quy tắc trích xuất đã được cung cấp để đảm bảo tính chính xác và nhất quán.

**Hướng dẫn chung:**

1.  **Phân tích toàn diện**: Đọc kỹ toàn bộ tài liệu PDF (nhiều trang) để hiểu bối cảnh và xác định tất cả các trường dữ liệu có liên quan.
2.  **Tuân thủ quy tắc trích xuất**: Áp dụng từng quy tắc trích xuất đã được cung cấp một cách chính xác. Các quy tắc này bao gồm ánh xạ trường, định dạng, giá trị mặc định, từ viết tắt, tính toán và tra cứu.
3.  **Điền `null` cho các trường không có**: Nếu một trường được định nghĩa trong cấu trúc JSON nhưng không thể tìm thấy trong tài liệu PDF theo quy tắc trích xuất, hãy điền giá trị `null` cho trường đó. KHÔNG suy luận hoặc tạo dữ liệu cho các trường không có.
4.  **Cấu trúc JSON đầu ra**: Đảm bảo rằng đầu ra của bạn là một đối tượng JSON hợp lệ, tuân thủ chính xác cấu trúc và các tên khóa (key) đã cung cấp. KHÔNG thêm, xóa hoặc sửa đổi bất kỳ khóa nào.
5.  **Xử lý bảng**: Đối với các mục hàng trong bảng, hãy trích xuất thông tin cho từng hàng riêng biệt và đặt chúng vào mảng `items` trong đối tượng `tables`. Đảm bảo rằng các trường cấp độ tài liệu (ví dụ: `オーダーNo`, `工事名`) được áp dụng đúng cho từng mục hàng trong bảng khi được hướng dẫn bởi các quy tắc.
6.  **Định dạng dữ liệu**: Chú ý đến các yêu cầu định dạng cụ thể (ví dụ: YYYY/MM/DD cho ngày, chỉ số cho số lượng).

**Cấu trúc JSON mục tiêu (TUYỆT ĐỐI KHÔNG THAY ĐỔI):**

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
    "supplier_name": null,
    "supplier_code": null,
    "supplier_postal_code": null,
    "supplier_tel": null,
    "agent": null
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
        "col_maker": null,
        "mat_size": null,
        "category_small": null,
        "is_processing": null
      }
    ]
  }
}
```

**Các quy tắc trích xuất chi tiết:**
(Chèn các quy tắc đã được tạo ở trên vào đây)

---
***BẮT ĐẦU TRÍCH XUẤT***
Bây giờ, hãy phân tích tài liệu PDF đã cung cấp và trả về dữ liệu JSON theo các hướng dẫn trên.
---