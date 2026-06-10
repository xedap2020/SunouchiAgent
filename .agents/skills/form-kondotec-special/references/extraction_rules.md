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
        "customer_code": null,
        "supplier_name": null,
        "supplier_code": null,
        "supplier_postal_code": null,
        "supplier_tel": null,
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
RULES (QUY TẮC TRÍCH XUẤT)
============================================================
- CHỈ trả về định dạng JSON hợp lệ. Không kèm văn bản ngoài (markdown). Không thêm chú thích.
- Kết quả đầu ra phải khớp chính xác cấu trúc: {"header": {...}, "tables": {"items": [...]}}

============================================================
KHÓA SCHEMA NGHIÊM NGẶT (STRICT SCHEMA LOCK)
============================================================
- Giữ nguyên các KEY chính xác như trong schema mẫu.
- KHÔNG thêm/xóa/đổi tên các key.
- Thông tin thiếu hoặc không rõ ràng => gán giá trị null.
- KHÔNG tự ý suy luận giá trị trừ khi có hướng dẫn cụ thể.
- nếu gặp file pdf có nhiều trang thì header lấy data ở cái trang đầu tiên còn items thì phải lấy của tất cả các trang không được bỏ qua trang nào 

[EXPLICIT BLACKLIST - QUAN TRỌNG]
Bạn BẮT BUỘC phải để giá trị `null` cho các trường sau, BẤT KỂ trên PDF ghi gì. KHÔNG trích xuất dữ liệu cho các key này:
- "商品コード" PHẢI LÀ null.
- "product_title" PHẢI LÀ null.
- "受注区分" PHẢI LÀ null.
- "搬入口" PHẢI LÀ null.
- "代理店" PHẢI LÀ null.
- "出荷倉庫" PHẢI LÀ null.
- "受注担当者" PHẢI LÀ null.

============================================================
QUY TẮC TRÍCH XUẤT PHẦN HEADER
============================================================

■ オーダーNo (Mã đơn hàng)
- Trích xuất từ mục "当社注番"

