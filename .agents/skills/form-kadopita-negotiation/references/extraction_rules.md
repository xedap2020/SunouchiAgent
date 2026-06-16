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
- Ở cái đơn này items lúc nào cũng sẽ có ít nhất 1 bản ghi nên bạn không được bỏ qua 
-NẾU GẶP FILE PDF CÓ NHIỀU TRANG THÌ HEADER LẤY DATA Ở TRANG ĐẦU TIÊN, CÒN ITEMS THÌ PHẢI LẤY CỦA TẤT CẢ CÁC TRANG, KHÔNG ĐƯỢC BỎ QUA TRANG NÀO (ĐÂY LÀ QUY TẮC CỰC KỲ QUAN TRỌNG)
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

============================================================
QUY TẮC TRÍCH XUẤT PHẦN HEADER
============================================================

■ オーダーNo (Mã đơn hàng)
- Trích xuất từ mục "発注書NO." nếu có 

■ 工事名 (Tên công trình)
- Trích xuất từ mục: "物件名（工区・節）"

■ 出荷日 (Ngày xuất hàng)
- Trường này sẽ lùi lại 1 ngày với 納期 nếu vướng thứ 7 hoặc chủ nhật thì phải lùi 3 ngày (bạn phải tự tính toán 納期 là thứ mấy trong năm để xác định chính xác 出荷日)
- Định dạng nghiêm ngặt: YYYY/MM/DD

■ 納期 (Ngày giao hàng)
- Trường này sẽ được viết tay bằng chữ màu đỏ ở trên đơn and được viết dưới dạng tháng/ngày còn năm sẽ lấy mặc định là 2026 (ví dụ: trên đơn ghi 5/13 thì 納期 sẽ là 2026/5/13)
- Định dạng nghiêm ngặt: YYYY/MM/DD

■ supplier_name 
- Trường này trích xuất ở mục 会社名 của mục 納入先

■ supplier_tel 
- Trường này trúc xuất ở mục TEL của mục 納入先
- Định dạng của trường này là XXX-XXX-XXXX hoặc XXXX-XX-XXXX , nếu như trên file pdf chỉ có 1 dãy số kiểu XXXXXXXXXX thì bạn phải chuẩn hóa về định dạng XXX-XXX-XXXX hoặc XXXX-XX-XXXX

■ supplier_code
- trường này thì để null 

■ customer_name1 và customer_name2 thì để null 

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
TRÍCH XUẤT THÔNG TIN SẢN PHẨM (PRODUCT META EXTRACTION)  (đây là phần quan trọng nhất trong file pdf file nào cũng sẽ có ít nhất 1 sản phẩm nên bạn phải phân tích thật kỹ không đọc bỏ qua cái này) 
============================================================
■ product_type: 	
- trường này trích xuất chính xác từ cột コラムサイズ của table
- giá trị của cột コラムサイズ sẽ có 3 trường hợp xảy ra 
	+ Trường hợp 1 AxBxC (A, B, C là 1 số nguyên, A nhỏ hơn B và C)
		- Các bước trích xuất product_type cho trường hợp 1 
			+ Bước 1: lấy giá trị từ cột コラムサイズ, cột コラムサイズ sẽ có dạng AxBxC (A, B, C là các số nguyên) 
			+ Bước 2: Chuẩn hóa AXBXC vừa lấy được nếu như có số nào có 1 chữ số thì cho thêm 1 chứ số 0 ở đầu cho đủ 2 chữ số (ví dụ:  AXBXC là 9x200x200 thì phải đổi về 09X200X200)
			+ Bước 3: Xác định giá trị ở cột 区分※1 (đôi khi trên đơn sẽ ghi là 分類) là chữ R hay chữ P hay chữ S 
				- Trường hợp 区分※1 là chữ R thì product_type sẽ là 2 số đầu tiên của số B cộng với số A (A, B, C lúc này đã phải được chuẩn hóa)(Ví dụ: giá trị của コラムサイズ là 25X450X450 thì product_type sẽ là 4525)
				- Trường hợp 区分※1 là chữ P thì product_type sẽ là chữ P cộng với 2 số đầu tiên của số B cộng với số A (A, B, C lúc này đã phải được chuẩn hóa)(Ví dụ: giá trị của コラムサイズ là 12X350X350 thì product_type sẽ là P3512)
	+ Trường hợp 2 AxBxC (A, B, C là 1 số nguyên, C nhỏ hơn A và B)
		- Các bước trích xuất product_type cho trường hợp 2 
			+ Bước 1: lấy giá trị từ cột コラムサイズ, cột コラムサイズ sẽ có dạng AxBxC (A, B, C là các số nguyên) 
			+ Bước 2: Chuẩn hóa AXBXC vừa lấy được nếu như có số nào có 1 chữ số thì cho thêm 1 chứ số 0 ở đầu cho đủ 2 chữ số (ví dụ: AXBXC là 200x200x9 thì phải đổi về 200X200x09)
			+ Bước 3: Xác định giá trị ở cột 区分※1 (đôi khi trên đơn sẽ ghi là 分類) là chữ R hay chữ P hay chữ S 
				- Trường hợp 区分※1 là chữ R thì product_type sẽ là 2 số đầu tiên của số A cộng với 2 số đầu tiên của số C (A, B, C lúc này đã phải được chuẩn hóa)(Ví dụ: giá trị của コラムサイズ là 450X450X25 thì product_type sẽ là 4525)
				- Trường hợp 区分※1 là chữ P thì product_type sẽ là chữ P cộng với 2 số đầu tiên của số B cộng với số A (A, B, C lúc này đã phải được chuẩn hóa)(Ví dụ: giá trị của コラムサイズ là 350X350X42 thì product_type sẽ là P3542 đây chỉ là ví dụ thực tế thì bạn cần phải lấy các con số ở trên đơn)
	+ Trường hợp 3: nếu data ở cột 区分※1 là ϕ thì thực hiện trích xuất product_type theo các bước dưới đây 
		- Các bước trích xuất product_type cho trường hợp 3
			+ Bước 1: lấy giá trị từ cột コラムサイズ, cột コラムサイズ sẽ có dạng AxB
			+ Bước 2: Chuẩn hóa AxB về AXB và thêm chữ P ở đầu (Ví dụ giá trị của コラムサイズ là 318.5x12.7 thì product_type sẽ là P318.5X12.7)
		
