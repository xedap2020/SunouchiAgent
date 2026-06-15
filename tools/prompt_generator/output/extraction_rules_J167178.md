Dưới đây là kết quả phân tích theo yêu cầu:

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

Các quy tắc chiết xuất dưới đây mô tả cách ánh xạ từng trường từ tài liệu PDF sang cấu trúc JSON mục tiêu, dựa trên thông tin tham chiếu từ các ảnh chụp màn hình hệ thống ERP.

**Quy tắc chung:**
*   **Ưu tiên ERP:** Các giá trị trong ảnh chụp màn hình ERP sẽ được ưu tiên nếu có sự khác biệt giữa PDF và ERP.
*   **Định dạng ngày:** YYYY/MM/DD.
*   **Giá trị mặc định:** Nếu một trường không tìm thấy trong PDF hoặc ERP và không có quy tắc cụ thể, nó sẽ được đặt là `null`.
*   **Chuẩn hóa tên:** Tên công ty sẽ được chuẩn hóa theo định dạng trong ERP nếu có thể (ví dụ: `(株)` thành `株式会社`).

**I. Phần Header:**

1.  **`受注区分`**:
    *   **Nguồn:** Ảnh chụp màn hình ERP, trường "受注区分".
    *   **Giá trị:** "本受注".

2.  **`搬入口`**:
    *   **Nguồn:** Phần "納入場所>" trên PDF P1 ("山善鉄工建設株式会社 第一工場") hoặc từ trường "搬入口" trong ERP.
    *   **Giá trị:** "第一工場".

3.  **`代理店`**:
    *   **Nguồn:** Không có trong PDF hoặc ERP.
    *   **Giá trị:** `null`.

4.  **`出荷日`**:
    *   **Nguồn:** Ảnh chụp màn hình ERP, trường "受注日".
    *   **Giá trị:** "2026/03/24".
    *   **Định dạng:** YYYY/MM/DD.

5.  **`納期`**:
    *   **Nguồn:** Ảnh chụp màn hình ERP, trường "納期".
    *   **Giá trị:** "2026/03/25".
    *   **Định dạng:** YYYY/MM/DD.
    *   *Lưu ý:* Giá trị này ưu tiên ERP, không sử dụng "納入日: 2026年4月5日" từ PDF P2.

6.  **`出荷倉庫`**:
    *   **Nguồn:** Không có trong PDF hoặc ERP.
    *   **Giá trị:** `null`.

7.  **`オーダーNo`**:
    *   **Nguồn:** Từ "件名" hoặc nội dung chính "イオン郡山螺番(S-1)" trên PDF P1, hoặc trường "No." trên PDF P2, hoặc trường "オーダーNo." trong ERP.
    *   **Giá trị:** "S-1".

8.  **`工事名`**:
    *   **Nguồn:** Trường "工事名" trong ERP screenshot. Có thể tham chiếu từ "納入先名" trên PDF P2.
    *   **Giá trị:** "(仮称)イオンモール郡山新築工事 C4工区".

9.  **`受注担当者`**:
    *   **Nguồn:** Trường "受注担当者" trong ERP screenshot.
    *   **Giá trị:** "澤崎芳".

10. **`customer_name1`**:
    *   **Nguồn:** Trường "得意先" trong ERP screenshot ("株式会社カガヤ"). Xác nhận với "差出人" trên PDF P1 ("(株)カガヤ") hoặc "発注先" trên PDF P2 ("(株)カガヤ").
    *   **Giá trị:** "株式会社カガヤ".
    *   **Chuẩn hóa:** Chuyển đổi `(株)` thành `株式会社`.

11. **`customer_name2`**:
    *   **Nguồn:** Không có trong PDF hoặc ERP.
    *   **Giá trị:** `null`.

12. **`customer_code`**:
    *   **Nguồn:** Trường "得意先コード" trong ERP screenshot.
    *   **Giá trị:** "150200".

13. **`supplier_name`**:
    *   **Nguồn:** Trường "納入先" trong ERP screenshot ("山善鉄工建設(株)"). Xác nhận với "納入場所>" trên PDF P1 ("山善鉄工建設株式会社") hoặc "納入先" trên PDF P2.
    *   **Giá trị:** "山善鉄工建設(株)".
    *   **Chuẩn hóa:** Chuyển đổi `株式会社` thành `(株)`.

14. **`supplier_code`**:
    *   **Nguồn:** Trường "納入先コード" trong ERP screenshot.
    *   **Giá trị:** "138010".

15. **`supplier_postal_code`**:
    *   **Nguồn:** Từ phần "納入場所>" trên PDF P1.
    *   **Giá trị:** "〒028-5713".

16. **`supplier_tel`**:
    *   **Nguồn:** Từ phần "納入場所>" trên PDF P1.
    *   **Giá trị:** "0195-27-4151".

17. **`agent`**:
    *   **Nguồn:** Không có trong PDF hoặc ERP.
    *   **Giá trị:** `null`.

**II. Phần Tables (items):**

Ánh xạ từng dòng sản phẩm từ ERP screenshot và thông tin liên quan trong PDF.