■ 工事名 (Tên công trình)
- Trích xuất linh hoạt dựa trên thứ tự ưu tiên sau (từ cao xuống thấp). Nếu không thỏa mãn bất kỳ điều kiện nào, BẮT BUỘC gán giá trị null.
1. Ưu tiên 1 (Dấu ngoặc định dạng dự án): 
Tìm các chuỗi văn bản nằm trong các dấu ngoặc dạng 【...】 hoặc <...> xuất hiện ở phần Header (thường dưới tên khách hàng/địa chỉ giao hàng). 
- Lấy nội dung bên trong ngoặc VÀ các thông tin hậu tố đi liền ngay sau đó (thường là số tầng, khu vực, cấu kiện như 節, 梁, 工区).
- Ví dụ: 【札幌ダイビル再開発プロジェクト 新築工事】 8節G梁 -> Lấy "札幌ダイビル再開発プロジェクト新築工事 8節 G梁". <(株)SUBARUボディ・トリム棟 (北棟)40工区2節大梁> -> Lấy "(株)ＳＵＢＡＲＵボディ・トリム棟（北棟）４０工区 ２節 大梁".
- LOẠI TRỪ: Bỏ qua nếu nội dung trong ngoặc chỉ là chỉ thị vận chuyển như 【納品先】, 【直送時送り状をFAX...】.
2. Ưu tiên 2 (Từ trường 客先注番): 
Tìm mục "客先注番:" nằm ở phần thông tin bên phải (dưới dòng 当社注番). Nếu có, lấy toàn bộ giá trị sau dấu hai chấm. 
- Ví dụ: 客先注番: 常峰様 -> Lấy "常峰様". 客先注番: 豊前中/一方井様 -> Lấy "豊前中ノ一方井様". 客先注番: 23J-0087 新幹線 -> Lấy "23J-0087 北海道新幹線駅舎新築１（躯体他） ３節" (nếu có thông tin chi tiết hơn ở ngoặc phần địa chỉ, ưu tiên gộp lại).
3. Ưu tiên 3 (Từ chi tiết bảng/Ghi chú): 
Nếu cột 品名・規格・サイズ hoặc cột 備考 có một dòng văn bản độc lập mô tả tên dự án (thường chứa các từ khóa như 計画, 工事, 節, 階, 梁, 仕口分), hãy trích xuất toàn bộ chuỗi đó.
- Ví dụ: "神田錦町計画 5節 R階 小梁".
[QUAN TRỌNG] ĐIỀU KIỆN TRẢ VỀ NULL (CHỐT CHẶN AN TOÀN):
- TUYỆT ĐỐI KHÔNG lấy tên công ty, tên chi nhánh, xưởng, hoặc địa chỉ thông thường (ví dụ: コンドーテック株式会社 九州営業所, (有)桑原鉄工所 第二工場) làm Tên công trình.
- Nếu mục 客先注番 bị trống/không tồn tại, VÀ không có dấu ngoặc 【】/ < > nào chứa tên dự án, VÀ không có từ khóa công trình (工事, 計画, v.v.), thì BẮT BUỘC trả về null.
Quy tắc Chuẩn hóa (BẮT BUỘC nếu có dữ liệu): 
- KHÔNG giữ lại các dấu ngoặc 【 】 hoặc < > trong kết quả cuối cùng.
- Xóa bỏ các ký hiệu đánh dấu thừa (ví dụ: vòng tròn số ①, ②).
- Chuẩn hóa các dấu gạch chéo / thành chữ Katakana ノ nếu tên người có dạng ghép (ví dụ: 豊前中/一方井 -> 豊前中ノ一方井).
- XỬ LÝ GIỚI HẠN ĐỘ DÀI (RẤT QUAN TRỌNG):
	+ Sau khi hoàn tất:
		* Trích xuất
		* Làm sạch dữ liệu
		* Chuẩn hóa
	+ Tính tổng số ký tự của giá trị cuối cùng
	+ Nếu độ dài ≤ 30 ký tự:
		* Giữ nguyên toàn bộ (Latin và số ở dạng full-width)
	+ Nếu độ dài > 30 ký tự:
		* Chuyển TOÀN BỘ chữ cái Latin và chữ số từ Full-width (全角) → Half-width (半角)
		* Giữ nguyên các ký tự tiếng Nhật (Kanji, Hiragana, Katakana) 
		* KHÔNG được cắt chuỗi
		* KHÔNG thay đổi ý nghĩa nội dung
	+ Mục đích:
		* Đảm bảo phù hợp giới hạn ô input tối đa 30 ký tự
		
■ 出荷日 (Ngày xuất hàng)
- trường này sẽ lùi vào 1 ngày so với trường 納期 (VD: 納期 là 2025/9/25 thì 出荷日 là 2025/9/24) nếu vướng thứ 7 chủ nhật thì lùi 3 ngày 

■ 納期 (Ngày giao hàng)
- trường này trích xuất từ cột 希望納期 trong table đôi lúc nó cũng có thể viết tay và nó chỉ ghi tháng và ngày còn năm sẽ là năm hiện tại (VD: 9/25 -> năm hiện tại/9/25) (năm nay là năm 2026) 

■ supplier_name, supplier_postal_code, supplier_tel (Thông tin đơn vị nhận hàng)
- Vị trí nhận diện: Tìm cụm thông tin nằm trong khối hình chữ nhật ở ngay dưới 【納品先】 (Nơi giao hàng).

1. Quy tắc trích xuất supplier_name:
   - Lấy tên đơn vị (Công ty, Chi nhánh, hoặc Xưởng) xuất hiện ngay bên dưới 【納品先】.
   - Lấy dòng đầu tiên của khối hình chữ nhật 
   - Nếu có tên phòng ban hoặc người phụ trách đi kèm (ví dụ: 九州営業所, 播磨営業所 常峰様), phải lấy đầy đủ.

