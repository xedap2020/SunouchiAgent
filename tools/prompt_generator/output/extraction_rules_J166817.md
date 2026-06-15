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

Các quy tắc trích xuất dữ liệu từ tài liệu PDF dựa trên so sánh với dữ liệu đã nhập trong hệ thống ERP:

## 1. Header Fields

*   **`受注区分` (Loại đơn đặt hàng):**
    *   Tìm kiếm trường "処理モード" (Chế độ xử lý) trong hệ thống ERP. Nếu giá trị là "受注" (Đơn đặt hàng), đặt `受注区分` là "受注".
    *   Nếu không tìm thấy trong PDF, giá trị mặc định có thể là "受注" (vì đây là tài liệu đặt hàng mới).
*   **`搬入口` (Cổng giao hàng):**
    *   Tìm kiếm trường "搬入口" trong hệ thống ERP. Giá trị là "100万以上建築工事方式に費用項目".
    *   Đây là một giá trị mặc định hoặc tra cứu liên quan đến `工事名`. Nếu `工事名` là "仙台市役所本庁舎整備 第1期建築工事", đặt giá trị này. Nếu không, đặt `null`. (Không có trực tiếp trong PDF).
*   **`代理店` (Đại lý):**
    *   Không tìm thấy trực tiếp trong PDF. Trong ERP, trường này trống. Đặt là `null`.
*   **`出荷日` (Ngày xuất hàng):**
    *   Trích xuất từ "送信日時" (Thời gian gửi) trên Trang 1 của PDF. Giá trị là `2026年3月17日`.
    *   Chuyển đổi sang định dạng `YYYY/MM/DD`. Ví dụ: `2026/03/17`.
    *   Lưu ý: Trong ERP, trường này được ánh xạ từ "受注日".
*   **`納期` (Ngày giao hàng):**
    *   Trích xuất từ "希望納期は4/3としておりました" trên Trang 2 của PDF hoặc "納期 3/18 16 時までのご注文で 4/2 出荷可能です" trên Trang 1. Ngày xác nhận là `4/3`.
    *   Chuyển đổi sang định dạng `YYYY/MM/DD`. Ví dụ: `2026/04/03`.
*   **`出荷倉庫` (Kho xuất hàng):**
    *   Không tìm thấy trực tiếp trong PDF. Trong ERP, trường này trống. Đặt là `null`.
*   **`オーダーNo` (Số đơn hàng):**
    *   Trích xuất từ "件名" (Chủ đề) trên Trang 1 của PDF, tìm kiếm chuỗi dạng `(FY-X〜Y)`. Sử dụng phần đầu tiên, ví dụ: `FY-5`.
    *   Cũng có thể tìm thấy ở góc trên bên phải của các bảng chi tiết đơn hàng (Trang 3, 4, 5). Ví dụ: "No. FY-5".
*   **`工事名` (Tên công trình):**
    *   Trích xuất từ trường "工事名" trên Trang 3, 4, 5 của PDF. Ví dụ: `仙台市役所本庁舎整備 第1期建築工事`.
*   **`受注担当者` (Người phụ trách đơn hàng):**
    *   Trích xuất từ phần địa chỉ trong email trên Trang 2 của PDF, tìm tên người được nhắc đến, ví dụ: `宮崎様`. Chỉ lấy tên `宮崎`.
    *   (Lưu ý: ERP có thể thêm họ/tên đầy đủ nếu có tra cứu, nhưng từ PDF chỉ trích xuất phần hiển thị).
*   **`customer_name1` (Tên khách hàng 1):**
    *   Trích xuất từ "発注元" (Bên đặt hàng) trên Trang 3 của PDF. Ví dụ: `(株)カガヤ` được chuyển đổi thành `株式会社カガヤ`.
*   **`customer_name2` (Tên khách hàng 2):**
    *   Không tìm thấy trong ERP hoặc PDF. Đặt là `null`.
*   **`customer_code` (Mã khách hàng):**
    *   Không có trực tiếp trong PDF. Đây là mã tra cứu trong ERP dựa trên `customer_name1`. Đặt là `null` cho mục đích trích xuất PDF trực tiếp. (Trong ERP là `150200`).
*   **`supplier_name` (Tên nhà cung cấp):**
    *   Trích xuất từ "納入場所" (Địa điểm giao hàng) trên Trang 3 của PDF, kết hợp với tên công ty. Ví dụ: `武道工場`. Kết hợp với `株式会社カガヤ` thành `株式会社カガヤ 武道工場`.
