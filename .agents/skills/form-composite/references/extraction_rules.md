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
RULES (QUY TẮC TRÍCH XUẤT)
============================================================
- CHỈ trả về định dạng JSON hợp lệ. Không kèm văn bản ngoài (markdown). Không thêm chú thích.
- Kết quả đầu ra phải khớp chính xác cấu trúc: {"header": {...}, "tables": {"items": [...]}}
- Sản phẩm thì bạn phải đọc của tất cả các cáitrang không phải là đọc của 1 trang 

============================================================
KHÓA SCHEMA NGHIÊM NGẶT (STRICT SCHEMA LOCK)
============================================================
- Giữ nguyên các KEY chính xác như trong schema mẫu.
- KHÔNG thêm/xóa/đổi tên các key.
- Thông tin thiếu hoặc không rõ ràng => gán giá trị null.
- KHÔNG tự ý suy luận giá trị trừ khi có hướng dẫn cụ thể.

[EXPLICIT BLACKLIST - QUAN TRỌNG]
Bạn BẮT BUỘC phải để giá trị `null` cho các trường sau, BẤT KỂ trên PDF ghi gì. KHÔNG trích xuất dữ liệu cho các key này:
- "商品コード" PHẢI LÀ null.
- "受注区分" PHẢI LÀ null.
- "搬入口" PHẢI LÀ null.
- "代理店" PHẢI LÀ null.
- "出荷倉庫" PHẢI LÀ null.
- "受注担当者" PHẢI LÀ null.

============================================================
QUY TẮC TRÍCH XUẤT PHẦN HEADER
============================================================

■ オーダーNo (Mã đơn hàng)
- Trích xuất từ mục "No."

■  agent là 255820

■ 工事名 (Tên công trình)
	- TASK: OCR "工事名" từ bản vẽ & RÚT GỌN nội dung theo quy tắc hệ thống.
	- CÔNG THỨC: [記号] [工事名称 (Đã rút gọn)] [区分名称 (Chỉ lấy dòng 1)]

	- QUY TẮC RÚT GỌN 工事名称 (QUAN TRỌNG):
		+ Loại bỏ các cụm từ thừa sau đây khỏi mục [工事名称] để khớp với giới hạn ký tự:
			1. Loại bỏ cụm từ loại hình: "第一種", "市街地".
			2. Loại bỏ trạng thái: "（仮称）", "(仮称)".
			3. Loại bỏ hậu tố công trình: "新築工事", "建築物".
			4. Ưu tiên giữ lại: Tên địa danh (VD: 虎ノ門...) và cụm từ dự án chính (VD: 再開発事業).
	- QUY TẮC ĐỊNH DẠNG KÝ TỰ:
		1. [記号]: LUÔN chuyển Katakana sang Bán giác (Hankaku). VD: ﾓ, ｱ3, ﾅC.
		2. [区分名称]: TUYỆT ĐỐI chỉ lấy dòng đầu tiên.
		3. Ký tự Hankaku/Zenkaku:
			+ Bán giác (Half-width): Số (1, 2, 17), chữ latin, dấu `:`, dấu `()`.
			+ Toàn giác (Full-width): Khi ký tự rộng bằng 1 chữ Hán. VD: ＣＳ, １５, （ ）, ．.
		4. Cách nhau bởi 1 khoảng trắng giữa 3 thành phần.

	- VÍ DỤ ĐỐI CHIẾU (Gốc -> Rút gọn):
	+ 虎ノ門...第一種市街地 再開発...新築工事 -> 虎ノ門一丁目東地区市街地再開発事業に係る施設建築物
	+ 八重洲...第一種市街地 再開発事業施設建築物 -> 八重洲二丁目中地区市街地再開発事業施設
	+ （仮称）内幸町...新築工事 -> 内幸町一丁目街区南地区再開発事業
	- OUTPUT: Chỉ trả về dòng: 工事名 : [Văn bản xử lý xong]

