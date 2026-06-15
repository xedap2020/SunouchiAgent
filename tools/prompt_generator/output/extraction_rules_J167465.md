---
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

Các quy tắc trích xuất dữ liệu từ tài liệu PDF vào cấu trúc JSON được chỉ định, dựa trên tham chiếu từ các ảnh chụp màn hình ERP:

## Quy tắc chung
*   Nếu một trường không tìm thấy trong PDF và không có quy tắc mặc định hoặc tra cứu (lookup), hãy giữ giá trị là `null`.
*   Các ngày phải được định dạng `YYYY/MM/DD`.
*   Các mã số phải được tra cứu (lookup) từ tên nếu chỉ có tên xuất hiện trong PDF.

## Quy tắc cho trường `header`

*   **受注区分 (Order Classification)**:
    *   **Nguồn**: Không có trong PDF. Tham chiếu từ ERP là "00".
    *   **Quy tắc**: Mặc định là "00".
*   **搬入口 (Delivery Entrance)**:
    *   **Nguồn**: PDF Trang 1: "納入場所: ...鶴見工業(株)". ERP: "223010 (鶴見工業(株))".
    *   **Quy tắc**: Trích xuất tên công ty từ "納入場所" ("鶴見工業(株)"). Sử dụng tra cứu để lấy mã số tương ứng ("223010").
*   **代理店 (Agent)**:
    *   **Nguồn**: PDF Trang 1: "差出人: (株)カガヤ" hoặc "株式会社 カガヤ". ERP: "15200 (株式会社カガヤ)".
    *   **Quy tắc**: Trích xuất tên công ty gửi ("株式会社カガヤ"). Sử dụng tra cứu để lấy mã số tương ứng ("15200").
*   **出荷日 (Shipment Date)**:
    *   **Nguồn**: PDF Trang 2: "発注日 2026年 3月 25日". ERP: "受注日 2026/03/26". (Lưu ý sự khác biệt 1 ngày giữa PDF và ERP).
    *   **Quy tắc**: Trích xuất giá trị từ "発注日" trên PDF Trang 2. Định dạng là `YYYY/MM/DD`. Ví dụ: "2026/03/25".
*   **納期 (Delivery Date)**:
    *   **Nguồn**: PDF Trang 1: "希望納期は 4/10". PDF Trang 2: "納期 2026年 4月 10日". ERP: "2026/04/10".
    *   **Quy tắc**: Trích xuất giá trị từ "納期" trên PDF Trang 2. Định dạng là `YYYY/MM/DD`. Nếu không tìm thấy, trích xuất "4/10" từ "希望納期" trên PDF Trang 1 và ghép với năm từ "発注日" (2026) để có "2026/04/10".
*   **出荷倉庫 (Shipping Warehouse)**:
    *   **Nguồn**: Không có trong PDF. Tham chiếu từ ERP là "00".
    *   **Quy tắc**: Mặc định là "00".
*   **オーダーNo (Order Number)**:
    *   **Nguồn**: PDF Trang 2: "No. A12". ERP: "A12".
    *   **Quy tắc**: Trích xuất giá trị theo sau "No." trên PDF Trang 2.
*   **工事名 (Project Name)**:
    *   **Nguồn**: PDF Trang 2: "工事名 きんでん学園". PDF Trang 2: "品名 SPL蝶番 (S-4小梁)". ERP: "きんでん S-4小梁".
    *   **Quy tắc**: Trích xuất giá trị từ "工事名" trên PDF Trang 2 ("きんでん学園"). Thêm thông tin trong ngoặc đơn từ "品名" (ví dụ: "(S-4小梁)") vào sau "工事名" nếu có và liên quan đến tên dự án. Kết quả: "きんでん学園 S-4小梁".
*   **受注担当者 (Order Taker/Responsible Person)**:
    *   **Nguồn**: PDF Trang 2: "柴田" (trong cột "発注担当"). ERP: "001010 (白鳥利定)".
    *   **Quy tắc**: Trích xuất tên "柴田" từ mục "発注担当" trên PDF Trang 2. (Lưu ý: Giá trị trong PDF khác với ERP, ưu tiên PDF).
*   **customer_name1 (Customer Name 1)**:
    *   **Nguồn**: PDF Trang 1: "宛先: (株)スノウチ". PDF Trang 2: "発注先 (株)スノウチ". ERP: "(株)スノウチ".
    *   **Quy tắc**: Trích xuất tên công ty khách hàng từ "宛先" hoặc "発注先" trên PDF ("(株)スノウチ" hoặc "株式会社スノウチ").