2. Quy tắc trích xuất supplier_postal_code:
   - Tìm ký hiệu mã bưu điện 〒 nằm trong khu vực thông tin 【納品先】.
   - Trích xuất chính xác dãy số định dạng XXX-XXXX.
   - Ví dụ: 〒839-0841 -> "839-0841".

3. Quy tắc trích xuất supplier_tel:
   - Tìm từ khóa TEL: nằm cùng dòng hoặc gần mã bưu điện của đơn vị nhận hàng.
   - Trích xuất dãy số điện thoại (bao gồm cả mã vùng và dấu gạch nối).
   - Ví dụ: TEL:0942-43-6010 -> "0942-43-6010".

■ supplier_code
- Trường này để null 
   
■ customer_code
- Trường này thì để trống 

============================================================
NHẬN DIỆN DÒNG SẢN PHẨM (ITEM ROW DETECTION)
============================================================
- Một hàng chỉ được tính là tồn tại nếu CẢ 数量 (Số lượng) VÀ 単価 (Đơn giá) đều có giá trị.
- Một hàng trên PDF = Một đối tượng JSON.
- Nếu hàng nào mà có chữ 立替運賃 thì không phải là sản phẩm không cần tạo json cho hàng đấy 

============================================================
TRÍCH XUẤT THÔNG TIN SẢN PHẨM (PRODUCT META EXTRACTION)
============================================================

■ product_type: 	
- trường này trích xuất chính xác từ cột 品名・規格・サイズ của table
### QUY TẮC TÌM KIẾM:
1. Chỉ quét các dòng có chứa từ khóa: "コラムサイズ", "品名・規格・サイズ", "カドビタ", hoặc ký hiệu hình hộp "ロ-".
2. Bỏ qua các loại thép lập là (FB), thép góc (L), thép hình (H) hoặc tiền vận chuyển (立替運賃).

### QUY TẮT CHUẨN HÓA TOÁN HỌC (ÁP DỤNG CHO MỌI SỐ):
Ký hiệu kích thước cột luôn có dạng: [Chiều rộng cạnh] x [Chiều rộng cạnh] x [Độ dày] HOẶC [Chiều rộng cạnh] X [Độ dày].
Hãy thực hiện tách chuỗi theo công thức sau:
- Bước 1: Lấy 2 chữ số đầu tiên của [Chiều rộng cạnh].
- Bước 2: Lấy 2 chữ số của [Độ dày].
- Bước 3: Ghép liền 2 kết quả trên lại với nhau để tạo thành một mã duy nhất gồm 4 chữ số.

### VÍ DỤ MINH HỌA LOGIC (Không giới hạn ở các số này):
- Nếu cạnh 550, dày 22: Lấy 55 và 22 -> Kết quả: 5522
- Nếu cạnh 400, dày 16: Lấy 40 và 16 -> Kết quả: 4016
- Nếu cạnh 300, dày 16: Lấy 30 và 16 -> Kết quả: 3016
- Nếu cạnh 600, dày 28: Lấy 60 và 28 -> Kết quả: 6028

### RÀNG BUỘC ĐẦU RA:
CHỈ hiển thị (các) mã 4 chữ số tìm được. Không giải thích, không kèm văn bản thừa. Nếu có nhiều kết quả khác nhau, mỗi kết quả nằm trên 1 dòng.

- Nếu trong trường hợp category_small là BCP thì product_type phải thêm chữ P ở đầu 

### VÍ DỤ MINH HỌA LOGIC (Không giới hạn ở các số này):
- Nếu cạnh 550, dày 22, category_small là BCP: Lấy 55 và 22 -> Kết quả: P5522
- Nếu cạnh 400, dày 16, category_small là BCP: Lấy 40 và 16 -> Kết quả: P4016
- Nếu cạnh 300, dày 16, category_small là BCP: Lấy 30 và 16 -> Kết quả: P3016
- Nếu cạnh 600, dày 28, category_small là BCP: Lấy 60 và 28 -> Kết quả: P6028