■ 出荷日 (Ngày xuất hàng)
- trường này thông thường sẽ được viết tay bằng chữ màu đen và được khoanh tròn ở ngay bên cạnh chữ 引取り và nó chỉ ghi tháng và ngày năm sẽ là năm hiện tại (VD: 9/25 -> năm hiện tại/9/25) (năm nay là năm 2026)
- Định dạng nghiêm ngặt: YYYY/MM/DD

■ 納期 (Ngày giao hàng)
- trường này thông thường sẽ được viết tay bằng chữ màu đen và được khoanh tròn ở ngay bên cạnh chữ 引取り và nó chỉ ghi tháng và ngày năm sẽ là năm hiện tại (VD: 9/25 -> năm hiện tại/9/25) (năm nay là năm 2026)
- Định dạng nghiêm ngặt: YYYY/MM/DD
- 2 trường 出荷日, 納期 lúc nào cũng giống nhau 

■ supplier_name 
- trường này thì để null 

■ supplier_code
- trường này sẽ đọc ở cạnh cái tiêu đề trên đầu của đơn hoặc nếu như cái tiêu đề trên đầu của đơn mà nằm ở góc trái thì bạn đọc ở góc trên cùng bên phải của đơn nếu là 川 1 thì supplier_code là 255820 nếu là 川 3 thì là 255821 
- Ví dụ: tiêu đề là 現寸指示書 ở bên cạnh có chữ 川 1 thì supplier_code là 255820
- Ví dụ: trong trường hợp tiêu đề nằm ở bên phải của đơn thì chữ 川 sẽ nằm ở bên trên ô 検 収 櫃 ở trên cùng góc bên phải của đơn 
- cái chữ kawa kia viết tay nên bạn phải đọc thật kỹ số 1 với số 3 thường được khoanh tròn 
- cái chữ 川 thường được đặt ở trên cùng góc bên phải của đơn 
- đây là 1 trường đặc biệt quan trọng kiểu gì cũng có nên bạn phải đặc biệt quan tâm không được bỏ qua phải tìm bằng được ở trên đơn xem nó là 川 1 hay là 川 3 

■ customer_name1 và customer_name2 thì để null 

============================================================
NHẬN DIỆN DÒNG SẢN PHẨM (ITEM ROW DETECTION)
============================================================
- Một hàng chỉ được tính là tồn tại nếu CẢ 数量 (Số lượng) VÀ 単価 (Đơn giá) đều có giá trị.
- Một hàng trên PDF = Một đối tượng JSON.