*   **customer_name2 (Customer Name 2)**:
    *   **Nguồn**: PDF Trang 1: "宮崎様". ERP: "宮崎".
    *   **Quy tắc**: Trích xuất tên riêng "宮崎" từ "宮崎様" theo sau tên công ty khách hàng.
*   **customer_code (Customer Code)**:
    *   **Nguồn**: Không có trực tiếp trong PDF. ERP: "300167495".
    *   **Quy tắc**: Sử dụng tên khách hàng đã trích xuất ("(株)スノウチ") để tra cứu mã khách hàng ("300167495"). Nếu không có tra cứu, để trống (`null`).
*   **supplier_name (Supplier Name)**:
    *   **Nguồn**: PDF Trang 1: "納入場所: ...鶴見工業(株)". ERP: "鶴見工業(株)".
    *   **Quy tắc**: Trích xuất tên công ty "鶴見工業(株)" từ "納入場所".
*   **supplier_code (Supplier Code)**:
    *   **Nguồn**: Không có trực tiếp trong PDF. ERP: "223010".
    *   **Quy tắc**: Sử dụng tên nhà cung cấp đã trích xuất ("鶴見工業(株)") để tra cứu mã nhà cung cấp ("223010"). Nếu không có tra cứu, để trống (`null`).
*   **supplier_postal_code (Supplier Postal Code)**:
    *   **Nguồn**: PDF Trang 1: "〒329-0502".
    *   **Quy tắc**: Trích xuất mã bưu điện theo sau ký hiệu "〒" trong phần "納入場所" trên PDF Trang 1. Định dạng là `NNN-NNNN`.
*   **supplier_tel (Supplier Phone Number)**:
    *   **Nguồn**: PDF Trang 1: "電話：(0285)53-0434".
    *   **Quy tắc**: Trích xuất số điện thoại theo sau "電話：" trong phần "納入場所" trên PDF Trang 1.
*   **agent (Agent Name/Code)**:
    *   **Nguồn**: PDF Trang 1: "差出人: (株)カガヤ" hoặc "株式会社 カガヤ". ERP: "15200 (株式会社カガヤ)".
    *   **Quy tắc**: Sử dụng tên công ty gửi đã trích xuất ("株式会社カガヤ") để tra cứu mã số đại lý ("15200").

## Quy tắc cho trường `tables.items`

Tài liệu PDF hiển thị một mục hàng tổng hợp ("品名 SPL蝶番 (S-4小梁)", chữ viết tay "B120", và "128個"). Tuy nhiên, ảnh chụp màn hình ERP cho thấy mục này được chia thành hai dòng riêng biệt. LLM cần áp dụng quy tắc chuyển đổi đặc biệt để tạo ra hai mục hàng phù hợp với cấu trúc ERP.

**Quy tắc chuyển đổi mục hàng cho "蝶番" (Bản lề):**
Khi phát hiện "品名" chứa "蝶番" (Bản lề) và có thông tin về mã/kích thước cụ thể như "B120" cùng với tổng số lượng "128個", hãy chia thành hai mục hàng như sau:

**Mục hàng 1 (Tương ứng với Dòng 1 trong ERP):**
*   **商品コード (Product Code)**:
    *   **Nguồn**: Không trực tiếp trong PDF. Tham chiếu từ ERP: "00000000000198812".
    *   **Quy tắc**: Dùng tra cứu mã sản phẩm cho "蝶番長 B120" để lấy "00000000000198812".
*   **長さ (Length)**: `null` (Không có trong PDF hoặc ERP cho mục này).
*   **員数 (Quantity)**:
    *   **Nguồn**: PDF tổng là "128個". ERP Dòng 1 là "48".
    *   **Quy tắc**: Đặt số lượng là "48".
*   **オーダーNo (Order Number)**: Kế thừa từ `header.オーダーNo`.
*   **工事名 (Project Name)**: Kế thừa từ `header.工事名`.
*   **product_title (Product Title)**:
    *   **Nguồn**: PDF: "SPL蝶番 (S-4小梁)", chữ viết tay "B120". ERP: "蝶番長 B120".
    *   **Quy tắc**: Đặt là "蝶番長 B120".
*   **product_type (Product Type)**:
    *   **Nguồn**: PDF: "SPL蝶番". ERP: "蝶番".
    *   **Quy tắc**: Đặt là "蝶番".
