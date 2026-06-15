Chào bạn, là một Kỹ sư Prompt AI chuyên về tự động hóa ERP Nhật Bản, tôi đã phân tích các trang PDF và ảnh chụp màn hình ERP bạn cung cấp. Dưới đây là cấu trúc JSON đích, quy tắc trích xuất và System Prompt LLM được yêu cầu.

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

Dưới đây là các quy tắc trích xuất chi tiết từ tài liệu PDF vào cấu trúc JSON đã cho, dựa trên ảnh chụp màn hình ERP làm tham chiếu chính xác cho các giá trị đã được nhập.

**Quy tắc chung:**
*   **Giá trị bị thiếu:** Nếu một trường không xuất hiện rõ ràng hoặc không thể suy ra theo quy tắc cụ thể từ PDF, hãy đặt giá trị là `null`.
*   **Định dạng ngày:** Tất cả các trường ngày phải được định dạng theo `YYYY/MM/DD`.
*   **Loại bỏ ký tự không mong muốn:** Loại bỏ các ký tự như "(株)", "〒", "TEL:", "様" trừ khi được hướng dẫn cụ thể.
*   **Đối với các bảng:** Trích xuất tất cả các dòng mục có thể xác định được.

---
### Header Fields

1.  **`受注区分` (Loại đơn hàng):**
    *   **Mô tả:** Loại tài liệu là Đơn đặt hàng.
    *   **Quy tắc:** Luôn trích xuất là "受注" (Order) cho loại tài liệu này ("発注明細書").
2.  **`搬入口` (Cổng giao hàng):**
    *   **Nguồn PDF:** Trang 1, 4, 6: Trường "納入場所" (Địa điểm giao hàng).
    *   **Quy tắc:** Trích xuất văn bản trong dấu ngoặc đơn từ trường "納入場所".
        *   Ví dụ: Từ "武道工場 (コア組(立)) 千葉宛て" -> "コア組(立)".
3.  **`代理店` (Đại lý):**
    *   **Nguồn PDF:** Trang 1, 4, 6: Trường "発注先" (Bên đặt hàng).
    *   **Quy tắc:** Trích xuất văn bản từ trường "発注先", loại bỏ "(株)".
        *   Ví dụ: Từ "(株)スノウチ" -> "スノウチ".
4.  **`出荷日` (Ngày xuất hàng):**
    *   **Nguồn PDF:** Trang 1, 4, 6: Trường "作成日" (Ngày tạo). (Lưu ý: Theo yêu cầu, ERP "受注日" map to "出荷日", và "受注日" trên ERP trùng với "作成日" trên PDF).
    *   **Quy tắc:** Trích xuất ngày từ trường "作成日". Định dạng thành `YYYY/MM/DD`.
        *   Ví dụ: Từ "2026年 3月 19日" -> "2026/03/19".
5.  **`納期` (Ngày giao hàng):**
    *   **Nguồn PDF:** Trang 1, 4, 6: Trường "納期" (Ngày giao hàng).
    *   **Quy tắc:** Trích xuất ngày từ trường "納期". Định dạng thành `YYYY/MM/DD`.
        *   Ví dụ: Từ "2026年 3月 31日" -> "2026/03/31".
6.  **`出荷倉庫` (Kho xuất hàng):**
    *   **Nguồn PDF:** Không có trường tương ứng rõ ràng trên PDF.
    *   **Quy tắc:** `null`.
7.  **`オーダーNo` (Số đơn hàng):**
    *   **Nguồn PDF:** Trang 1, 4, 6: Trường "No.".
    *   **Quy tắc:** Trích xuất giá trị từ trường "No.".
        *   Ví dụ: Từ "No. S1" -> "S1".
8.  **`工事名` (Tên dự án/công trình):**
    *   **Nguồn PDF:** Trang 1, 4, 6: Trường "工事名" (Tên dự án/công trình).
    *   **Quy tắc:** Trích xuất toàn bộ văn bản từ trường "工事名".
        *   Ví dụ: "メープルツリー北上金ヶ崎 ロジスティクスセンター新築工事".
