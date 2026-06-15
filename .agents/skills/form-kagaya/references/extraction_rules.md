============================================================
OUTPUT SHAPE (CẤU TRÚC JSON ĐẦU RA BẮT BUỘC)
============================================================
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

============================================================
RULES (QUY TẮC TRÍCH XUẤT TỔNG QUÁT)
============================================================
- CHỈ trả về định dạng JSON hợp lệ. Không kèm văn bản ngoài (markdown). Không thêm chú thích.
- Kết quả đầu ra phải khớp chính xác cấu trúc: {"header": {...}, "tables": {"items": [...]}}

============================================================
KHÓA SCHEMA NGHIÊM NGẶT (STRICT SCHEMA LOCK)
============================================================
- Giữ nguyên các KEY chính xác như trong schema mẫu (bao gồm chữ Kanji "員数").
- KHÔNG thêm/xóa/đổi tên các key.
- Thông tin thiếu hoặc không rõ ràng trên PDF => gán giá trị null.
- KHÔNG tự ý suy luận giá trị hoặc gán cứng đơn giá/số tiền từ ảnh chụp ERP.

[EXPLICIT BLACKLIST - QUAN TRỌNG]
Bạn BẮT BUỘC phải để giá trị `null` cho các trường sau:
- "商品コード" PHẢI LÀ null (trường này sẽ do db_helper tự động tra cứu từ database).
- "受注区分" PHẢI LÀ null.
- "代理店" PHẢI LÀ null.
- "出荷倉庫" PHẢI LÀ null.

============================================================
QUY TẮC TRÍCH XUẤT PHẦN HEADER
============================================================

■ customer_code
- LUÔN LUÔN gán giá trị cố định là `"150200"` (Mã khách hàng của Kagaya).

■ customer_name1
- LUÔN LUÔN gán giá trị cố định là `"株式会社カガヤ"`.

■ customer_name2
- Trích xuất tên riêng của người phụ trách/người gửi nếu có trên email hoặc chữ ký (ví dụ: `宮崎`, `澤口`), nếu không có thì gán `null`.

■ オーダーNo (Mã đơn hàng)
- Trích xuất từ trường "No." ở góc trên của bảng đơn hàng hoặc trong phần email (ví dụ: `A12`, `FY-5`, `S1`, `T25`, `T26`).

■ 工事名 (Tên công trình)
- Trích xuất từ mục "工事名" trên PDF đơn hàng.
- Định dạng: Giữ nguyên văn bản tiếng Nhật gốc (ví dụ: `きんでん学園`).

■ 出荷日 (Ngày xuất hàng)
- Trích xuất ngày gửi đơn hàng từ trường "発注日" hoặc thời gian gửi email trên PDF.
- Định dạng nghiêm ngặt: YYYY/MM/DD.

■ 納期 (Ngày giao hàng)
- Trích xuất từ trường "納期" hoặc "希望納期" trên PDF.
- Định dạng nghiêm ngặt: YYYY/MM/DD.

■ 搬入口 (Nơi nhận hàng)
- Trích xuất từ trường "納入場所" hoặc "搬入口" trên PDF (ví dụ: `武道工場 現寸：西村宛`).

■ supplier_name
- Trích xuất tên nhà xưởng từ mục "納入場所" trên PDF.
- So khớp và chuyển đổi sang dạng tiếng Nhật Katakana/Kanji chuẩn để đối chiếu:
  * Nếu ghi `Ground` hoặc `Ground工場` -> gán `"グラウンド工場"`.
  * Nếu ghi `武道` hoặc `武道工場` -> gán `"武道工場"`.
- Nếu không có thông tin rõ ràng, đặt là `null`.

■ supplier_code, supplier_postal_code, supplier_tel, agent
- Đặt giá trị mặc định là `null`.

============================================================
TRÍCH XUẤT THÔNG TIN SẢN PHẨM (tables.items)
============================================================

■ 長さ (Chiều dài)
- Trích xuất giá trị số từ cột "長さ" hoặc từ ký hiệu sản phẩm (ví dụ: `330`, `380`, `370`).
- Nếu không có thông tin chiều dài cụ thể, đặt là `null`.

■ 員数 (Số lượng)
- Trích xuất chính xác số lượng từ cột số lượng ("本数", "数量" hoặc "個数") của sản phẩm trên PDF.
- KHÔNG tự động chia dòng hay thay đổi số lượng dựa trên quy cách đóng gói (ERP sẽ tự tính số thùng/lẻ).

■ product_title
- Nếu loại sản phẩm `product_type` là `"FB"` (thép tấm dẹt) hoặc `"特AP"` (Taredome) -> Gán giá trị là `null`.
- Các trường hợp khác -> Gán giá trị mặc định là `"Nothing"`.

■ product_type (Loại sản phẩm)
- Nhận diện loại sản phẩm dựa trên tên/ký hiệu:
  * Nếu là thép tấm dẹt -> `"FB"`
  * Nếu ký hiệu bắt đầu bằng R -> `"CR-F"`
  * Nếu là End Tab -> `"エﾝﾄﾞﾀﾌﾞ ST"` hoặc `"エﾝﾄﾞﾀﾌﾞ EX"`
  * Nếu là Apron -> `"エﾌﾟﾛﾝ AP"`
  * Nếu là Taredome -> `"特AP"`

■ product_size (Kích thước)
- Trích xuất kích thước sản phẩm dưới dạng kích thước mặt cắt (ví dụ: `9X25`, `12X35°`, `28X50`).
- Đặc biệt: Nếu loại sản phẩm `product_type` là `"特AP"` (Taredome) -> Gán kích thước dưới dạng `[dày]X[rộng]XL1` (ví dụ: `9X25XL1`).

■ col_maker (Nhà sản xuất)
- Nếu loại sản phẩm `product_type` là `"FB"` (thép tấm dẹt) hoặc `"特AP"` (Taredome) -> Gán giá trị là `null`.
- Các trường hợp khác: Kiểm tra các từ khóa xuất hiện trên PDF để gán mã nhà sản xuất:
  * Có chữ `日鉄`, `共栄` và category là BCR -> `"NS-R"`; category là BCP -> `"NS-P"`.
  * Có chữ `知多` -> `"JFE-W"`.
  * Có chữ `丸一` -> `"ﾏﾙｲﾁ"`.
  * Nếu không có thông tin nhà sản xuất cụ thể -> `"ｺｳｶﾝ"`.

■ mat_size
- Nếu là thép tấm dẹt (FB), đặt là `"FB"`. Các trường hợp khác đặt là `null`.

■ category_small
- Nếu dòng sản phẩm có ghi chữ BCR -> `"BCR"`; có chữ BCP -> `"BCP"`. Nếu không có thông tin -> `null`.

■ is_processing
- Nếu sản phẩm có góc cắt vát hoặc các ký hiệu gia công bổ sung (ví dụ: góc `14°`, `35°`, hoặc ký hiệu vát cạnh như `RF0`, `TP14°`) -> Gán giá trị là `true`.
- Nếu loại sản phẩm `product_type` là `"特AP"` (Taredome) -> LUÔN LUÔN gán giá trị là `true`.
- Các trường hợp khác: Mặc định đặt là `false` (hoặc `0`).