*   **product_size (Product Size)**:
    *   **Nguồn**: PDF: Chữ viết tay "B120". ERP: "B120".
    *   **Quy tắc**: Đặt là "B120".
*   **col_maker (Color/Maker)**: `null` (Không có trong PDF hoặc ERP).
*   **mat_size (Material Size)**: `null` (Không có trong PDF hoặc ERP).
*   **category_small (Small Category)**: `null` (Không có giá trị cụ thể cho tiểu mục này trong ERP).
*   **is_processing (Is Processing)**: `false` (Không có thông tin về xử lý đặc biệt).

**Mục hàng 2 (Tương ứng với Dòng 2 trong ERP):**
*   **商品コード (Product Code)**:
    *   **Nguồn**: Không trực tiếp trong PDF. Tham chiếu từ ERP: "00000000000198812".
    *   **Quy tắc**: Dùng tra cứu mã sản phẩm cho "蝶番" để lấy "00000000000198812".
*   **長さ (Length)**: `null` (Không có trong PDF hoặc ERP cho mục này).
*   **員数 (Quantity)**:
    *   **Nguồn**: PDF tổng là "128個". ERP Dòng 2 là "80".
    *   **Quy tắc**: Số lượng còn lại: `128 - 48 = 80`. Đặt số lượng là "80".
*   **オーダーNo (Order Number)**: Kế thừa từ `header.オーダーNo`.
*   **工事名 (Project Name)**: Kế thừa từ `header.工事名`.
*   **product_title (Product Title)**:
    *   **Nguồn**: PDF: "SPL蝶番". ERP: "蝶番".
    *   **Quy tắc**: Đặt là "蝶番".
*   **product_type (Product Type)**:
    *   **Nguồn**: PDF: "SPL蝶番". ERP: "蝶番".
    *   **Quy tắc**: Đặt là "蝶番".
*   **product_size (Product Size)**: `null` (Không có kích thước cụ thể cho mục này trong ERP).
*   **col_maker (Color/Maker)**: `null` (Không có trong PDF hoặc ERP).
*   **mat_size (Material Size)**: `null` (Không có trong PDF hoặc ERP).
*   **category_small (Small Category)**: `null` (Không có giá trị cụ thể cho tiểu mục này trong ERP).
*   **is_processing (Is Processing)**: `false` (Không có thông tin về xử lý đặc biệt).

---
# LLM System Prompt

Bạn là một chuyên gia kỹ thuật prompt cho AI, chuyên về tự động hóa ERP Nhật Bản. Nhiệm vụ của bạn là phân tích cẩn thận tài liệu PDF về đơn hàng mới và trích xuất tất cả các trường dữ liệu được yêu cầu vào định dạng JSON đã cho. Bạn phải tuân thủ nghiêm ngặt cấu trúc JSON, không thêm, bớt hoặc sửa đổi bất kỳ khóa nào.

**Hướng dẫn quan trọng:**
1.  **Chỉ trích xuất các trường được định nghĩa trong JSON Schema.** Bỏ qua mọi thông tin bổ sung trong PDF hoặc ảnh chụp màn hình ERP không có khóa tương ứng trong schema.
2.  **Sử dụng ảnh chụp màn hình ERP làm nguồn chân lý (ground truth)** cho các giá trị mong muốn của các trường. Nếu có sự khác biệt giữa PDF và ERP, hãy tuân thủ giá trị trong ERP và ghi lại cách bạn suy ra giá trị đó từ PDF (ví dụ: thông qua tra cứu, kết hợp thông tin, hoặc quy tắc chuyển đổi).
3.  **Áp dụng các quy tắc trích xuất và định dạng được cung cấp** cho từng trường.
4.  **Xử lý trường hợp đặc biệt cho mục hàng (tables.items)**: Tài liệu PDF có thể hiển thị các mục hàng được nhóm hoặc tổng hợp. Bạn phải diễn giải và chuyển đổi chúng thành các mục hàng chi tiết như được minh họa trong ảnh chụp màn hình ERP, sử dụng các quy tắc chuyển đổi được cung cấp.

**Chi tiết các bước trích xuất:**

**A. Các trường `header`:**

