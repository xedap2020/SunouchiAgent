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
- "product_title" PHẢI LÀ null.
- "オーダーNo" ở header PHẢI LÀ null còn "オーダーNo" ở table thì vẫn đọc bình thường.
- "supplier_postal_code" PHẢI LÀ null.
- "supplier_tel" PHẢI LÀ null.

============================================================
QUY TẮC TRÍCH XUẤT PHẦN HEADER
============================================================

■ 受注区分
- Trích xuất từ con dấu màu đỏ (tròn hoặc chữ nhật) chứa chữ "本受注" hoặc chữ "本" (thường nằm ở góc trên bên trái hoặc ở góc dưới bên trái cạnh các thông tin ngày xuất hàng/ngày giao hàng viết tay). Nếu tìm thấy một trong các dấu này thì gán "本受注", ngược lại gán null.

■ 搬入口
- Trích xuất giá trị từ cột "担当者名" của hàng sản phẩm ĐẦU TIÊN trong bảng dữ liệu.

■ 代理店
- Trích xuất `matsumoto_agent` (ví dụ: "BA0") và nối với " 京滋" để tạo thành giá trị cho trường này (ví dụ: "BA0 京滋").

■ 出荷日 (Ngày xuất hàng)
- Trường này thường viết tay ở trên đơn khi viết tay họ sẽ viết tháng và ngày thôi còn năm sẽ là năm hiện tại (năm nay là năm 2026) 
- Định dạng nghiêm ngặt: YYYY/MM/DD (ví dụ 2026年3月10日 -> 2026/03/10)

■ 納期 (Ngày giao hàng)
- Trường này thường viết tay ở trên đơn khi viết tay họ sẽ viết tháng và ngày thôi còn năm sẽ là năm hiện tại (năm nay là năm 2026) 
- Định dạng nghiêm ngặt: YYYY/MM/DD (ví dụ 3/11 -> 2026/03/11)
- Nếu trong trường hợp mà trường 納期 không được viết tay ở trên đơn thì trường này sẽ tăng thêm 1 ngày so với 出荷日 (ví dụ: 出荷日 là 2026/03/10 thì 納期 sẽ là 2026/03/11)

■ 出荷倉庫
- Trường này sẽ sử dụng quy tắc trích xuất tương tự như `shipping_warehouse`:
	- Nếu trên form đơn viết là 広 thì 出荷倉庫 sẽ là 東広島倉庫
	- Nếu trên form đơn viết là 本社 thì 出荷倉庫 sẽ là 本社倉庫
	- Nếu trên form đơn viết là ア thì 出荷倉庫 sẽ là 綾瀬倉庫

■ 工事名 (header)
	- Trích xuất từ cột "得意先注番" trong bảng dữ liệu.
	- Bảng sử dụng đường chấm dọc (vertical dotted lines) để phân tách cột, KHÔNG phải khoảng trắng.
	- Các đường chấm dọc này là ranh giới cột tuyệt đối. Không được đọc dữ liệu vượt qua ranh giới này.
	- Cột "得意先注番" nằm giữa cột "仕入@" và cột "担当者名".
	- Chỉ lấy dữ liệu nằm trong phạm vi ranh giới của cột "得意先注番".

	[QUY TẮC NGHIÊM NGẶT]
	- KHÔNG được lấy dữ liệu từ cột "仕入@" hoặc "担当者名".
	- KHÔNG suy luận dựa vào khoảng cách chữ.
	- KHÔNG ghép dữ liệu từ cột khác.

	[TRƯỜNG HỢP KHÔNG CÓ DỮ LIỆU]
	- Nếu ô "得意先注番" trống -> trả về null.
	- KHÔNG lấy giá trị từ cột bên cạnh khi ô trống.

	[TRƯỜNG HỢP SỐ CĂN TRÁI]
	- Nếu giá trị trong "得意先注番" là số và căn trái, vẫn phải giữ nguyên cột.
	- KHÔNG nhầm với giá trị số ở cột "仕入@".
	- Chỉ lấy giá trị nằm trong ranh giới của cột "得意先注番".

	[LEFT-RIGHT ALIGNMENT RULE - QUAN TRỌNG]
	- Cột "仕入@" thường chứa số căn phải.
	- Cột "得意先注番" có thể chứa số căn trái.
	- Khi hai giá trị nằm sát nhau, phải tách theo vị trí cột từ header, KHÔNG coi là một chuỗi.

	- Nếu một chuỗi số dài nằm giữa "仕入@" và "担当者名":
		+ Phần bên trái thuộc về "仕入@"
		+ Phần bắt đầu ngay sau ranh giới cột thuộc về "得意先注番"