- Trường Hợp: nếu data ở cột 品名・規格・サイズ có chữ ϕ thì thực hiện trích xuất product_type theo các bước dưới đây 
			+ Bước 1: lấy giá trị có dạng AϕXB
			+ Bước 2: Loại bỏ ϕ
			+ Bước 3: Thêm chữ P ở đầu (Ví dụ giá trị trích xuất được từ cột là 318.5ϕx12.7 thì product_type sẽ là P318.5X12.7)

■ product_size: 
- trường này trích xuất chính xác từ cột 品名・規格・サイズ
- product_size sẽ có dạng AXBC (A, B, C đều là 1 số nguyên)
- Ví dụ: giá trị của cột 品名・規格・サイズ là カドピタ裏当金 SN490B 9x25 □-300 x 16 ツメ付 ルートギャップ 7mm thì product_size sẽ là 9X25 
- product size sẽ nằm trong các giá trị sau: 9X25, 6X25, 8X24, 9X19, 9X32, 9X50, 12X25, 12X32, 12X50, 12X70, 16X32, 12X38, 5C 8X24, 5C 9X25, 18C 9X50, 3C 9X25
- Trên đơn đôi khi sẽ có các trường hợp gạch đi và ghi lại bằng mực đỏ và họ chỉ ghi giá trị vào hàng đầu tiên rồi kẻ 1 đường mũi tên từ đầu đến giá trị cuối cùng bị sửa đổi thì bạn sẽ phải ưu tiên lấy giá trị đã được sửa đổi bằng mực đỏ 
- BẠN CẦN PHẢI TRÍCH XUÁT CHÍNH XÁC GIÁ TRỊ CỦA CỘT NÀY KHÔNG ĐƯỢC ĐỌC NHẦM GIÁ TRỊ CỦA HÀNG KHÁC 

■ product_title: 
- Trường này trích xuất từ cột "品名・規格・サイズ" 
- Còn nếu như giá trị của cột 品名・規格・サイズ có chữ GJ thì giá trị của product_title là GJ
- Còn nếu như giá trị của cột 品名・規格・サイズ có chữ GJ-R thì giá trị của product_title là GJ-R
- Còn nếu như giá trị của cột 品名・規格・サイズ không có chữ GJ-R hoặc GJ thì giá trị của product_title là Nothing
- ĐÂY LÀ TRƯỜNG QUA TRỌNG KHÔNG ĐƯỢC BỎ QUA 
- 1 SẢN PHẨM BẮT BUỘC SẼ CÓ 1 product_title NÊN TRƯỜNG NÀY KHÔNG ĐƯỢC ĐỂ NULL 
- Nếu giá trị của cột 品名・規格・サイズ có chữ GJR thì giá trị của product_title là GJ-R

■ col_maker: trường này sẽ trích xuất từ cột "品名・規格・サイズ", trường này có thể sẽ được viết tay nên bạn phải đọc thật kỹ 
- Nếu như mà gặp chữ 日鉄, 日鉄建材, ニッテツ, 共栄, ｷｮｳｴｲ, 日建 và category_small là BCR thì col_maker là NS-R còn category_small là BCP thì col_maker là NS-P 
- Nếu như mà gặp chữ 京浜, JFE thì col_maker là JFE
- Nếu như mà gặp chữ 知多, JFE-W thì col_maker là JFE-W
- Nếu như mà gặp chữ 丸一, ﾏﾙｲﾁ  hi col_maker là ﾏﾙｲﾁ   
- Nếu như mà gặp chữ TSC, 東京製鉄, ﾄｳﾃﾂ  thì col_maker là ﾄｳﾃﾂ 
- Nếu như mà không gặp gì thì col_maker là ｺｳｶﾝ
- Nếu như mà gặp chữ T, m, ﾒｰｶｰﾅｼ thì col_maker là ﾒｰｶｰﾅｼ  
- Nếu như mà gặp chữ 中島, ﾅｶｼﾞﾏ thì col_maker là ﾅｶｼﾞﾏ 
- Nếu như mà gặp chữ 佐々木, ｻｻｷ thì col_maker là ｻｻｷ 
- Nếu như mà gặp chữ 佐野, ｾｲｹｲ thì col_maker là ｾｲｹｲ
- Nếu như mà gặp các chữ nằm trong các chữ mà mình đã chỉ định ở trên thì mình phải chuyển về định dạng giống với mấy chữ ở trên (ví du: ナカジマ -> ﾅｶｼﾞﾏ)
- Cái trường này sẽ có một số trường hợp là họ sẽ sửa hoặc bổ xung bằng mực đỏ nên bạn cũng phải để ý rất kỹ (ví dụ: mực in của file có thể là JFE nhưng nó hoàn toàn có thể thêm -w bằng mực đỏ vào để tạo thành JFE-W ), ,ếu mà có một cái mũi tên được viết bằng mực đỏ kẻ từ trên xuống thì có nghĩa là tất cả các sản phẩm bị kẻ cũng sẽ bị ảnh hưởng theo 