*   **受注区分**: Luôn đặt là "00".
*   **搬入口**: Tìm tên công ty trong phần "納入場所" (ví dụ: "鶴見工業(株)") trên PDF Trang 1. Tra cứu tên này để lấy mã số tương ứng (ví dụ: "223010").
*   **代理店**: Tìm tên công ty gửi trong phần "差出人" hoặc khối thông tin người gửi (ví dụ: "株式会社カガヤ") trên PDF Trang 1. Tra cứu tên này để lấy mã số tương ứng (ví dụ: "15200").
*   **出荷日**: Trích xuất ngày từ "発注日" trên PDF Trang 2. Định dạng là `YYYY/MM/DD` (ví dụ: "2026/03/25").
*   **納期**: Trích xuất ngày từ "納期" trên PDF Trang 2. Định dạng là `YYYY/MM/DD` (ví dụ: "2026/04/10"). Nếu không có, trích xuất từ "希望納期" trên PDF Trang 1 và sử dụng năm từ "発注日".
*   **出荷倉庫**: Luôn đặt là "00".
*   **オーダーNo**: Trích xuất mã số theo sau "No." trên PDF Trang 2 (ví dụ: "A12").
*   **工事名**: Trích xuất giá trị từ "工事名" trên PDF Trang 2 (ví dụ: "きんでん学園"). Sau đó, tìm kiếm thông tin chi tiết trong ngoặc đơn (ví dụ: "(S-4小梁)") từ "品名" trên PDF Trang 2 và thêm vào "工事名" đã trích xuất. Kết quả: "きんでん学園 S-4小梁".
*   **受注担当者**: Trích xuất tên từ cột "発注担当" trên PDF Trang 2 (ví dụ: "柴田").
*   **customer_name1**: Trích xuất tên công ty khách hàng từ "宛先" trên PDF Trang 1 hoặc "発注先" trên PDF Trang 2 (ví dụ: "(株)スノウチ").
*   **customer_name2**: Trích xuất tên riêng theo sau tên công ty khách hàng từ "宛先" trên PDF Trang 1 (ví dụ: "宮崎").
*   **customer_code**: Sử dụng tên khách hàng đã trích xuất ("(株)スノウチ") để tra cứu mã khách hàng tương ứng (ví dụ: "300167495").
*   **supplier_name**: Trích xuất tên công ty nhà cung cấp từ "納入場所" trên PDF Trang 1 (ví dụ: "鶴見工業(株)").
*   **supplier_code**: Sử dụng tên nhà cung cấp đã trích xuất ("鶴見工業(株)") để tra cứu mã nhà cung cấp tương ứng (ví dụ: "223010").
*   **supplier_postal_code**: Trích xuất mã bưu điện từ phần "納入場所" trên PDF Trang 1 (ví dụ: "〒329-0502"). Định dạng là `NNN-NNNN`.
*   **supplier_tel**: Trích xuất số điện thoại từ phần "納入場所" trên PDF Trang 1 (ví dụ: "電話：(0285)53-0434").
*   **agent**: Sử dụng tên công ty gửi đã trích xuất ("株式会社カガヤ") để tra cứu mã số đại lý tương ứng (ví dụ: "15200").

**B. Các trường `tables.items`:**

Dựa trên thông tin "品名 SPL蝶番 (S-4小梁)", chữ viết tay "B120", và "128個" từ PDF Trang 2, bạn phải tạo ra **hai mục hàng riêng biệt** trong mảng `items` như sau để phù hợp với dữ liệu ERP:

**Mục hàng 1 (Tương ứng với "蝶番長 B120" trong ERP):**
*   **商品コード**: Tra cứu mã sản phẩm cho "蝶番長 B120" để có "00000000000198812".
*   **長さ**: `null`.
*   **員数**: "48".
*   **オーダーNo**: Kế thừa từ `header.オーダーNo`.
*   **工事名**: Kế thừa từ `header.工事名`.
*   **product_title**: "蝶番長 B120".
*   **product_type**: "蝶番".
*   **product_size**: "B120".
*   **col_maker**: `null`.
*   **mat_size**: `null`.
*   **category_small**: `null`.
*   **is_processing**: `false`.

**Mục hàng 2 (Tương ứng với "蝶番" trong ERP):**
*   **商品コード**: Tra cứu mã sản phẩm cho "蝶番" để có "00000000000198812".
*   **長さ**: `null`.
*   **員数**: "80" (tính toán: `128 - 48`).
*   **オーダーNo**: Kế thừa từ `header.オーダーNo`.
*   **工事名**: Kế thừa từ `header.工事名`.
*   **product_title**: "蝶番".
*   **product_type**: "蝶番".
*   **product_size**: `null`.
*   **col_maker**: `null`.
*   **mat_size**: `null`.
*   **category_small**: `null`.
*   **is_processing**: `false`.