- bạn cần phải đọc data chính xác từ cột コラムサイズ của table không được nhầm sang cột khác 
- PRODUCT_TYPE SẼ CÓ DẠNG 4 CHỮ SỐ CHỨ KHÔNG PHẢI 5 CHỮ SỐ HAY 6 CHỮ SỐ. KHI TRÍCH XUẤT CHỈ ĐƯỢC LẤY 2 SỐ ĐẦU CỦA B CỘNG VỚI 2 SỐ CUỐI CỦA A. TUYỆT ĐỐI KHÔNG ĐƯỢC NHẦM THÀNH 5 CHỮ SỐ HOẶC 6 CHỮ SỐ.
(Ví dụ: コラムサイズ là 9x300x300 và category_small là BCR thì product_type sẽ là 3009 chứ không phải là 093030 hay 30009)
- bạn cần phải trích xuất chính xác giá trị của từng hàng không được nhầm giữa các hàng với nhau 
- [CỰC KỲ QUAN TRỌNG - KHÔNG COPY HÀNG TRÊN]: Mỗi hàng trong bảng có kích thước khác nhau hoàn toàn (ví dụ: hàng 1 là 22, hàng 2 là 19, hàng 3 là 16). BẮT BUỘC phải tính toán lại product_type độc lập cho từng hàng dựa trên con số thực tế của hàng đó. TUYỆT ĐỐI KHÔNG ĐƯỢC sao chép kết quả tính của hàng trên để áp dụng cho các hàng phía dưới.

■ product_size: 
- trường này trích xuất chính xác từ cột FBサイズ※2 
- product_size sẽ có dạng AXBC (A, B, C đều là 1 số nguyên)
- Ví dụ: giá trị của cột FBサイズ※2 là FB9x25 thì product_size sẽ là 9X25 
- product size sẽ nằm trong các giá trị sau: 9X25, 6X25, 8X24, 9X19, 9X32, 9X50, 12X25, 12X32, 12X50, 12X70, 16X32, 12X38
- bạn cần phải đọc data chính xác từ cột FBサイズ※2 của table không được nhầm sang cột khác 
- Trên đơn đôi khi sẽ có các trường hợp gạch đi và ghi lại bằng mực đỏ và họ chỉ ghi giá trị vào hàng đầu tiên rồi kẻ 1 đường mũi tên từ đầu đến giá trị cuối cùng bị sửa đổi thì bạn sẽ phải ưu tiên lấy giá trị đã được sửa đổi bằng mực đỏ 
(Ví dụ: giá trị của cột FBサイズ※2 là FB9x25 nhưng cũng có thể họ gạch số 25 đi rồi ghi số 50 vào bên cạnh thì product_size lúc này là 9X50 nhưng bạn phải để ý cái mũi tên màu đỏ sẽ tương ứng với các bản ghi bị ảnh hưởng)
- [KHÔNG TỰ SUY DIỄN SỐ]: Chỉ trích xuất product_size từ cột FBサイズ※2 và bắt buộc phải khớp với danh sách đã cho (9X25, 6X25...). TUYỆT ĐỐI KHÔNG lấy các con số ở cột kích thướcコラム (như số 19, 16) để tự chế ra các kích thước lạ không có trong danh sách (như 9X19). Nếu không thấy ghi rõ ở cột FBサイズ※2 thì để là null.

