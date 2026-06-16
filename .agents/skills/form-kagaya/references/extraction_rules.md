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
- Trích xuất từ mục "工事名" trên PDF đơn hàng kết hợp với thông tin cụ thể ở dòng chi tiết đầu tiên để lấy tên công trình đầy đủ nhất.
- **QUY TẮC CHUẨN HÓA BẮT BUỘC**:
  1. Loại bỏ khoảng trắng dư thừa sau chữ `(仮称)`. Ví dụ: `(仮称) イオンモール郡山新築工事` -> `(仮称)イオンモール郡山新築工事`.
  2. Lấy tên công trình đầy đủ của dòng chi tiết đầu tiên để điền vào `header.工事名` (bao gồm cả hậu tố như `大梁現場溶接用 Ｂ３工区・２ＦＬ分`).
  3. Chuyển đổi toàn bộ các ký tự chữ cái và chữ số tiếng Anh bán sỉ (half-width, ví dụ: `B3`, `2FL`, `RFL`) thành ký tự toàn sỉ (full-width, ví dụ: `Ｂ３`, `２ＦＬ`, `ＲＦＬ`) để khớp chính xác dữ liệu ERP.


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
- Chỉ trích xuất giá trị số từ cột "長さ" cho loại sản phẩm "FB" (thép tấm dẹt).
- Đối với tất cả các loại sản phẩm khác (ST, EX, AP, 特AP, CR-F, B-180, B-120) -> Gán giá trị là `null` (vì chiều dài được tích hợp trong kích thước hoặc không nhập trên dòng ERP).

■ 員数 (Số lượng)
- Trích xuất chính xác số lượng từ cột số lượng ("本数", "数量" hoặc "個数") của sản phẩm trên PDF.
- KHÔNG tự động chia dòng hay thay đổi số lượng dựa trên quy cách đóng gói (ERP sẽ tự tính số thùng/lẻ).

■ product_title
- Nếu loại sản phẩm `product_type` là `"FB"` hoặc `"特AP"` -> Gán giá trị là `null`.
- Nếu loại sản phẩm là `"ST"`, `"EX"`, hoặc `"AP"` -> Gán giá trị cố định là `"エンドタブ"` (chữ Katakana toàn chiều rộng chính xác: `エンドタブ`).
- Nếu loại sản phẩm là `"B-180"` hoặc `"B-120"` -> Gán giá trị cố định là `"蝶番"`.
- Các trường hợp khác -> Gán giá trị mặc định là `null`.

■ product_type (Loại sản phẩm)
- Nhận diện loại sản phẩm dựa trên tên/ký hiệu:
  * Nếu là thép tấm dẹt -> `"FB"`
  * Nếu là thép dẹt bo tròn đầu (có R ở cột R hoặc ký hiệu R trong bản vẽ, ví dụ: 15.5R) -> `"CR-F"`
  * Nếu là End Tab loại ST (hoặc ghi `モX` / `モ` / `ST`) -> `"ST"`
  * Nếu là End Tab loại EX -> `"EX"`
  * Nếu là Apron (AP) -> `"AP"`
  * Nếu là Taredome -> `"特AP"`
  * Nếu là Bản lề dài (Hinge Long) -> `"B-180"` hoặc `"B-120"` (dựa trên ký hiệu B180型 hoặc B120型)

■ product_size (Kích thước)
- Trích xuất và định dạng kích thước tùy theo loại sản phẩm:
  * Nếu là `"ST"` hoặc `"EX"` -> Định dạng `[dày]X[góc]°` (ví dụ: `12X35°`, `16X35°`).
  * Nếu là `"AP"` -> Định dạng `[dày]X[rộng]X[dài]` (ví dụ: `12X38X50`, `16X38X50`).
  * Nếu là `"特AP"` -> Định dạng `[dày]X[rộng]XL1` (ví dụ: `4.5X25XL1`, `9X25XL1`).
  * Nếu là `"CR-F"` -> Định dạng `[dày]X[rộng]X[dài]` (ví dụ: `9X25X155` dựa trên độ dày, chiều rộng bản vẽ FB-9*25 và chiều dài 155).
  * Nếu là `"FB"` hoặc Bản lề (`"B-180"`, `"B-120"`) -> Gán giá trị là `null`.

■ col_maker (Nhà sản xuất)
- Nếu loại sản phẩm là `"FB"`, `"特AP"`, `"B-180"`, hoặc `"B-120"` -> Gán giá trị là `null`.
- Các trường hợp khác: Kiểm tra các từ khóa xuất hiện trên PDF để gán mã nhà sản xuất:
  * Có chữ `日鉄`, `共栄` và category là BCR -> `"NS-R"`; category là BCP -> `"NS-P"`.
  * Có chữ `知多` -> `"JFE-W"`.
  * Có chữ `丸一` -> `"ﾏﾙｲﾁ"`.
  * Nếu không có thông tin nhà sản xuất cụ thể -> `"ｺｳｶﾝ"`.

■ mat_size
- Nếu loại sản phẩm là `"FB"` -> Đặt là `"FB"`. Các trường hợp khác đặt là `null`.

■ category_small
- Nếu loại sản phẩm là `"CR-F"` -> Đặt là `"CR-F"`.
- Nếu dòng sản phẩm có ghi chữ BCR -> `"BCR"`; có chữ BCP -> `"BCP"`. Nếu không có thông tin -> `null`.

■ is_processing
- Nếu loại sản phẩm `product_type` là `"特AP"` (Taredome) -> LUÔN LUÔN gán giá trị là `true`.
- Nếu sản phẩm có góc gia công vát hoặc các ký hiệu gia công bổ sung (ví dụ: góc `14°`, `35°`, hoặc ký hiệu vát cạnh như `RF0`, `TP14°` ở cột 角度/タイプ) -> Gán giá trị là `true`.
- Các trường hợp khác: Mặc định đặt là `false` (hoặc `0`).

■ 工事名 (Tên công trình) ở dòng chi tiết (items)
- Trích xuất tên công trình cụ thể cho từng dòng sản phẩm dựa trên thông tin trên dòng đó hoặc bản vẽ/ghi chú đi kèm.
- **QUY TẮC CHUẨN HÓA BẮT BUỘC**:
  1. Loại bỏ khoảng trắng dư thừa sau chữ `(仮称)`. Ví dụ: `(仮称) イオンモール郡山新築工事` -> `(仮称)イオンモール郡山新築工事`.
  2. Chuyển đổi toàn bộ các ký tự chữ cái và chữ số tiếng Anh bán sỉ (half-width, ví dụ: `B3`, `2FL`, `RFL`) thành ký tự toàn sỉ (full-width, ví dụ: `Ｂ３`, `２ＦＬ`, `ＲＦＬ`).
  3. Đảm bảo ghép đúng tên công trình chính với phần mô tả khu vực/tầng cụ thể của dòng sản phẩm (ví dụ: `(仮称)イオンモール郡山新築工事 大梁現場溶接用 Ｂ３工区・２ＦＬ分`).