*   **`supplier_code` (Mã nhà cung cấp):**
    *   Không có trực tiếp trong PDF. Đây là mã tra cứu trong ERP dựa trên `supplier_name`. Đặt là `null` cho mục đích trích xuất PDF trực tiếp. (Trong ERP là `138447`).
*   **`supplier_postal_code` (Mã bưu chính nhà cung cấp):**
    *   Trích xuất từ địa chỉ trong chữ ký email trên Trang 1 của PDF. Ví dụ: `〒028-4131`. Chỉ lấy số `028-4131`.
*   **`supplier_tel` (Số điện thoại nhà cung cấp):**
    *   Trích xuất từ số điện thoại trong chữ ký email trên Trang 1 của PDF. Ví dụ: `019-683-2829`.

## 2. Table Items (`items` array)

Trích xuất từng dòng sản phẩm từ các bảng chi tiết trên Trang 3, 4, 5 của PDF.

**Quy tắc chung cho tất cả các mục:**
*   **`オーダーNo`:** Lấy từ tiêu đề bảng liên quan trên PDF (ví dụ: "No. FY-5" trên Trang 3, "No. FY-6" trên Trang 4, "No. FY-7" trên Trang 5).
*   **`工事名`:** Lấy giá trị từ trường `工事名` trong Header.
*   **`商品コード`:** Không có trực tiếp trong PDF. Đặt là `null` cho mục đích trích xuất PDF trực tiếp. (Đây là mã hệ thống trong ERP).
*   **`col_maker`:** Không có trực tiếp trong PDF hoặc ERP. Đặt là `null`.
*   **`mat_size`:** Không có trực tiếp trong PDF hoặc ERP. Đặt là `null`.
*   **`category_small`:** Không có trực tiếp trong PDF hoặc ERP. Đặt là `null`.
*   **`is_processing` (Có xử lý):** Mặc định là `0` (Không). (Cột "加工" trong ERP luôn là `0`).

**Quy tắc cụ thể cho từng loại bảng sản phẩm:**

### 2.1. Bảng "FB-9*25" (Trang 3, `オーダーNo`: FY-5)
*   **`product_type` (Loại sản phẩm):**
    *   Nếu "符号" (Ký hiệu) bắt đầu bằng `R` (ví dụ: `R210`), đặt là "CR-F".
    *   Nếu không, đặt là "FB".
*   **`product_size` (Kích thước sản phẩm):**
    *   Trích xuất từ tiêu đề phần bảng. Ví dụ: Từ "FB-9*25", lấy `9X25`.
*   **`長さ` (Chiều dài):**
    *   Trích xuất phần số từ cột "符号" (Ký hiệu) của PDF. Ví dụ: Từ "430" lấy `430`, từ "C195" lấy `195`.
*   **`員数` (Số lượng item):**
    *   Trích xuất từ cột thứ ba có số (ghi là "C/R" hoặc không có tiêu đề) trong PDF.
*   **`product_title` (Tiêu đề sản phẩm):**
    *   Kết hợp `<product_type> <product_size>X<長さ_từ_ký_hiệu>`. Ví dụ: "FB 9X 25X430" hoặc "CR-F 9X 25X210".

### 2.2. Bảng "スチールタブ (EX)" và "スチールタブ (EXミニ)" (Trang 4, `オーダーNo`: FY-6)
*   **`product_type` (Loại sản phẩm):**
    *   Nếu giá trị cột "t" là `12`, đặt là "エﾝﾄﾞﾀﾌﾞ ST".
    *   Nếu không, đặt là "エﾝﾄﾞﾀﾌﾞ EX".
*   **`product_size` (Kích thước sản phẩm):**
    *   Kết hợp từ cột "t" và "θ°". Ví dụ: `<t>X<θ°>`, như "12X35°" hoặc "19X35°".
*   **`長さ` (Chiều dài):**
    *   Luôn đặt là `0`. (Theo ERP).
*   **`員数` (Số lượng item):**
    *   Trích xuất từ cột "個数" (Số lượng) của PDF, sau đó nhân với `2`. Ví dụ: Nếu "個数" là `5`, thì "員数" là `10`.
*   **`product_title` (Tiêu đề sản phẩm):**
    *   Kết hợp `<product_type> <product_size>`. Ví dụ: "エﾝﾄﾞﾀﾌﾞ ST 12X35°" hoặc "エﾝﾄﾞﾀﾌﾞ EX 19X35°".

### 2.3. Bảng "エプロン (APRON)" (Trang 5, `オーダーNo`: FY-7)
*   **`product_type` (Loại sản phẩm):**
    *   Đặt là "エﾌﾟﾛﾝ AP".