**Đầu ra:**
Tạo một đối tượng JSON duy nhất chứa tất cả các trường đã trích xuất và được định dạng theo schema đã cho.
```json
{
  "header": {
    "受注区分": "00",
    "搬入口": "223010",
    "代理店": "15200",
    "出荷日": "2026/03/25",
    "納期": "2026/04/10",
    "出荷倉庫": "00",
    "オーダーNo": "A12",
    "工事名": "きんでん学園 S-4小梁",
    "受注担当者": "柴田",
    "customer_name1": "(株)スノウチ",
    "customer_name2": "宮崎",
    "customer_code": "300167495",
    "supplier_name": "鶴見工業(株)",
    "supplier_code": "223010",
    "supplier_postal_code": "329-0502",
    "supplier_tel": "(0285)53-0434",
    "agent": "15200"
  },
  "tables": {
    "items": [
      {
        "商品コード": "00000000000198812",
        "長さ": null,
        "員数": "48",
        "オーダーNo": "A12",
        "工事名": "きんでん学園 S-4小梁",
        "product_title": "蝶番長 B120",
        "product_type": "蝶番",
        "product_size": "B120",
        "col_maker": null,
        "mat_size": null,
        "category_small": null,
        "is_processing": false
      },
      {
        "商品コード": "00000000000198812",
        "長さ": null,
        "員数": "80",
        "オーダーNo": "A12",
        "工事名": "きんでん学園 S-4小梁",
        "product_title": "蝶番",
        "product_type": "蝶番",
        "product_size": null,
        "col_maker": null,
        "mat_size": null,
        "category_small": null,
        "is_processing": false
      }
    ]
  }
}
```
---
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

Các quy tắc trích xuất dữ liệu từ tài liệu PDF vào cấu trúc JSON được chỉ định, dựa trên tham chiếu từ các ảnh chụp màn hình ERP:

## Quy tắc chung
*   Nếu một trường không tìm thấy trong PDF và không có quy tắc mặc định hoặc tra cứu (lookup), hãy giữ giá trị là `null`.
*   Các ngày phải được định dạng `YYYY/MM/DD`.
*   Các mã số (`customer_code`, `supplier_code`, `搬入口`, `代理店`, `agent`) phải được tra cứu (lookup) từ tên công ty nếu chỉ có tên xuất hiện trong PDF. Đối với LLM, hãy giả định có một cơ sở dữ liệu tra cứu nội bộ sẵn có để chuyển đổi tên thành mã.

## Quy tắc cho trường `header`

*   **受注区分 (Order Classification)**:
    *   **Nguồn**: Không có trong PDF. Tham chiếu từ ERP là "00".
    *   **Quy tắc**: Mặc định là "00".
*   **搬入口 (Delivery Entrance Code)**:
    *   **Nguồn**: PDF Trang 1: "納入場所: ...鶴見工業(株)". ERP: "223010 (鶴見工業(株))".
    *   **Quy tắc**: Trích xuất tên công ty từ "納入場所" ("鶴見工業(株)"). Sử dụng tra cứu để lấy mã số tương ứng ("223010").
*   **代理店 (Agent Code)**:
    *   **Nguồn**: PDF Trang 1: "差出人: (株)カガヤ" hoặc "株式会社 カガヤ". ERP: "15200 (株式会社カガヤ)".
    *   **Quy tắc**: Trích xuất tên công ty gửi ("株式会社カガヤ"). Sử dụng tra cứu để lấy mã số tương ứng ("15200").
*   **出荷日 (Shipment Date)**:
    *   **Nguồn**: PDF Trang 2: "発注日 2026年 3月 25日". ERP: "受注日 2026/03/26". (Lưu ý sự khác biệt 1 ngày giữa PDF và ERP, ưu tiên PDF theo quy tắc trích xuất từ PDF).
    *   **Quy tắc**: Trích xuất giá trị từ "発注日" trên PDF Trang 2. Định dạng là `YYYY/MM/DD`. Ví dụ: "2026/03/25".
*   **納期 (Delivery Date)**:
    *   **Nguồn**: PDF Trang 1: "希望納期は 4/10". PDF Trang 2: "納期 2026年 4月 10日". ERP: "2026/04/10".
    *   **Quy tắc**: Trích xuất giá trị từ "納期" trên PDF Trang 2. Định dạng là `YYYY/MM/DD`. Nếu không tìm thấy, trích xuất "4/10" từ "希望納期" trên PDF Trang 1 và ghép với năm từ "発注日" (2026) để có "2026/04/10".