■ 受注担当者
- Trích xuất tên viết tay "松山咲良" được tìm thấy gần thông tin ngày xuất hàng/kho hàng.

■ customer_name1
- Trích xuất tên công ty chính (ví dụ: "マツモト産業") từ mục "マツモト産業（株）京滋営業所" ở góc trên bên phải.

■ customer_name2
- Trích xuất và mở rộng hậu tố pháp lý (ví dụ: `（株）` thành "株式会社") từ mục "マツモト産業（株）京滋営業所" ở góc trên bên phải.

■ customer_code
- Trường này thì để null.

■ matsumoto_customer
	- Trường này sẽ có quy tắc trích xuất như sau:
		+ Quy tắc trích xuất matsumoto_customer từ 注番:
			-  Lấy 3 ký tự đầu tiên của trường 注番
			- 3 ký tự này có định dạng: 2 chữ cái viết hoa (A-Z) + 1 chữ số (0-9)
			- Lưu ý quan trọng: Ký tự thứ 3 luôn là chữ số, không phải chữ cái. Do đó:
				+ Nếu thấy ký tự giống chữ "O" ở vị trí thứ 3 thì đó là số 0 (không)
				+ Không bao giờ có trường hợp chữ "O" (chữ cái) ở vị trí thứ 3
		+ Ví dụ:
			- 注番 = BE0Z680707 → lấy BE0 (B, E, số 0)
			- 注番 = BD0123456 → lấy BD0 (B, D, số 0)
			- 注番 = AB9XYZ123 → lấy AB9 (A, B, số 9)

■ supplier_name (Địa điểm giao hàng)
Trích xuất từ mục: (直送先) ⇒ 会社名:
BƯỚC 1 — Lấy toàn bộ dòng sau nhãn "会社名:", bỏ qua các ghi chú trong ngoặc đơn như "(仕入)" ở cuối.
BƯỚC 2 — Chuẩn hóa danh xưng công ty:
	株式会社 biến thể: 株式会社, (株), （株）, ㈱  -> Chuyển tất cả thành: (株)
	ĐẢM BẢO giữ nguyên hoặc thêm khoảng trắng sau hậu tố pháp lý (ví dụ: (株)) nếu có các phần tên khác theo sau (ví dụ: "大丸エナウィン(株) 京都支店").
	有限会社 biến thể: 有限会社, (有), （有）, ㈲  -> Chuyển tất cả thành: (有)

■ supplier_code
- trường này thì để null 

■ shipping_warehouse: giá trị của trường này thông thường nó sẽ là chữ viết tay trên form đơn nó có thể viết ở bất kỳ vị trí vào tên đơn nên bạn 
phải tìm thật là kỹ dưới đây là các trường hợp có thể xảy ra: 
	- Nếu trên form đơn viết là 広 thì shipping_warehouse sẽ là 東広島倉庫
	- Nếu trên form đơn viết là 本社 thì shipping_warehouse sẽ là 本社倉庫
	- Nếu trên form đơn viết là ア thì shipping_warehouse sẽ là 綾瀬倉庫

■ matsumoto_agent (hãng)
- Trường này sẽ có quy tắc trích xuất như sau:
	+ Quy tắc trích xuất matsumoto_agent từ 注番:
	-  Lấy 3 ký tự đầu tiên của trường 注番
	- 3 ký tự này có định dạng: 2 chữ cái viết hoa (A-Z) + 1 chữ số (0-9)
	- Lưu ý quan trọng: Ký tự thứ 3 luôn là chữ số, không phải chữ cái. Do đó:
		+ Nếu thấy ký tự giống chữ "O" ở vị trí thứ 3 thì đó là số 0 (không)
		+ Không bao giờ có trường hợp chữ "O" (chữ cái) ở vị trí thứ 3
		+ Ví dụ:
		- 注番 = BE0Z680707 → lấy BE0 (B, E, số 0)
		- 注番 = BD0123456 → lấy BD0 (B, D, số 0)
		- 注番 = AB9XYZ123 → lấy AB9 (A, B, số 9)