**Đối với dòng sản phẩm 1: `螺番長B180` (từ PDF P2 `B180型`):**

1.  **`商品コード`**:
    *   **Nguồn:** Cột "商品コード" trong ERP screenshot.
    *   **Giá trị:** "00000000000198018".
    *   **Quy tắc tra cứu:** Ánh xạ dựa trên `product_type` (`B180型`).

2.  **`長さ`**:
    *   **Nguồn:** Cột "長さ" trong ERP screenshot.
    *   **Giá trị:** `0`.

3.  **`員数`**:
    *   **Nguồn:** Cột "員数" trong ERP screenshot.
    *   **Giá trị:** `4`.
    *   *Lưu ý:* Giá trị này ưu tiên ERP, tương ứng với "4個" trong PDF P2. Mặc dù PDF có "80個/ケース", ERP hiển thị `員数` là `4` và `入数` là `4`, cho thấy đơn vị đặt hàng có thể là "bộ/đơn vị" thay vì số lượng chi tiết thực tế mỗi case.

4.  **`オーダーNo`**:
    *   **Nguồn:** Lấy từ giá trị header `オーダーNo`.
    *   **Giá trị:** "S-1".

5.  **`工事名`**:
    *   **Nguồn:** Lấy từ giá trị header `工事名`.
    *   **Giá trị:** "(仮称)イオンモール郡山新築工事 C4工区".

6.  **`product_title`**:
    *   **Nguồn:** Từ tiêu đề bảng "品名" trên PDF P2.
    *   **Giá trị:** "螺番長".

7.  **`product_type`**:
    *   **Nguồn:** Từ cột "規格" trên PDF P2.
    *   **Giá trị:** "B180型".

8.  **`product_size`**:
    *   **Nguồn:** Từ bản vẽ chi tiết cho `B180型` trên PDF P2 (chiều dài).
    *   **Giá trị:** "180mm".

9.  **`col_maker`**:
    *   **Nguồn:** Không có trong PDF hoặc ERP.
    *   **Giá trị:** `null`.

10. **`mat_size`**:
    *   **Nguồn:** Từ bản vẽ chi tiết và thông tin vật liệu cho `B180型` trên PDF P2.
    *   **Giá trị:** "t=3.7mm, 材質:ハイブ STPG370 15A(S-80) 芯棒:G3503 SWRM8 D=11mm".

11. **`category_small`**:
    *   **Nguồn:** Không có trong PDF hoặc ERP.
    *   **Giá trị:** `null`.

12. **`is_processing`**:
    *   **Nguồn:** Hộp kiểm "加工" trong ERP screenshot cho dòng sản phẩm này.
    *   **Giá trị:** `false` (hộp kiểm không được chọn).

**Đối với dòng sản phẩm 2: `運賃` (Phí vận chuyển - chỉ có trong ERP screenshot):**

1.  **`商品コード`**:
    *   **Nguồn:** Cột "商品コード" trong ERP screenshot.
    *   **Giá trị:** "00000000000198000".

2.  **`長さ`**:
    *   **Nguồn:** Cột "長さ" trong ERP screenshot.
    *   **Giá trị:** `0`.

3.  **`員数`**:
    *   **Nguồn:** Cột "員数" trong ERP screenshot.
    *   **Giá trị:** `1`.

4.  **`オーダーNo`**:
    *   **Nguồn:** Lấy từ giá trị header `オーダーNo`.
    *   **Giá trị:** "S-1".

5.  **`工事名`**:
    *   **Nguồn:** Lấy từ giá trị header `工事名`.
    *   **Giá trị:** "(仮称)イオンモール郡山新築工事 C4工区".

6.  **`product_title`**:
    *   **Nguồn:** Cột "品名" trong ERP screenshot.
    *   **Giá trị:** "運賃".

7.  **`product_type`**:
    *   **Nguồn:** Không có loại cụ thể cho phí vận chuyển.
    *   **Giá trị:** `null`.

8.  **`product_size`**:
    *   **Nguồn:** Không có kích thước cho phí vận chuyển.
    *   **Giá trị:** `null`.

9.  **`col_maker`**:
    *   **Nguồn:** Không có trong PDF hoặc ERP.
    *   **Giá trị:** `null`.

10. **`mat_size`**:
    *   **Nguồn:** Không có thông tin vật liệu/kích thước cho phí vận chuyển.
    *   **Giá trị:** `null`.

11. **`category_small`**:
    *   **Nguồn:** Không có trong PDF hoặc ERP.
    *   **Giá trị:** `null`.

12. **`is_processing`**:
    *   **Nguồn:** Hộp kiểm "加工" trong ERP screenshot cho dòng sản phẩm này.
    *   **Giá trị:** `false` (hộp kiểm không được chọn).

# LLM System Prompt

Bạn là một chuyên gia Kỹ sư Prompt AI chuyên về tự động hóa ERP Nhật Bản. Nhiệm vụ của bạn là phân tích tài liệu PDF mới để trích xuất dữ liệu, tuân thủ chặt chẽ cấu trúc JSON được cung cấp và sử dụng ảnh chụp màn hình hệ thống ERP làm nguồn dữ liệu mặt đất (ground truth) để đối chiếu kết quả đầu vào thực tế.