============================================================
TRÍCH XUẤT THÔNG TIN SẢN PHẨM (PRODUCT META EXTRACTION)  (đây là phần quan trọng nhất trong file pdf file nào cũng sẽ có ít nhất 1 sản phẩm nên bạ phải phân tích thật kỹ không đọcw bỏ qua cái này 
============================================================
■ product_type: trường này có 5  trường hợp xảy ra trong file pdf và trích xuất từ cột 設計タイプ và cột 名称
+ Trường hợp 1: 
- Trường này trong bảng thường có dạng là AXBXC (A, B, C là số) lúc này chúng ta sẽ lấy 2 số đầu của số AX với số B (ví dụ: ABCXDEFXGH cả A, B, C, D, E, F, G, H đều là 1 số nguyên ->product_type chính là ABGH) 
- [Quy tắc quan trọng] ở trường hợp 1 này thì product_type sẽ có 4 chữ số không phải 5 nên bạn không bao giờ được đọc nhầm (vd: product_type chính là 3009 là ĐÚNG còn product_type chính là 30009 là SAI)
- Ví dụ: hàng dữ liệu có dạng □-750x750x36用 thì product_type là 7536 
+ Trường hợp 2: 
- Nếu category_small mà là BCP thì phải thêm chữ P vào đằng trước 
- Ví dụ: hàng dữ liệu có dạng □-750x750x36用 thì product_type là P7536
+ Trường hợp 3:  
- Trường hợp mà ở hàng sản phầm găp chữ JBCR hoặc JFE知多 hoặc col_maker mà là JFE-W thì bạn cần phải thêm chữ J vào đằng sau product_type [QUY TẮC QUAN TRỌNG KHÔNG ĐƯỢC BỎ QUA ]
- Ví dụ:  □-750x750x36用 4X18C JFE知多 thì product_type là 5022J 
+ Trường hợp 4:
- Trường hợp mà kích thước trong bằng sản phẩm có dạng AXB thì lúc này chúng ta sẽ lấy 2 số đầu của số AX với số B (ví dụ: ABCXGH cả A, B, C, G, H đều là 1 số nguyên ->product_type chính là ABGH)
+ Trường hợp 5:  
- Nếu như mà trường AXBXC hoặc AXB có A là 4 chữ số chứ không phải 3 chữ số thì sẽ lấy 2 số giữa của A chứ không phải 2 số đầu 
- Ví dụ: hàng dữ liệu có dạng □-1000x1000x36用 FB 25 x 9 238 thì product_type là 0036

■ product_size: trích xuất từ cột 品名, product_size sẽ có dạng AXBC (A, B, C đều là 1 số nguyên) (dữ liệu ở cột có thể ghi là BCXA thì bạn tự chuẩn hóa về AXBC)
- product size sẽ nằm trong các giá trị sau: 9X25, 6X25, 8X24, 9X19, 9X32, 9X50, 12X25, 12X32, 12X50, 12X70, 16X32, 12X38, 5C 8X24, 5C 9X25, 18C 9X50, 3C 9X25

■ product_title: trường này có thể là GJ-R hoặc GJ hoặc null (nếu trong trường hợp trên hàng sản phẩm không phải là GJ-R hoặc GJ thì bắt buộc là null) (đây là quy tắc quan trọng không được bỏ qua) 
- Nếu như product_title không phải GJ-R hoặc GJ thì bạn cứ mặc định product_title là null cho mình 
- Trường này thường viết tay bằng mực đỏ và đôi khi sẽ chi ghi ở bản ghi đầu tiên bắt đầu từ bản ghi thứ 2 sẽ được vạch 1 mũi tên màu đỏ bắt đầu từ bản ghi đầu tiên bị ảnh hưởng đến bản ghi cuối cùng bị ảnh hưởng 
- Vị trí của trường này thường nằm ngay sau product_size

■ col_maker: trường này sẽ được viết ở bất kỳ nơi nào ở trên file pdf thông thường sẽ viết 1 lần app dụng cho tất cả các sản phẩm ở trên trang 
- Nếu như mà gặp chữ 日鉄, 日鉄建材, ニッテツ, 共栄, ｷｮｳｴｲ, 日建 và category_small là BCR thì col_maker là NS-R còn category_small là BCP thì col_maker là NS-P 
- Nếu như mà gặp chữ 京浜, JFE thì col_maker là JFE
- Nếu như mà gặp chữ 知多, JFE-W thì col_maker là JFE-W
- Nếu như mà gặp chữ 丸一, ﾏﾙｲﾁ  thì col_maker là ﾏﾙｲﾁ   
- Nếu như mà gặp chữ TSC, 東京製鉄, ﾄｳﾃﾂ  thì col_maker là ﾄｳﾃﾂ 
- Nếu như mà không gặp gì thì col_maker là ｺｳｶﾝ
- Nếu như mà gặp chữ T, m, ﾒｰｶｰﾅｼ thì col_maker là ﾒｰｶｰﾅｼ  
- Nếu như mà gặp chữ 中島, ﾅｶｼﾞﾏ thì col_maker là ﾅｶｼﾞﾏ 
- Nếu như mà gặp chữ 佐々木, ｻｻｷ thì col_maker là ｻｻｷ 
- Nếu như mà gặp chữ 佐野, ｾｲｹｲ thì col_maker là ｾｲｹｲ
- Nếu như mà gặp các chữ nằm trong các chữ mà mình đã chỉ định ở trên thì mình phải chuyển về định dạng giống với mấy chữ ở trên (ví du: ナカジマ -> ﾅｶｼﾞﾏ)
- Cái trường này sẽ có một số trường hợp là họ sẽ sửa hoặc bổ xung bằng mực đỏ nên bạn cũng phải để ý rất kỹ (ví dụ: mực in của file có thể là JFE nhưng nó hoàn toàn có thể thêm -w bằng mực đỏ vào để tạo thành JFE-W ), ,ếu mà có một cái mũi tên được viết bằng mực đỏ kẻ từ trên xuống thì có nghĩa là tất cả các sản phẩm bị kẻ cũng sẽ bị ảnh hưởng theo 

■ mat_size: trường này sẽ nằm ngày đằng trước của product_size và sẽ thường là 1 trong các giá trị sau đây: 3C, 5C, 18C, FB 
- Nếu trong trường hợp trong cái cell sản phầm đấy không có 3C, 5C, 18C thì mat_size chính là FB 

■ category_small: trường này sẽ có 2 trường hợp xảy ra đó là BCP hoặc BCR nếu như hàng sản phẩm đấy có chữ BCP thì category_small là BCP còn trên hàng sản phẩm đấy có chữ BCR thì category_small là BCR 
- trường này có thể ghi ở bất kỳ đâu ở trên trang và thông thường chỉ ghi 1 lần app dụng cho toàn trang

■ オーダーNo (Mã đơn hàng)
- Trích xuất từ mục "No."
- Loại bỏ các số 0 ở đầu (ví dụ: 0020 -> 20).
- trường này thì bắt buộc phải lấy của trang tương ứng với cái bản ghi đấy chứ không được lấy của trang đầu tiên 

■ 工事名 (Tên công trình)
	- TASK: OCR "工事名" từ bản vẽ & RÚT GỌN nội dung theo quy tắc hệ thống.
	- CÔNG THỨC: [記号] [工事名称 (Đã rút gọn)] [区分名称 (Chỉ lấy dòng 1)]

	- QUY TẮC RÚT GỌN 工事名称 (QUAN TRỌNG):
		+ Loại bỏ các cụm từ thừa sau đây khỏi mục [工事名称] để khớp với giới hạn ký tự:
			1. Loại bỏ cụm từ loại hình: "第一種", "市街地".
			2. Loại bỏ trạng thái: "（仮称）", "(仮称)".
			3. Loại bỏ hậu tố công trình: "新築工事", "建築物".
			4. Ưu tiên giữ lại: Tên địa danh (VD: 虎ノ門...) và cụm từ dự án chính (VD: 再開発事業).
	- QUY TẮC ĐỊNH DẠNG KÝ TỰ:
		1. [記号]: LUÔN chuyển Katakana sang Bán giác (Hankaku). VD: ﾓ, ｱ3, ﾅC.
		2. [区分名称]: TUYỆT ĐỐI chỉ lấy dòng đầu tiên.
		3. Ký tự Hankaku/Zenkaku:
			+ Bán giác (Half-width): Số (1, 2, 17), chữ latin, dấu `:`, dấu `()`.
			+ Toàn giác (Full-width): Khi ký tự rộng bằng 1 chữ Hán. VD: ＣＳ, １５, （ ）, ．.
		4. Cách nhau bởi 1 khoảng trắng giữa 3 thành phần.

	- VÍ DỤ ĐỐI CHIẾU (Gốc -> Rút gọn):
	+ 虎ノ門...第一種市街地 再開発...新築工事 -> 虎ノ門一丁目東地区市街地再開発事業に係る施設建築物
	+ 八重洲...第一種市街地 再開発事業施設建築物 -> 八重洲二丁目中地区市街地再開発事業施設
	+ （仮称）内幸町...新築工事 -> 内幸町一丁目街区南地区再開発事業
	- OUTPUT: Chỉ trả về dòng: 工事名 : [Văn bản xử lý xong]

■ 長さ: trường này mặc định để null 

■ 員数: Extract the numeric value from the "数量" column.

■ is_processing
- trường này để là True 

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