■ agent: trường này để null 
■ 状況区分: để null
■ 見積日: để null
■ 受注日: để null
■ 失注理由: để null
■ 受注期限: để null
■ 回答出荷日: để null
■ ミルシート: để null
■ 来月精算: để null
■ 承認済: để null
■ 消費税率: để null
■ 得意先メモ: để null
■ 納入先メモ: để null
■ 営業担当者: để null


============================================================
NHẬN DIỆN DÒNG SẢN PHẨM (ITEM ROW DETECTION)
============================================================
- Một hàng chỉ được tính là tồn tại nếu CẢ 数量 (Số lượng) VÀ 単価 (Đơn giá) đều có giá trị.
- Một hàng trên PDF = Một đối tượng JSON.

============================================================
QUY TẮC ƯU TIÊN TUYỆT ĐỐI (ABSOLUTE PRIORITY RULE)
============================================================
- TUYỆT ĐỐI KHÔNG xác định trường dữ liệu dựa trên định dạng ký tự.
- Gán dữ liệu nghiêm ngặt theo các nhãn mô tả (descriptors). Nếu không có mô tả khớp -> null.

============================================================
TRÍCH XUẤT THÔNG TIN SẢN PHẨM (PRODUCT META EXTRACTION)
============================================================
■ 商品コード
- Hàng cuối cùng trong bảng (sản phẩm cuối cùng, thường là 送料/vận chuyển) hoặc nếu `product_type` của hàng là "運賃", thì `商品コード` mặc định gán là "0000000000000000001".
- Trong các trường hợp khác, nếu ô "商品コード" trên PDF trống, gán giá trị `null`.

■ product_type:
- Trường này thì lấy ở cột 品名規格 trong bảng.
- Nếu 品名規格 chứa "送料", thì `product_type` là "運賃".
- Đối với các trường hợp khác, chỉ lấy các ký tự là chữ cái viết hoa (A-Z), số (0-9) và dấu gạch ngang (-), không lấy tiếng Nhật và các ký tự khác.
- Trường hợp nếu như mà product_type là DC thì product_size chính là kích thước đằng sau nó (VD: DC 1 X 355 thì product_size là 1X355 bạn phải loại bỏ khoảng trắng giữa các ký tự)
- Trong trường hợp mà gặp chữ ガウジング ở cột 品名規格 trên table thì product_type của nó chính là DC luôn còn product_size chính là cái số đằng trước mm (ví dụ: 品名規格 có giá trị là ガウジングカーボン丸型9mm thì product_type là DC và product_size là 9X355)
- Tất cả các mẫu product_type khác có thể gặp: B-120, B-180, VS, VM, VL, VB-55, VB-75, VB-110, VWS, VW, VWB, VM-30, VL-30, VB-5530, VS-4, VM-4, VL-4, VL-25, VB-25, FS, FM, FL, FB-55, FB-75, FB-110, FWS, FW, FWB, FWN-20, FWN-32, FM-30, FL-30, FB-5530, FS-4, FM-4, FL-4, FM-25, FL-25, FB-25, FB-7525, FM-328, FL-340, SC, SC-3T, SC-4T, SC-5, RT-25, A, AW, AW-2, A-50, A-80, A-110, DF-40, DF-55, DF-75, DF-120, CP-40, CP-50, CP-100, YV-25, FMG-28, FHT-30, YHR-25N, YHR-32N, YHR-50N, ND, TR-25, TR-40, VSHD, VLHD, JS, L-1, L-2, LB-12, LB-17, LCB-19, LCB-20, LB-23T, LCB-27T, LCB-29T, LB-46T, RV-3245, RV-3250, RV-3255, SRF-30, SRF-40, CAT-30, NST-1, VW-32R, VW-55R, CAT-16, BPX140-35, IT-50, PSK-50, PSK-503, SS, V-S, V-M, V-L, F-S, F-M, F-L, CBW-30NP, TGW-30L, CBW-G34NP, CBW-F40NP, CBW-271NP, CBW-276NP, CBW-TR90NP, CBW-07φNP, CBW-10φNP, CBW-12φNP, CBW-15φNP, CBW-S01NP, CBW-S02NP, CBW-S03NP, CBW-3C, CBW-36, CBW-J27, CBW-TR901, CBWR300TR, CBWR300G35, CBX-S02, CBX-F30P, CBX-30KG, CBM8067, CBX-WTD16, CBX-WTD41, CBX-WTD51, P-S, P-L, TC-25, TC-40
- Không được tự ý thêm gạch ngang vào để tạo nên product_type ví dụ: FW 32H thì product_type là FW chứ không được thêm - để biến product_type thành FW-32H
- Nếu product_type nằm trong mục Tất cả các mẫu product_type khác có thể gặp thì product_size sẽ là null  