■ mat_size: 
- trường này sẽ thường là 1 trong các giá trị sau đây: 3C, 5C, 18C, FB 
- trường này thì sẽ trích xuất từ cột "品名・規格・サイズ" 
- nếu như trên cột "品名・規格・サイズ"  không có 3C, 5C, 18C thì giá trị mặc định của trường này nó sẽ là FB 

■ category_small: 
- trường này sẽ trích xuất từ cột "品名・規格・サイズ" 
- trường này có thể là BCR, BCP, STKT, STK 
- Chỉ cần trong hàng của cái sản phẩm đấy có chữ BCR, BCP, STKT thì category_small cũng là chữ đấy (Ví dụ: trong hàng sản phẩm đấy có chữ UBCR thì category_small sẽ là BCR)
- nếu giá trị của 品名・規格・サイズ có ký tự ϕ thì category_small sẽ là STK (Nếu category_small mà là STK thì col_maker là null)

■ オーダーNo (Mã đơn hàng)
- Trích xuất từ mục "当社注番"

■ 工事名 (Tên công trình)
- Trích xuất linh hoạt dựa trên thứ tự ưu tiên sau (từ cao xuống thấp). Nếu không thỏa mãn bất kỳ điều kiện nào, BẮT BUỘC gán giá trị null.
1. Ưu tiên 1 (Từ trường 客先注番): 
Tìm mục "客先注番:" nằm ở phần thông tin bên phải (dưới dòng 当社注番). Nếu có, lấy toàn bộ giá trị sau dấu hai chấm. 
- Ví dụ: 客先注番: 常峰様 -> Lấy "常峰様". 客先注番: 豊前中/一方井様 -> Lấy "豊前中ノ一方井様". 客先注番: 23J-0087 新幹線 -> Lấy "23J-0087 北海道新幹線駅舎新築１（躯体他） ３節" (nếu có thông tin chi tiết hơn ở ngoặc phần địa chỉ, ưu tiên gộp lại).
2. Ưu tiên 2 (Dấu ngoặc định dạng dự án): 
Tìm các chuỗi văn bản nằm trong các dấu ngoặc dạng 【...】 hoặc <...> xuất hiện ở phần Header (thường dưới tên khách hàng/địa chỉ giao hàng). 
- Lấy nội dung bên trong ngoặc VÀ các thông tin hậu tố đi liền ngay sau đó (thường là số tầng, khu vực, cấu kiện như 節, 梁, 工区).
- Ví dụ: 【札幌ダイビル再開発プロジェクト 新築工事】 8節G梁 -> Lấy "札幌ダイビル再開発プロジェクト新築工事 8節 G梁". <(株)SUBARUボディ・トリム棟 (北棟)40工区2節大梁> -> Lấy "(株)ＳＵＢＡＲＵボディ・トリム棟（北棟）４０工区 ２節 大梁".
- LOẠI TRỪ: Bỏ qua nếu nội dung trong ngoặc chỉ là chỉ thị vận chuyển như 【納品先】, 【直送時送り状をFAX...】.
3. Ưu tiên 3 (Từ chi tiết bảng/Ghi chú): 
Nếu cột 品名・規格・サイズ hoặc cột 備考 có một dòng văn bản độc lập mô tả tên dự án (thường chứa các từ khóa như 計画, 工事, 節, 階, 梁, 仕口分), hãy trích xuất toàn bộ chuỗi đó.
- Ví dụ: "神田錦町計画 5節 R階 小梁".
[QUAN TRỌNG] ĐIỀU KIỆN TRẢ VỀ NULL (CHỐT CHẶN AN TOÀN):
- TUYỆT ĐỐI KHÔNG lấy tên công ty, tên chi nhánh, xưởng, hoặc địa chỉ thông thường (ví dụ: コンドーテック株式会社 九州営業所, (有)桑原鉄工所 第二工場) làm Tên công trình.
- Nếu mục 客先注番 bị trống/không tồn tại, VÀ không có dấu ngoặc 【】/ < > nào chứa tên dự án, VÀ không có từ khóa công trình (工事, 計画, v.v.), thì BẮT BUỘC trả về null.
Quy tắc Chuẩn hóa (BẮT BUỘC nếu có dữ liệu): 
- KHÔNG giữ lại các dấu ngoặc 【 】 hoặc < > trong kết quả cuối cùng.
- Xóa bỏ các ký hiệu đánh dấu thừa (ví dụ: vòng tròn số ①, ②).
- Chuẩn hóa các dấu gạch chéo / thành chữ Katakana ノ nếu tên người có dạng ghép (ví dụ: 豊前中/一方井 -> 豊前中ノ一方井).
- XỬ LÝ GIỚI HẠN ĐỘ DÀI (RẤT QUAN TRỌNG):
	+ Sau khi hoàn tất:
		* Trích xuất
		* Làm sạch dữ liệu
		* Chuẩn hóa
	+ Tính tổng số ký tự của giá trị cuối cùng
	+ Nếu độ dài ≤ 30 ký tự:
		* Giữ nguyên toàn bộ (Latin và số ở dạng full-width)
	+ Nếu độ dài > 30 ký tự:
		* Chuyển TOÀN BỘ chữ cái Latin và chữ số từ Full-width (全角) → Half-width (半角)
		* Giữ nguyên các ký tự tiếng Nhật (Kanji, Hiragana, Katakana)
		* KHÔNG được cắt chuỗi
		* KHÔNG thay đổi ý nghĩa nội dung
	+ Mục đích:
		* Đảm bảo phù hợp giới hạn ô input tối đa 30 ký tự