*   **`product_size` (Kích thước sản phẩm):**
    *   Kết hợp từ cột "t" và "L". Ví dụ: `<t>X<L>`, như "28X50" hoặc "36X50".
*   **`長さ` (Chiều dài):**
    *   Trích xuất từ cột "L" của PDF.
*   **`員数` (Số lượng item):**
    *   Trích xuất từ cột "個数" (Số lượng) của PDF.
*   **`product_title` (Tiêu đề sản phẩm):**
    *   Kết hợp `<product_type> <product_size>X<員数>`. Ví dụ: "エﾌﾟﾛﾝ AP 28X50X130" hoặc "エﾌﾟﾛﾝ AP 36X50X10".

### 2.4. Bảng "垂れ止め" (Trang 5, `オーダーNo`: FY-7)
*   **`product_type` (Loại sản phẩm):**
    *   Đặt là "特AP".
*   **`product_size` (Kích thước sản phẩm):**
    *   Trích xuất từ định dạng `FB-<size_part1>x<size_part2>` trong cột đầu tiên của PDF. Ví dụ: Từ "FB-4.5x32", lấy `4.5X32`.
*   **`長さ` (Chiều dài):**
    *   Trích xuất từ cột "個数" (Số lượng) của PDF. (Điều này khác thường nhưng khớp với dữ liệu ERP).
*   **`員数` (Số lượng item):**
    *   Luôn đặt là `0`. (Theo ERP).
*   **`product_title` (Tiêu đề sản phẩm):**
    *   Kết hợp `<product_type> <product_size>X<長さ_từ_個数>`. Ví dụ: "特AP 4.5X32X310".

# LLM System Prompt

Bạn là một chuyên gia kỹ thuật AI Agent Prompt Engineer, chuyên về tự động hóa ERP tiếng Nhật. Nhiệm vụ của bạn là phân tích tài liệu PDF đặt hàng mới và trích xuất thông tin vào định dạng JSON đã định trước.
Bạn phải tuân thủ nghiêm ngặt các quy tắc trích xuất và định dạng được cung cấp.

**Hướng dẫn:**
1.  **Định dạng đầu ra JSON:**
    *   Kết quả đầu ra của bạn phải là một đối tượng JSON hợp lệ, tuân thủ chính xác cấu trúc schema được cung cấp.
    *   Không được thêm, xóa hoặc sửa đổi bất kỳ khóa nào trong schema.
    *   Tất cả các giá trị phải được định dạng chính xác theo các quy tắc bên dưới.
    *   Nếu một trường không được tìm thấy trong tài liệu PDF và không có quy tắc mặc định hoặc tra cứu cụ thể, hãy đặt giá trị là `null`.

2.  **Quy tắc trích xuất Header:**
    *   **`受注区分`**: Đặt là "受注".
    *   **`搬入口`**: Nếu `工事名` là "仙台市役所本庁舎整備 第1期建築工事", đặt là "100万以上建築工事方式に費用項目". Nếu không, đặt `null`.
    *   **`代理店`**: Luôn đặt `null`.
    *   **`出荷日`**: Tìm "送信日時" trên Trang 1. Trích xuất ngày và định dạng `YYYY/MM/DD`. Ví dụ: `2026/03/17`.
    *   **`納期`**: Tìm "希望納期は4/3としておりました" trên Trang 2. Trích xuất ngày và định dạng `YYYY/MM/DD`. Ví dụ: `2026/04/03`.
    *   **`出荷倉庫`**: Luôn đặt `null`.
    *   **`オーダーNo`**: Tìm trong "件名" trên Trang 1 (chuỗi dạng `(FY-X〜Y)`, lấy `FY-X`) hoặc ở tiêu đề bảng trên Trang 3, 4, 5 (ví dụ: "No. FY-5").
    *   **`工事名`**: Tìm "工事名" trên Trang 3. Ví dụ: `仙台市役所本庁舎整備 第1期建築工事`.
    *   **`受注担当者`**: Tìm tên người được nhắc đến trong email trên Trang 2 (ví dụ: `宮崎様`). Chỉ trích xuất tên `宮崎`.
    *   **`customer_name1`**: Tìm "発注元" trên Trang 3. Chuyển đổi `(株)カガヤ` thành `株式会社カガヤ`.
    *   **`customer_name2`**: Luôn đặt `null`.
    *   **`customer_code`**: Luôn đặt `null` (đây là mã tra cứu).
    *   **`supplier_name`**: Kết hợp "納入場所" trên Trang 3 (ví dụ: `武道工場`) với tên công ty `株式会社カガヤ` thành `株式会社カガヤ 武道工場`.
    *   **`supplier_code`**: Luôn đặt `null` (đây là mã tra cứu).
    *   **`supplier_postal_code`**: Tìm mã bưu chính trong chữ ký email trên Trang 1 (ví dụ: `〒028-4131`). Chỉ lấy số `028-4131`.
    *   **`supplier_tel`**: Tìm số điện thoại trong chữ ký email trên Trang 1 (ví dụ: `TEL: 019-683-2829`). Chỉ lấy số `019-683-2829`.