**Hướng dẫn và Quy tắc trích xuất chi tiết:**

1.  **Mục tiêu:** Trích xuất toàn bộ dữ liệu từ tài liệu PDF (trang 1 và 2) vào cấu trúc JSON được định nghĩa.
2.  **Cấu trúc JSON:** Bạn PHẢI tuân thủ CHÍNH XÁC cấu trúc JSON đã cho, không thêm, bớt hoặc sửa đổi bất kỳ khóa nào. Nếu một trường không có giá trị, hãy đặt là `null`.
3.  **Ưu tiên ERP:** Các giá trị trong ảnh chụp màn hình ERP được xem là dữ liệu mặt đất. Nếu có sự khác biệt giữa PDF và ERP, hãy sử dụng giá trị từ ERP. Đặc biệt chú ý đến:
    *   **Mã (Code):** `customer_code`, `supplier_code`, `商品コード`.
    *   **Ngày tháng:** `出荷日`, `納期`.
    *   **Tên công ty:** `customer_name1`, `supplier_name` (chuẩn hóa theo ERP, ví dụ: `(株)` thành `株式会社` hoặc ngược lại).
    *   **Số lượng:** `員数`.
    *   **Chi tiết dòng sản phẩm:** `商品コード`, `長さ`, `員数`.
4.  **Trường Header:**
    *   `受注区分`: Lấy giá trị "本受注" từ ERP.
    *   `搬入口`: Lấy "第一工場" từ PDF P1 hoặc ERP.
    *   `出荷日`: Lấy từ trường "受注日" của ERP, định dạng YYYY/MM/DD (ví dụ: "2026/03/24").
    *   `納期`: Lấy từ trường "納期" của ERP, định dạng YYYY/MM/DD (ví dụ: "2026/03/25"). Bỏ qua "納入日" trong PDF P2 nếu khác.
    *   `オーダーNo`: Lấy "S-1" từ PDF P1 (`件名` hoặc nội dung) hoặc PDF P2 (`No.`) hoặc ERP.
    *   `工事名`: Lấy từ trường "工事名" của ERP (ví dụ: "(仮称)イオンモール郡山新築工事 C4工区").
    *   `受注担当者`: Lấy từ trường "受注担当者" của ERP (ví dụ: "澤崎芳").
    *   `customer_name1`: Lấy từ trường "得意先" của ERP ("株式会社カガヤ"). Đối chiếu với "差出人" hoặc "発注先" trong PDF.
    *   `customer_code`: Lấy từ trường "得意先コード" của ERP ("150200").
    *   `supplier_name`: Lấy từ trường "納入先" của ERP ("山善鉄工建設(株)"). Đối chiếu với "納入場所>" hoặc "納入先" trong PDF.
    *   `supplier_code`: Lấy từ trường "納入先コード" của ERP ("138010").
    *   `supplier_postal_code`: Lấy mã bưu điện từ "納入場所>" trên PDF P1 (ví dụ: "〒028-5713").
    *   `supplier_tel`: Lấy số điện thoại từ "納入場所>" trên PDF P1 (ví dụ: "0195-27-4151").
    *   Các trường `代理店`, `出荷倉庫`, `customer_name2`, `agent` không có trong PDF/ERP sẽ là `null`.
5.  **Trường Table (`tables.items`):**
    *   Trích xuất tất cả các dòng sản phẩm có trong ERP screenshot. Đối với mỗi dòng:
        *   `商品コード`: Tra cứu từ ERP dựa trên tên sản phẩm (`product_title` hoặc `product_type`).
        *   `長さ`: Lấy từ cột "長さ" của ERP.
        *   `員数`: Lấy từ cột "員数" của ERP.
        *   `オーダーNo`, `工事名`: Lấy lại từ header.
        *   `product_title`: Lấy từ cột "品名" trong PDF P2 hoặc ERP.
        *   `product_type`: Lấy từ cột "規格" trong PDF P2 (ví dụ: "B180型").
        *   `product_size`: Đối với sản phẩm có bản vẽ, trích xuất kích thước chính từ bản vẽ (ví dụ: "180mm" cho `B180型`).
        *   `mat_size`: Trích xuất thông tin vật liệu và kích thước chi tiết từ bản vẽ (ví dụ: "t=3.7mm, 材質:ハイブ STPG370 15A(S-80) 芯棒:G3503 SWRM8 D=11mm").
        *   `is_processing`: Dựa vào trạng thái hộp kiểm "加工" trong ERP screenshot (`true` nếu được chọn, `false` nếu không).
        *   Các trường `col_maker`, `category_small` không có thông tin sẽ là `null`.
    *   Đặc biệt chú ý xử lý dòng `運賃` (Freight) có trong ERP nhưng không rõ ràng trong PDF. Dòng này phải được đưa vào kết quả với các giá trị từ ERP.

Bắt đầu trích xuất dữ liệu từ các trang PDF được cung cấp, sử dụng ảnh chụp màn hình ERP làm nguồn đối chiếu chính xác, và trả về kết quả JSON theo đúng cấu trúc yêu cầu.