9.  **`受注担当者` (Người phụ trách đơn hàng):**
    *   **Nguồn PDF:** Trang 2, 3, 5: Từ email hoặc thông tin liên hệ của bên đặt hàng (スノウチ).
    *   **Quy tắc:** Tìm tên người sau "スノウチ" trong phần thông tin liên hệ.
        *   Ví dụ: Từ "株式会社 スノウチ 営業業務部 宮崎" -> "宮崎様" (giữ "様" nếu có trong ngữ cảnh tên người). Trong trường hợp này, ERP chỉ có "宮崎様" nên ta sẽ trích xuất "宮崎様".
10. **`customer_name1` (Tên khách hàng 1):**
    *   **Nguồn PDF:** Trang 1, 4, 6: Tên công ty ở cuối tài liệu.
    *   **Quy tắc:** Trích xuất tên công ty "株式会社カガヤ".
11. **`customer_name2` (Tên khách hàng 2):**
    *   **Nguồn PDF:** Không có trường tương ứng rõ ràng.
    *   **Quy tắc:** `null`.
12. **`customer_code` (Mã khách hàng):**
    *   **Nguồn PDF:** Không có trường tương ứng rõ ràng trên PDF.
    *   **Quy tắc:** `null`.
13. **`supplier_name` (Tên nhà cung cấp/Giao hàng đến):**
    *   **Nguồn PDF:** Trang 1, 4, 6: Phần đầu của trường "納入場所" (Địa điểm giao hàng).
    *   **Quy tắc:** Trích xuất văn bản trước dấu ngoặc đơn đầu tiên từ trường "納入場所".
        *   Ví dụ: Từ "武道工場 (コア組(立)) 千葉宛て" -> "武道工場".
14. **`supplier_code` (Mã nhà cung cấp/Giao hàng đến):**
    *   **Nguồn PDF:** Không có trường tương ứng rõ ràng trên PDF.
    *   **Quy tắc:** `null`.
15. **`supplier_postal_code` (Mã bưu chính nhà cung cấp/Giao hàng đến):**
    *   **Nguồn PDF:** Trang 2, 3, 5: Mã bưu chính liên quan đến địa chỉ của "株式会社 スノウチ".
    *   **Quy tắc:** Trích xuất mã bưu chính từ địa chỉ của "株式会社 スノウチ". Loại bỏ "〒".
        *   Ví dụ: Từ "〒279-0024" -> "279-0024".
16. **`supplier_tel` (Số điện thoại nhà cung cấp/Giao hàng đến):**
    *   **Nguồn PDF:** Trang 2, 3, 5: Số điện thoại liên quan đến "株式会社 スノウチ".
    *   **Quy tắc:** Trích xuất số điện thoại từ thông tin liên hệ của "株式会社 スノウチ". Loại bỏ "TEL: ".
        *   Ví dụ: Từ "TEL: 047-353-8751" -> "047-353-8751".
17. **`agent` (Đại lý (khác)):**
    *   **Nguồn PDF:** Không có trường tương ứng rõ ràng.
    *   **Quy tắc:** `null`.

---
### Table Items

Trích xuất các mục từ bảng chi tiết sản phẩm trên Trang 1, 4, 6.

1.  **`商品コード` (Mã sản phẩm):**
    *   **Nguồn PDF:** Không có trường tương ứng rõ ràng trên PDF. Đây là mã nội bộ ERP.
    *   **Quy tắc:** `null`.
2.  **`長さ` (Chiều dài):**
    *   **Nguồn PDF:** Cột "長さ" trong bảng chi tiết mục.
    *   **Quy tắc:** Trích xuất giá trị số từ cột "長さ".
        *   Ví dụ: "370".
3.  **`員数` (Số lượng):**
    *   **Nguồn PDF:** Cột "本数" (Số lượng miếng) trong bảng chi tiết mục.
    *   **Quy tắc:** Trích xuất giá trị số từ cột "本数".
        *   Ví dụ: "2".
4.  **`オーダーNo` (Số đơn hàng):**
    *   **Quy tắc:** Kế thừa giá trị từ trường `header.オーダーNo`.
        *   Ví dụ: "S1".
5.  **`工事名` (Tên dự án/công trình (mục)):**
    *   **Nguồn PDF:** Không có trường tương ứng trực tiếp cho mục này, giá trị trong ERP được tổng hợp từ nhiều nguồn.
    *   **Quy tắc:** `null`. (Lưu ý: `product_type` và `product_title` sẽ nắm bắt các chi tiết cụ thể về sản phẩm).