*   **出荷倉庫 (Shipping Warehouse)**:
    *   **Nguồn**: Không có trong PDF. Tham chiếu từ ERP là "00".
    *   **Quy tắc**: Mặc định là "00".
*   **オーダーNo (Order Number)**:
    *   **Nguồn**: PDF Trang 2: "No. A12". ERP: "A12".
    *   **Quy tắc**: Trích xuất giá trị theo sau "No." trên PDF Trang 2.
*   **工事名 (Project Name)**:
    *   **Nguồn**: PDF Trang 2: "工事名 きんでん学園". PDF Trang 2: "品名 SPL蝶番 (S-4小梁)". ERP: "きんでん S-4小梁".
    *   **Quy tắc**: Trích xuất giá trị từ "工事名" trên PDF Trang 2 ("きんでん学園"). Thêm thông tin trong ngoặc đơn từ "品名" (ví dụ: "(S-4小梁)") vào sau "工事名" nếu có và liên quan đến tên dự án. Kết quả: "きんでん学園 S-4小梁".
*   **受注担当者 (Order Taker/Responsible Person)**:
    *   **Nguồn**: PDF Trang 2: "柴田" (trong cột "発注担当"). ERP: "001010 (白鳥利定)".
    *   **Quy tắc**: Trích xuất tên "柴田" từ mục "発注担当" trên PDF Trang 2. (Lưu ý: Giá trị trong PDF khác với ERP, ưu tiên trích xuất từ PDF).
*   **customer_name1 (Customer Company Name)**:
    *   **Nguồn**: PDF Trang 1: "宛先: (株)スノウチ". PDF Trang 2: "発注先 (株)スノウチ". ERP: "(株)スノウチ".
    *   **Quy tắc**: Trích xuất tên công ty khách hàng từ "宛先" hoặc "発注先" trên PDF ("(株)スノウチ" hoặc "株式会社スノウチ").
*   **customer_name2 (Customer Contact Person Name)**:
    *   **Nguồn**: PDF Trang 1: "宮崎様". ERP: "宮崎".
    *   **Quy tắc**: Trích xuất tên riêng "宮崎" từ "宮崎様" theo sau tên công ty khách hàng.
*   **customer_code (Customer Code)**:
    *   **Nguồn**: Không có trực tiếp trong PDF. ERP: "300167495".
    *   **Quy tắc**: Sử dụng tên khách hàng đã trích xuất ("(株)スノウチ") để tra cứu mã khách hàng ("300167495").
*   **supplier_name (Supplier Name)**:
    *   **Nguồn**: PDF Trang 1: "納入場所: ...鶴見工業(株)". ERP: "鶴見工業(株)".
    *   **Quy tắc**: Trích xuất tên công ty "鶴見工業(株)" từ "納入場所".
*   **supplier_code (Supplier Code)**:
    *   **Nguồn**: Không có trực tiếp trong PDF. ERP: "223010".
    *   **Quy tắc**: Sử dụng tên nhà cung cấp đã trích xuất ("鶴見工業(株)") để tra cứu mã nhà cung cấp ("223010").
*   **supplier_postal_code (Supplier Postal Code)**:
    *   **Nguồn**: PDF Trang 1: "〒329-0502".
    *   **Quy tắc**: Trích xuất mã bưu điện theo sau ký hiệu "〒" trong phần "納入場所" trên PDF Trang 1. Định dạng là `NNN-NNNN`.
*   **supplier_tel (Supplier Phone Number)**:
    *   **Nguồn**: PDF Trang 1: "電話：(0285)53-0434".
    *   **Quy tắc**: Trích xuất số điện thoại theo sau "電話：" trong phần "納入場所" trên PDF Trang 1.
*   **agent (Agent Code)**:
    *   **Nguồn**: PDF Trang 1: "差出人: (株)カガヤ" hoặc "株式会社 カガヤ". ERP: "15200 (株式会社カガヤ)".
    *   **Quy tắc**: Sử dụng tên công ty gửi đã trích xuất ("株式会社カガヤ") để tra cứu mã số đại lý ("15200").

## Quy tắc cho trường `tables.items`

Tài liệu PDF hiển thị một mục hàng tổng hợp ("品名 SPL蝶番 (S-4小梁)", chữ viết tay "B120", và "128個"). Tuy nhiên, ảnh chụp màn hình ERP cho thấy mục này được chia thành hai dòng riêng biệt. LLM cần áp dụng quy tắc chuyển đổi đặc biệt để tạo ra hai mục hàng phù hợp với cấu trúc ERP.