■ オーダーNo (Mã đơn hàng)
- Trường này lấy từ ô 注番 phải lấy luôn cả các cái con số kiểu 01, 02, 03, .... ở ô bên cạnh nữa. Nối giá trị chính và số thứ tự *mà không có bất kỳ khoảng trắng nào* ở giữa (ví dụ: "BA0Z3308001").
- 3 ký tự của trường này nó thường là 2 chữ cái viết hoa cộng với 1 con số nên bạn khôg được nhầm giữa số 0 và chữ O (ví dụ: ABO -> AB0)

■ 工事名 (table)
	- Trích xuất từ cột "得意先注番" trong bảng dữ liệu.
	- Bảng sử dụng đường chấm dọc (vertical dotted lines) để phân tách cột, KHÔNG phải khoảng trắng.
	- Các đường chấm dọc này là ranh giới cột tuyệt đối. Không được đọc dữ liệu vượt qua ranh giới này.
	- Cột "得意先注番" nằm giữa cột "仕入@" và cột "担当者名".
	- Chỉ lấy dữ liệu nằm trong phạm vi ranh giới của cột "得意先注番".

	[QUY TẮC NGHIÊM NGẶT]
	- KHÔNG được lấy dữ liệu từ cột "仕入@" hoặc "担当者名".
	- KHÔNG suy luận dựa vào khoảng cách chữ.
	- KHÔNG ghép dữ liệu từ cột khác.

	[TRƯỜNG HỢP KHÔNG CÓ DỮ LIỆU]
	- Nếu ô "得意先注番" trống -> trả về null.
	- KHÔNG lấy giá trị từ cột bên cạnh khi ô trống.

	[TRƯỜNG HỢP SỐ CĂN TRÁI]
	- Nếu giá trị trong "得意선注番" là số và căn trái, vẫn phải giữ nguyên cột.
	- KHÔNG nhầm với giá trị số ở cột "仕入@".
	- Chỉ lấy giá trị nằm trong ranh giới của cột "得意先注番".

	[LEFT-RIGHT ALIGNMENT RULE - QUAN TRỌNG]
	- Cột "仕入@" thường chứa số căn phải.
	- Cột "得意先注番" có thể chứa số căn trái.
	- Khi hai giá trị nằm sát nhau, phải tách theo vị trí cột từ header, KHÔNG coi là một chuỗi.

	- Nếu một chuỗi số dài nằm giữa "仕入@" và "担当者名":
		+ Phần bên trái thuộc về "仕入@"
		+ Phần bắt đầu ngay sau ranh giới cột thuộc về "得意先注番"

============================================================
CHỐT AN TOÀN DỮ LIỆU (PRODUCT META SAFETY LOCK)
============================================================
- product_type KHÔNG ĐƯỢC trùng với mã sản phẩm (商品コード).
- KHÔNG tự ý suy luận dữ liệu không có sẵn trên PDF.
- KHÔNG kết hợp hoặc "mượn" dữ liệu giữa các hàng khác nhau.
- Nếu không chắc chắn hoặc mơ hồ -> Trả về null.
- 長さ: trong trường hợp product type là FB thì cái 長さ để null 
- 長さ: trong trường hợp đặc biệt product_type là FB và product_size là 12X32X thì 長さ chính là giá trị nằm sau chữ L (ví dụ: 12X32 ... L260 thì 長さ là 260)
============================================================
QUY TẮC VỀ SỐ VÀ VĂN BẢN
============================================================

■ CÁC TRƯỜNG DỮ LIỆU SỐ (員数, 単価):
- Trích xuất giá trị số thô từ các cột tương ứng.
- Kết quả là kiểu Số (Number), không để trong dấu ngoặc kép.
- Loại bỏ dấu phẩy phân cách hoặc ký tự đơn vị (ví dụ: 1,000 -> 1000).

■ BẢO TỒN VĂN BẢN:
- Giữ nguyên văn bản tiếng Nhật (Kanji/Kana) chính xác như trên file.
- Chỉ chuẩn hóa các khoảng trắng thừa.
- KHÔNG diễn giải lại, không dịch, không rút ngắn văn bản.