6.  **`product_title` (Tên sản phẩm):**
    *   **Nguồn PDF:** Biểu đồ trên Trang 1, 4, 6, có chữ "FB-9*25".
    *   **Quy tắc:** Trích xuất chuỗi "FB-9*25" từ biểu đồ.
        *   Ví dụ: "FB-9*25".
7.  **`product_type` (Loại sản phẩm):**
    *   **Nguồn PDF:** Trường "品名" (Tên sản phẩm) trong bảng chi tiết mục.
    *   **Quy tắc:** Trích xuất phần mô tả loại từ "品名".
        *   Ví dụ: Từ "3節柱仕ロ・ワラ当 (※材料工区①)" -> "3節柱仕ロ". (Chấp nhận "仕ロ" thay vì "仕口" nếu đó là văn bản trên PDF).
8.  **`product_size` (Kích thước sản phẩm):**
    *   **Nguồn PDF:** Biểu đồ trên Trang 1, 4, 6, có chữ "FB-9*25".
    *   **Quy tắc:** Trích xuất giá trị số sau dấu "*" từ văn bản "FB-9*25" trong biểu đồ.
        *   Ví dụ: "25".
9.  **`col_maker` (Nhà sản xuất/Chất liệu):**
    *   **Nguồn PDF:** Cột "材質" (Vật liệu) trong bảng chi tiết mục.
    *   **Quy tắc:** Trích xuất giá trị từ cột "材質".
        *   Ví dụ: "SN490B".
10. **`mat_size` (Kích thước vật liệu):**
    *   **Nguồn PDF:** Cột "長さ" (Chiều dài) trong bảng chi tiết mục.
    *   **Quy tắc:** Trích xuất giá trị số từ cột "長さ".
        *   Ví dụ: "370".
11. **`category_small` (Danh mục nhỏ):**
    *   **Nguồn PDF:** Không trực tiếp trên PDF cho mục. Được suy ra từ "代理店".
    *   **Quy tắc:** Kết hợp "D" với giá trị từ `header.代理店` (đã loại bỏ "(株)").
        *   Ví dụ: "D" + "スノウチ" -> "Dスノウチ".
12. **`is_processing` (Đang xử lý):**
    *   **Nguồn PDF:** Không có trường tương ứng rõ ràng.
    *   **Quy tắc:** Giá trị mặc định là `false`.

---
# LLM System Prompt

Bạn là một chuyên gia Kỹ sư Prompt AI chuyên về tự động hóa hệ thống ERP Nhật Bản. Nhiệm vụ của bạn là phân tích cẩn thận các trang PDF của một tài liệu đặt hàng mới và trích xuất dữ liệu thô vào định dạng JSON. Bạn phải tuân thủ nghiêm ngặt cấu trúc JSON được cung cấp, không được thêm, xóa hoặc sửa đổi bất kỳ khóa nào. Sử dụng ảnh chụp màn hình hệ thống ERP làm tài liệu tham khảo chính xác cho các giá trị đã được nhập.

**Hướng dẫn chi tiết:**

1.  **Phân tích tài liệu PDF:**
    *   Xem xét tất cả các trang PDF được cung cấp (Trang 1-6).
    *   Xác định mục đích chính của tài liệu (ví dụ: Đơn đặt hàng).

2.  **Định dạng đầu ra JSON:**
    *   Kết quả đầu ra phải là một đối tượng JSON duy nhất tuân thủ chính xác `Target JSON Schema` đã cung cấp.
    *   Tất cả các khóa JSON phải khớp chính xác với schema, bao gồm cả chữ hoa/thường và tiếng Nhật.