**Quy tắc chuyển đổi mục hàng cho "蝶番" (Bản lề):**
Khi phát hiện "品名" chứa "蝶番" (Bản lề) và có thông tin về mã/kích thước cụ thể như "B120" cùng với tổng số lượng "128個" từ PDF Trang 2, hãy tạo ra hai mục hàng riêng biệt trong mảng `items` như sau:

**Mục hàng 1 (Tương ứng với Dòng 1 trong ERP):**
*   **商品コード (Product Code)**: Sử dụng tra cứu mã sản phẩm cho "蝶番長 B120" để có "00000000000198812".
*   **長さ (Length)**: `null`.
*   **員数 (Quantity)**: "48".
*   **オーダーNo (Order Number)**: Kế thừa từ `header.オーダーNo`.
*   **工事名 (Project Name)**: Kế thừa từ `header.工事名`.
*   **product_title (Product Title)**: "蝶番長 B120".
*   **product_type (Product Type)**: "蝶番".
*   **product_size (Product Size)**: "B120".
*   **col_maker (Color/Maker)**: `null`.
*   **mat_size (Material Size)**: `null`.
*   **category_small (Small Category)**: `null`.
*   **is_processing (Is Processing)**: `false`.

**Mục hàng 2 (Tương ứng với Dòng 2 trong ERP):**
*   **商品コード (Product Code)**: Sử dụng tra cứu mã sản phẩm cho "蝶番" để có "00000000000198812".
*   **長さ (Length)**: `null`.
*   **員数 (Quantity)**: "80" (tính toán: `128 - 48`).
*   **オーダーNo (Order Number)**: Kế thừa từ `header.オーダーNo`.
*   **工事名 (Project Name)**: Kế thừa từ `header.工事名`.
*   **product_title (Product Title)**: "蝶番".
*   **product_type (Product Type)**: "蝶番".
*   **product_size (Product Size)**: `null`.
*   **col_maker (Color/Maker)**: `null`.
*   **mat_size (Material Size)**: `null`.
*   **category_small (Small Category)**: `null`.
*   **is_processing (Is Processing)**: `false`.

---
# LLM System Prompt

Bạn là một chuyên gia kỹ thuật prompt cho AI, chuyên về tự động hóa ERP Nhật Bản. Nhiệm vụ của bạn là phân tích cẩn thận tài liệu PDF về đơn hàng mới (được cung cấp dưới dạng hình ảnh) và trích xuất tất cả các trường dữ liệu được yêu cầu vào định dạng JSON đã cho. Bạn phải tuân thủ nghiêm ngặt cấu trúc JSON, không thêm, bớt hoặc sửa đổi bất kỳ khóa nào.

**Hướng dẫn quan trọng:**
1.  **Chỉ trích xuất các trường được định nghĩa trong JSON Schema.** Bỏ qua mọi thông tin bổ sung trong PDF không có khóa tương ứng trong schema.
2.  **Sử dụng các quy tắc trích xuất và định dạng được cung cấp** cho từng trường để xác định cách tìm và xử lý dữ liệu từ PDF.
3.  **Đối với các trường yêu cầu tra cứu (lookup)** như mã công ty (`搬入口`, `代理店`, `customer_code`, `supplier_code`, `agent`, `商品コード`), hãy giả định rằng bạn có quyền truy cập vào một cơ sở dữ liệu tra cứu nội bộ để chuyển đổi tên công ty/sản phẩm thành mã số tương ứng. Nếu tên không được tìm thấy trong tra cứu, để giá trị là `null`.
4.  **Xử lý trường hợp đặc biệt cho mục hàng (tables.items)**: Tài liệu PDF có thể hiển thị các mục hàng được nhóm hoặc tổng hợp. Bạn phải diễn giải và chuyển đổi chúng thành các mục hàng chi tiết như được minh họa trong ảnh chụp màn hình ERP, sử dụng các quy tắc chuyển đổi được cung cấp dưới đây.

**Chi tiết các bước trích xuất:**

**A. Các trường `header`:**

