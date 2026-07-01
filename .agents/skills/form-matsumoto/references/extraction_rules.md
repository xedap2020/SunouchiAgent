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
        "matsumoto_customer": null,
        "supplier_name": null,
        "supplier_code": null,
        "supplier_postal_code": null,
        "supplier_tel": null,
        "shipping_warehouse": null,
        "agent": null,
        "matsumoto_agent": null
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

============================================================
RULES (QUY TẮC TRÍCH XUẤT)
============================================================
- CHỈ trả về định dạng JSON hợp lệ. Không kèm văn bản ngoài (markdown). Không thêm chú thích.
- Kết quả đầu ra phải khớp chính xác cấu trúc: {"header": {...}, "tables": {"items": [...]}}
- [Quy tắc quan trọng bắt buộc phải tuân thủ] Loại đơn này nó phân chia các hàng và các cột bằng đường chấm dọc nên bạn phải thật là để ý không được bỏ qua hàng hay cột nào

============================================================
KHÓA SCHEMA NGHIÊM NGẶT (STRICT SCHEMA LOCK)
============================================================
- Giữ nguyên các KEY chính xác như trong schema mẫu.
- KHÔNG thêm/xóa/đổi tên các key.
- Thông tin thiếu hoặc không rõ ràng => gán giá trị null.
- KHÔNG tự ý suy luận giá trị trừ khi có hướng dẫn cụ thể.

[EXPLICIT BLACKLIST - QUAN TRỌNG]
Bạn BẮT BUỘC phải để giá trị `null` cho các trường sau, BẤT KỂ trên PDF ghi gì. KHÔNG trích xuất dữ liệu cho các key này:
- "オーダーNo" ở header PHẢI LÀ null còn "オーダーNo" ở table thì vẫn đọc bình thường.
- "supplier_name" PHẢI LÀ null (Thông tin直送先 phải được đưa vào customer_name2, không được đưa vào supplier_name).
- "supplier_code" PHẢI LÀ null (Mã của直送先 phải đưa vào matsumoto_customer, không được đưa vào supplier_code).
- "supplier_postal_code" PHẢI LÀ null.
- "supplier_tel" PHẢI LÀ null.

============================================================
QUY TẮC TRÍCH XUẤT PHẦN HEADER
============================================================

■ 受注区分
- Trích xuất giá trị từ con dấu viết tay "本受注" ở góc trên bên trái của tài liệu.

■ 搬入口
- Trích xuất giá trị từ cột "担当者名" của hàng sản phẩm ĐẦU TIÊN trong bảng dữ liệu (ví dụ: "岡田様").

■ 代理店
- Trích xuất tên đại lý từ góc trên bên phải hoặc thông tin đại lý trên đơn (ví dụ: "BAO 京滋" hoặc "BAO京滋"). Nếu chỉ thấy mã thì tra cứu hoặc ghép với tên địa phương tương ứng.

■ 出荷日 (Ngày xuất hàng)
- Trường này thường viết tay ở trên đơn, khi viết tay họ sẽ viết tháng và ngày thôi còn năm sẽ là năm hiện tại (năm nay là năm 2026).
- Định dạng nghiêm ngặt: YYYY/MM/DD (ví dụ 2026年7月1日 -> 2026/07/01)

■ 納期 (Ngày giao hàng)
- Trường này thường viết tay ở trên đơn, khi viết tay họ sẽ viết tháng và ngày thôi còn năm sẽ là năm hiện tại (năm nay là năm 2026).
- Định dạng nghiêm ngặt: YYYY/MM/DD (ví dụ 7/2 -> 2026/07/02)
- Nếu trường 納期 không được viết tay ở trên đơn thì trường này sẽ tăng thêm 1 ngày so với 出荷日 (ví dụ: 出荷日 là 2026/07/01 thì 納期 sẽ là 2026/07/02).

■ 出荷倉庫
- Trường này sẽ sử dụng quy tắc trích xuất tương tự như `shipping_warehouse`:
	- Nếu trên form đơn viết là 広 thì 出荷倉庫 sẽ là 東広島倉庫
	- Nếu trên form đơn viết là 本社 thì 出荷倉庫 sẽ là 本社倉庫
	- Nếu trên form đơn viết là ア thì 出荷倉庫 sẽ là 綾瀬倉庫