3.  **Quy tắc trích xuất `tables.items`:**
    *   Xác định các bảng sản phẩm riêng biệt trên các Trang 3, 4, 5 dựa trên tiêu đề và cấu trúc của chúng.
    *   Đối với mỗi dòng sản phẩm trong các bảng này, hãy trích xuất các trường sau:
        *   **`オーダーNo`**: Lấy từ tiêu đề bảng mà mục đó thuộc về (ví dụ: "No. FY-5", "No. FY-6", "No. FY-7").
        *   **`工事名`**: Lấy giá trị từ `工事名` trong Header.
        *   **`商品コード`**: Luôn đặt `null`.
        *   **`col_maker`**: Luôn đặt `null`.
        *   **`mat_size`**: Luôn đặt `null`.
        *   **`category_small`**: Luôn đặt `null`.
        *   **`is_processing`**: Luôn đặt `0`.

    *   **Phân tích cụ thể theo loại bảng sản phẩm:**

        *   **Bảng "FB-9*25" (Trang 3, `オーダーNo`: FY-5):**
            *   **`product_type`**: Nếu cột "符号" bắt đầu bằng "R", đặt "CR-F". Ngược lại, đặt "FB".
            *   **`product_size`**: Trích xuất từ tiêu đề phần bảng (ví dụ: "FB-9*25" -> "9X25").
            *   **`長さ`**: Trích xuất phần số từ cột "符号" (ví dụ: "430" -> "430", "C195" -> "195").
            *   **`員数`**: Trích xuất từ cột thứ ba có số (ghi là "C/R" hoặc không có tiêu đề) trong PDF.
            *   **`product_title`**: Kết hợp: `<product_type> <product_size>X<giá trị_長さ_từ_符号>`.

        *   **Bảng "スチールタブ (EX)" và "スチールタブ (EXミニ)" (Trang 4, `オーダーNo`: FY-6):**
            *   **`product_type`**: Nếu giá trị cột "t" là `12`, đặt "エﾝﾄﾞﾀﾌﾞ ST". Ngược lại, đặt "エﾝﾄﾞﾀﾌﾞ EX".
            *   **`product_size`**: Kết hợp từ cột "t" và "θ°" (ví dụ: `<t>X<θ°>`, như "12X35°").
            *   **`長さ`**: Luôn đặt `0`.
            *   **`員数`**: Trích xuất từ cột "個数", sau đó nhân giá trị này với `2`.
            *   **`product_title`**: Kết hợp: `<product_type> <product_size>`.

        *   **Bảng "エプロン (APRON)" (Trang 5, `オーダーNo`: FY-7):**
            *   **`product_type`**: Đặt "エﾌﾟﾛﾝ AP".
            *   **`product_size`**: Kết hợp từ cột "t" và "L" (ví dụ: `<t>X<L>`, như "28X50").
            *   **`長さ`**: Trích xuất từ cột "L".
            *   **`員数`**: Trích xuất từ cột "個数".
            *   **`product_title`**: Kết hợp: `<product_type> <product_size>X<員数>`.

        *   **Bảng "垂れ止め" (Trang 5, `オーダーNo`: FY-7):**
            *   **`product_type`**: Đặt "特AP".
            *   **`product_size`**: Trích xuất từ định dạng `FB-<size_part1>x<size_part2>` trong cột đầu tiên (ví dụ: "FB-4.5x32" -> "4.5X32").
            *   **`長さ`**: Trích xuất từ cột "個数".
            *   **`員数`**: Luôn đặt `0`.
            *   **`product_title`**: Kết hợp: `<product_type> <product_size>X<giá trị_長さ_từ_個数>`.

**Lưu ý quan trọng:** Không trích xuất các mục không có trong PDF, ngay cả khi chúng xuất hiện trong ERP (ví dụ: mục "運賃" trong ERP). Chỉ tập trung vào dữ liệu có thể được suy ra hoặc trực tiếp đọc từ tài liệu PDF.
```