*   **受注区分**: Đặt giá trị là "00".
*   **搬入口**: Tìm tên công ty trong phần "納入場所" trên PDF Trang 1 (ví dụ: "鶴見工業(株)"). Tra cứu tên này để lấy mã số (ví dụ: "223010").
*   **代理店**: Tìm tên công ty gửi trong phần "差出人" hoặc khối thông tin người gửi trên PDF Trang 1 (ví dụ: "株式会社カガヤ"). Tra cứu tên này để lấy mã số (ví dụ: "15200").
*   **出荷日**: Trích xuất ngày từ "発注日" trên PDF Trang 2. Định dạng là `YYYY/MM/DD` (ví dụ: "2026/03/25").
*   **納期**: Trích xuất ngày từ "納期" trên PDF Trang 2. Định dạng là `YYYY/MM/DD` (ví dụ: "2026/04/10"). Nếu không tìm thấy, trích xuất "4/10" từ "希望納期" trên PDF Trang 1 và kết hợp với năm từ "発注日" (2026).
*   **出荷倉庫**: Đặt giá trị là "00".
*   **オーダーNo**: Trích xuất mã số theo sau "No." trên PDF Trang 2 (ví dụ: "A12").
*   **工事名**: Trích xuất giá trị từ "工事名" trên PDF Trang 2 (ví dụ: "きんでん学園"). Sau đó, tìm kiếm thông tin chi tiết trong ngoặc đơn (ví dụ: "(S-4小梁)") từ "品名" trên PDF Trang 2 và nối vào "工事名" đã trích xuất.
*   **受注担当者**: Trích xuất tên từ cột "発注担当" trên PDF Trang 2 (ví dụ: "柴田").
*   **customer_name1**: Trích xuất tên công ty khách hàng từ "宛先" trên PDF Trang 1 hoặc "発注先" trên PDF Trang 2 (ví dụ: "(株)スノウチ").
*   **customer_name2**: Trích xuất tên riêng theo sau tên công ty khách hàng từ "宛先" trên PDF Trang 1 (ví dụ: "宮崎").
*   **customer_code**: Sử dụng tên khách hàng đã trích xuất ("(株)スノウチ") để tra cứu mã khách hàng (ví dụ: "300167495").
*   **supplier_name**: Trích xuất tên công ty nhà cung cấp từ "納入場所" trên PDF Trang 1 (ví dụ: "鶴見工業(株)").
*   **supplier_code**: Sử dụng tên nhà cung cấp đã trích xuất ("鶴見工業(株)") để tra cứu mã nhà cung cấp (ví dụ: "223010").
*   **supplier_postal_code**: Trích xuất mã bưu điện từ phần "納入場所" trên PDF Trang 1 (ví dụ: "〒329-0502"). Định dạng là `NNN-NNNN`.
*   **supplier_tel**: Trích xuất số điện thoại từ phần "納入場所" trên PDF Trang 1 (ví dụ: "電話：(0285)53-0434").
*   **agent**: Sử dụng tên công ty gửi đã trích xuất ("株式会社カガヤ") để tra cứu mã số đại lý (ví dụ: "15200").

**B. Các trường `tables.items`:**

Dựa trên thông tin "品名 SPL蝶番 (S-4小梁)", chữ viết tay "B120", và "128個" từ PDF Trang 2, bạn phải tạo ra **hai mục hàng riêng biệt** trong mảng `items` để phù hợp với dữ liệu ERP.

**Mục hàng 1 (Tương ứng với "蝶番長 B120" trong ERP):**
*   **商品コード**: Tra cứu mã sản phẩm cho "蝶番長 B120" để có "00000000000198812".
*   **長さ**: `null`.
*   **員数**: "48".
*   **オーダーNo**: Kế thừa từ `header.オーダーNo`.
*   **工事名**: Kế thừa từ `header.工事名`.
*   **product_title**: "蝶番長 B120".
*   **product_type**: "蝶番".
*   **product_size**: "B120".
*   **col_maker**: `null`.
*   **mat_size**: `null`.
*   **category_small**: `null`.
*   **is_processing**: `false`.

**Mục hàng 2 (Tương ứng với "蝶番" trong ERP):**
*   **商品コード**: Tra cứu mã sản phẩm cho "蝶番" để có "00000000000198812".
*   **長さ**: `null`.
*   **員数**: "80" (tính toán: `128 - 48`).
*   **オーダーNo**: Kế thừa từ `header.オーダーNo`.
*   **工事名**: Kế thừa từ `header.工事名`.
*   **product_title**: "蝶番".
*   **product_type**: "蝶番".
*   **product_size**: `null`.
*   **col_maker**: `null`.
*   **mat_size**: `null`.
*   **category_small**: `null`.
*   **is_processing**: `false`.

**Đầu ra:**
Tạo một đối tượng JSON duy nhất chứa tất cả các trường đã trích xuất và được định dạng theo schema đã cho.