- trường này thì bắt buộc phải lấy của trang tương ứng với cái bản ghi đấy chứ không được lấy của trang đầu tiên 

■ is_processing
- trường này để là True 

============================================================
CHỐT AN TOÀN DỮ LIỆU (PRODUCT META SAFETY LOCK)
============================================================
- product_type KHÔNG ĐƯỢC trùng với mã sản phẩm (商品コード).
- KHÔNG tự ý suy luận dữ liệu không có sẵn trên PDF.
- KHÔNG kết hợp hoặc "mượn" dữ liệu giữa các hàng khác nhau.
- Nếu không chắc chắn hoặc mơ hồ -> Trả về null.
============================================================
QUY TẮC VỀ SỐ VÀ VĂN BẢN
============================================================

■ 員数
- trường 員数 sẽ trích xuất từ cột 数量单位

■ CÁC TRƯỜNG DỮ LIỆU SỐ (員数, 単価):
- Trích xuất giá trị số thô từ các cột tương ứng.
- Kết quả là kiểu Số (Number), không để trong dấu ngoặc kép.
- Loại bỏ dấu phẩy phân cách hoặc ký tự đơn vị (ví dụ: 1,000 -> 1000).

■ BẢO TỒN VĂN BẢN:
- Giữ nguyên văn bản tiếng Nhật (Kanji/Kana) chính xác như trên file.
- Chỉ chuẩn hóa các khoảng trắng thừa.
- KHÔNG diễn giải lại, không dịch, không rút ngắn văn bản.