■ 工事名 (header)
	- Trích xuất từ cột "得意先注番" trong bảng dữ liệu.
	- Bảng sử dụng đường chấm dọc (vertical dotted lines) để phân tách cột, KHÔNG phải khoảng trắng.
	- Chỉ lấy dữ liệu nằm trong phạm vi ranh giới của cột "得意先注番" (ví dụ: "45W6310M").

■ 受注担当者
- Trích xuất tên viết tay (ví dụ "松山咲良") được tìm thấy ở góc trên bên phải hoặc gần thông tin ngày xuất hàng/kho hàng.

■ customer_name1
- Trích xuất tên công ty chính (ví dụ: "マツモト産業株式会社") từ mục "マツモト産業（株）京滋営業所" ở góc trên bên phải, chuẩn hóa hậu tố pháp lý thành "株式会社".

■ customer_name2
- Trích xuất thông tin khách hàng nhận hàng trực tiếp từ phần 直送先 -> 会社名 (ví dụ: "大丸エナウィン(株) 京都支店"). Đảm bảo bảo tồn khoảng trắng nếu có.

■ customer_code
- Gán giá trị mặc định là "400000" cho Matsumoto.

■ matsumoto_customer
- Trích xuất mã số khách hàng (gồm 6 chữ số) nằm gần thông tin 直送先 hoặc góc trên bên phải (ví dụ: "431680").

■ shipping_warehouse
- Dựa vào chữ viết tay trên đơn:
	- Nếu trên form đơn viết là 広 thì shipping_warehouse sẽ là 東広島倉庫
	- Nếu trên form đơn viết là 本社 thì shipping_warehouse sẽ là 本社倉庫
	- Nếu trên form đơn viết là ア thì shipping_warehouse sẽ là 綾瀬倉庫

■ matsumoto_agent (hãng)
- Trích xuất mã số đại lý (gồm 6 chữ số) nằm gần thông tin đại lý hoặc góc trên bên phải (ví dụ: "014201").

■ agent
- Đồng nhất với trường 代理店 (ví dụ: "BAO 京滋").

■ 状況区分, 見積日, 受注日, 失注理由, 受注期限, 回答出荷日, ミルシート, 来月精算, 承認済, 消費税率, 得意先メモ, 納入先メモ, 営業担当者: để null.

============================================================
NHẬN DIỆN DÒNG SẢN PHẨM (ITEM ROW DETECTION)
============================================================
- Một hàng chỉ được tính là tồn tại nếu CẢ 数量 (Số lượng) VÀ/HOẶC 員数 (Số lượng thực) VÀ 単価 (Đơn giá) đều có giá trị.
- Một hàng trên PDF = Một đối tượng JSON.

============================================================
TRÍCH XUẤT THÔNG TIN SẢN PHẨM (PRODUCT META EXTRACTION)
============================================================
■ 商品コード
- Nếu `product_title` của hàng là "運賃", thì `商品コード` sẽ là "0000000000000000001".
- Trong các trường hợp khác, trích xuất chính xác mã hàng từ cột 商品コード. Nếu trống thì để null.

■ product_title
- Trích xuất tên sản phẩm đầy đủ từ cột 品名規格 hoặc 品名 (ví dụ: "ｾﾗﾐｯｸﾀﾌﾞ DF-55", "運賃"). KHÔNG được để null nếu có tên sản phẩm trên PDF.

■ product_type
- Luôn để null cho tất cả các mặt hàng thông thường của Matsumoto, thông tin loại sản phẩm đã nằm trong product_title.

■ product_size
- Luôn để null cho các mặt hàng thông thường của Matsumoto.

■ オーダーNo (Mã đơn hàng)
- Trích xuất từ cột 注番 của hàng. Lưu ý nhận diện ký tự:
  - 3 ký tự đầu thường gồm 2 chữ cái viết hoa và 1 chữ số (ví dụ: "BA0"). Không nhầm chữ "O" thành số "0" hoặc ngược lại ở các vị trí khác, đặc biệt không được nhầm số "0" thành chữ "Z" (ví dụ: "BA0233008001" chứ không phải "BA0Z33080 01").
  - Phải ghép phần mã gốc và số thứ tự dòng ở cột bên cạnh mà không có khoảng trắng.

■ 工事名 (table)
- Trích xuất từ cột "得意先注番" tương ứng của hàng (ví dụ: "45W6310M").