■ product_title: 
- Trường này trích xuất từ cột "テーパー※4GJ・GJ-R" hoặc "テーパー〈分類4〉GJ・GJ-R".
- [QUY TẮC Ô TIÊU ĐỀ GỘP DỌC]: Cột này có phần tiêu đề (Header) là ô gộp dọc (Multirow/Rowspan) gồm 2 dòng chữ cố định là "テーパー※4" (hoặc "テーパー〈分類4〉") ở trên và "GJ・GJ-R" ở dưới. 
- TUYỆT ĐỐI KHÔNG trích xuất các chữ cố định của tiêu đề gộp này để điền cho dữ liệu hàng. Chỉ bốc dữ liệu nằm hoàn toàn PHÍA DƯỚI thanh ngăn cách ngang của tiêu đề chính.
- Trường này có thể có các giá trị thực tế viết/in bên dưới là: GJ-R, GJ, hoặc để trống.
- Tuyệt đối phải lấy đúng giá trị thực tế ghi trong cột tương ứng với hàng đó, KHÔNG ĐƯỢC đoán bừa. Nếu ô dữ liệu của hàng đó để TRỐNG, product_title bắt buộc phải gán giá trị là null.
- Tuyệt đối không được đoán nhầm GJ・GJ-R ở trên header phải truy xuất đúng hàng [ĐÂY LÀ QUY TẮC ĐẶC BIỆT QUAN TRỌNG BỞI VÌ ĐỌC SAI TRƯỜNG NÀY SẼ ĐỌC SAI TẤT CẢ]

■ col_maker: trường này sẽ đọc ở ngay bên dưới カドピタ và thường được căn giữa ở dưới cùng của cái ô đấy, trường này có thể sẽ được viết tay nên bạn phải đọc thật kỹ 
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
- Nếu category_small mà là STK thì col_maker là null

■ mat_size: 
- trường này sẽ thường là 1 trong các giá trị sau đây: 3C, 5C, 18C, FB 
- trường này thì sẽ trích xuất từ cột FBサイズ※2

■ category_small: 
- trường này sẽ trích xuất từ cột 区分※1 (đôi khi trên đơn sẽ ghi là 分類)
- nếu giá trị của 区分※1 là R thì category_small sẽ là BCR nếu là chữ P thì giá trị của category_small sẽ là BCP còn là chữ S thì sẽ là STKT 
- nếu giá trị của 区分※1 là ϕ thì category_small sẽ là STK (Nếu category_small mà là STK thì col_maker là null)

■ オーダーNo (Mã đơn hàng)
- Trích xuất từ mục "発注書NO." nếu có 
- trường này thì bắt buộc phải lấy của trang tương ứng với cái bản ghi đấy chứ không được lấy của trang đầu tiên 

■ 工事名 (Tên công trình)
- Trích xuất từ mục: "物件名（工区・節）"
- trường này thì bắt buộc phải lấy của trang tương ứng với cái bản ghi đấy chứ không được lấy của trang đầu tiên trừ trường hợp pdf chỉ có 1 trang sản phẩm thì lấy của trang đầu tiên 

■ is_processing
- trường này để là True 

============================================================
CHỐT AN TOÀN DỮ LIỆU (PRODUCT META SAFETY LOCK)
============================================================
- KHÔNG tự ý suy luận dữ liệu không có sẵn trên PDF.
- KHÔNG kết hợp hoặc "mượn" dữ liệu giữa các hàng khác nhau.
- Nếu không chắc chắn hoặc mơ hồ -> Trả về null.
- 長さ: trường này để là null 
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
- KHÔNG diễn giải lại, không dịch, không rút ngắn văn bản.'
- Các hàng mà có chữ 運賃 thì không phải là 1 bản ghi chuẩn nên bỏ qua không đọc hàng đấy chuyển xuống đọc hàng tiếp theo luôn