3.  **Trích xuất trường Header:**
    *   Tìm và trích xuất dữ liệu cho từng khóa trong phần `header` của JSON.
    *   **Định dạng ngày:** Đảm bảo tất cả các giá trị ngày được định dạng là `YYYY/MM/DD`.
    *   **`受注区分`:** Luôn đặt là "受注".
    *   **`搬入口`:** Trích xuất văn bản trong dấu ngoặc đơn từ trường "納入場所" (ví dụ: "(コア組(立))" -> "コア組(立)").
    *   **`代理店`:** Trích xuất văn bản từ trường "発注先", loại bỏ "(株)".
    *   **`出荷日`:** Trích xuất ngày từ trường "作成日".
    *   **`納期`:** Trích xuất ngày từ trường "納期".
    *   **`出荷倉庫`:** Không có trên PDF. Đặt là `null`.
    *   **`オーダーNo`:** Trích xuất giá trị từ trường "No.".
    *   **`工事名` (Header):** Trích xuất toàn bộ văn bản từ trường "工事名".
    *   **`受注担当者`:** Trích xuất tên người từ thông tin liên hệ của "株式会社 スノウチ" (ví dụ: "宮崎様").
    *   **`customer_name1`:** Trích xuất tên công ty "株式会社カガヤ" từ cuối tài liệu.
    *   **`customer_name2`:** Không có trên PDF. Đặt là `null`.
    *   **`customer_code`:** Không có trên PDF. Đặt là `null`.
    *   **`supplier_name`:** Trích xuất phần văn bản trước dấu ngoặc đơn đầu tiên từ trường "納入場所".
    *   **`supplier_code`:** Không có trên PDF. Đặt là `null`.
    *   **`supplier_postal_code`:** Trích xuất mã bưu chính từ địa chỉ của "株式会社 スノウチ" trên các trang email (loại bỏ "〒").
    *   **`supplier_tel`:** Trích xuất số điện thoại từ thông tin liên hệ của "株式会社 スノウチ" trên các trang email (loại bỏ "TEL: ").
    *   **`agent`:** Không có trên PDF. Đặt là `null`.

4.  **Trích xuất trường Table Items:**
    *   Xác định bảng chi tiết sản phẩm trên các trang PDF (Trang 1, 4, 6).
    *   Đối với mỗi dòng sản phẩm trong bảng, hãy trích xuất dữ liệu cho từng khóa trong `tables.items`.
    *   **`商品コード`:** Không có trên PDF. Đặt là `null`.
    *   **`長さ`:** Trích xuất giá trị số từ cột "長さ".
    *   **`員数`:** Trích xuất giá trị số từ cột "本数".
    *   **`オーダーNo`:** Sử dụng giá trị từ `header.オーダーNo`.
    *   **`工事名` (Item):** Không có trên PDF cho mục. Đặt là `null`.
    *   **`product_title`:** Trích xuất chuỗi "FB-9*25" từ biểu đồ sản phẩm.
    *   **`product_type`:** Trích xuất phần mô tả loại từ trường "品名" (ví dụ: "3節柱仕ロ").
    *   **`product_size`:** Trích xuất giá trị số sau dấu "*" từ "FB-9*25" trong biểu đồ.
    *   **`col_maker`:** Trích xuất giá trị từ cột "材質".
    *   **`mat_size`:** Trích xuất giá trị số từ cột "長さ".
    *   **`category_small`:** Tạo giá trị bằng cách thêm "D" vào trước giá trị `header.代理店` (sau khi đã loại bỏ "(株)"). Ví dụ: "Dスノウチ".
    *   **`is_processing`:** Không có trên PDF. Đặt là `false`.

5.  **Xử lý dữ liệu bị thiếu/không tìm thấy:**
    *   Nếu một trường được yêu cầu không thể tìm thấy hoặc suy ra từ tài liệu PDF dựa trên các quy tắc trên, hãy đặt giá trị của nó là `null` trong JSON.

**Ví dụ về kết quả mong muốn (chỉ để tham khảo cấu trúc, bạn phải trích xuất các giá trị thực tế):**

```json
{
  "header": {
    "受注区分": "受注",
    "搬入口": "コア組(立)",
    "代理店": "スノウチ",
    "出荷日": "2026/03/19",
    "納期": "2026/03/31",
    "出荷倉庫": null,
    "オーダーNo": "S1",
    "工事名": "メープルツリー北上金ヶ崎 ロジスティクスセンター新築工事",
    "受注担当者": "宮崎様",
    "customer_name1": "株式会社カガヤ",
    "customer_name2": null,
    "customer_code": null,
    "supplier_name": "武道工場",
    "supplier_code": null,
    "supplier_postal_code": "279-0024",
    "supplier_tel": "047-353-8751",
    "agent": null
  },
  "tables": {
    "items": [
      {
        "商品コード": null,
        "長さ": "370",
        "員数": "2",
        "オーダーNo": "S1",
        "工事名": null,
        "product_title": "FB-9*25",
        "product_type": "3節柱仕ロ",
        "product_size": "25",
        "col_maker": "SN490B",
        "mat_size": "370",
        "category_small": "Dスノウチ",
        "is_processing": false
      }
    ]
  }
}
```