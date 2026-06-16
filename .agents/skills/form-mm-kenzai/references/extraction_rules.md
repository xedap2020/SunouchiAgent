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
- Trích xuất từ mục "発注No."
- Loại bỏ các số 0 ở đầu (ví dụ: 0020 -> 20).

■ agent (hãng)
- Trích xuất từ mục "発注No."
- Loại bỏ các số 0 ở đầu (ví dụ: 0020 -> 20).
- Chỉ lấy 2 số đầu tiên (ví dụ: 123456 -> 12)

■ 工事名 (Tên công trình)
- Trích xuất từ nhãn: "工事名:"

- Phạm vi lấy dữ liệu:
+ Bắt đầu từ:
* Nội dung nằm ngay sau "工事名:" trên cùng một dòng, hoặc
* Dòng kế tiếp gần nhất nếu dòng chứa nhãn không có dữ liệu

+ Cho phép đọc tiếp các dòng phía dưới (dòng 2, 3, 4, ...) nếu:
* Nội dung vẫn thuộc cùng một cụm thông tin của 工事名
* Bao gồm cả các dòng bổ sung/ghi chú liên quan (ví dụ: nội dung trong ngoặc như "(事務所棟)")
* Không gặp điều kiện dừng

- Điều kiện dừng:
+ Dừng khi gặp:
* Trường "郵便番号"
* Dòng tiêu đề, hướng dẫn hoặc nội dung không liên quan

- Ràng buộc:
+ Tuyệt đối không lấy dữ liệu từ bất kỳ dòng nào phía trên "工事名:"
+ Không lấy dữ liệu từ các dòng/trường phía trên có chứa từ "業所"

- Điều kiện dữ liệu:
+ Nếu sau "工事名:" không có nội dung hợp lệ → trả về null
+ Nếu không xác định được rõ ràng giá trị từ OCR → trả về null
- Chuẩn hóa:
+ Nếu giá trị chứa chữ cái Latin hoặc chữ số → chuyển toàn bộ sang dạng full-width (全角)

- Làm sạch dữ liệu:
+ Nếu trong giá trị có chứa "裏当金" → loại bỏ cụm "裏当金" khỏi kết quả
+ Nếu trong giá trị có chứa "ウラ当" → loại bỏ cụm "ウラ当" khỏi kết quả
+ Giữ lại các nội dung trong ngoặc () nếu liên quan đến 工事名 (ví dụ: "(事務所棟)")
+ Loại bỏ khoảng trắng dư thừa ở đầu/cuối và nối các dòng thành một chuỗi

- [LOẠI TRỪ CỤ THỂ]
+ Nếu kết quả đọc được chính xác là:
* "一宮倉庫様分(０００００１００)" hoặc "(有)相澤鉄工 様分 （０００３９３６２）" hoặc "(株)京和建設 様分 (００３１９３１１)"
+ → bắt buộc trả về null

[QUAN TRỌNG - TRÁNH NHẦM LẪN]
- TUYỆT ĐỐI KHÔNG lấy các dòng tiêu đề hoặc ghi chú chung như: "要送り状FAX 発注番号明記のこと"
- Dòng này là header instruction, KHÔNG phải dữ liệu của 工事名.
- Nếu OCR không tìm thấy giá trị rõ ràng cho 工事名 => bắt buộc trả về null.

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
- Trích xuất từ mục "発送日:"
- Định dạng nghiêm ngặt: YYYY/MM/DD

■ 納期 (Ngày giao hàng)
- Trích xuất từ mục "希望着日:"
- Định dạng nghiêm ngặt: YYYY/MM/DD

■ supplier_name (Địa điểm giao hàng): trường này sẽ có 2 trường hợp xảy ra trong đơn (trường này rất là quan trọng bạn phải đọc thật kỹ không được nhầm chữ nào) 
- Trường hợp 1:  Trích xuất từ mục: 納入先名:
BƯỚC 1 — Lấy toàn bộ dòng sau nhãn "納入先名:".
BƯỚC 2 — Loại bỏ phần văn bản kết thúc bằng chữ "様".
BƯỚC 3 — Chuẩn hóa danh xưng công ty:
株式会社 biến thể: 株式会社, (株), （株）, ㈱  -> Chuyển tất cả thành:(株)
有限会社 biến thể: 有限会社, (有), （有）, ㈲  -> Chuyển tất cả thành:(有)
- Nếu danh xưng ở đầu: 株式会社山田 -> ㈱山田
- Nếu danh xưng ở cuối: 山田株式会社 -> 山田㈱
BƯỚC 4 — Loại bỏ các hậu tố hành chính: 事務所, 本社, 本店, 管理部, 営業部.
BƯỚC 5 — CHỈ GIỮ LẠI các hậu tố địa điểm: 工場, ヤード, センター, 倉庫, 置場.
BƯỚC 6 — Loại bỏ khoảng trắng thừa.
BƯỚC 7 — Chuẩn hóa khoảng cách giữa công ty và địa điểm:
- Nếu sau danh xưng công ty (（株）, （有）, ㈱, ㈲) dính liền với tên địa điểm (工場, ヤード, センター, 倉庫, 置場) → chèn 1 khoảng trắng duy nhất giữa chúng.
Ví dụ:
冬木工業（株）倉賀野工場 → 冬木工業（株） 倉賀野工場
山田㈱東京倉庫 → 山田㈱ 東京倉庫
- nếu data trích xuất từ mục 納入先名 chữ (株) nó nằm trước tên cty thì phải giữ nguyên cho nó nằm trước ko được lộn ngược lại (ví dụ: 納入先名:(株) 栁沼鋼業  thì supplier_name nó phải là (株)栁沼鋼業 không phải là 栁沼鋼業（株）)
- Trường hợp 2: Trong trường hợp mục 納入先名 nó có chứa ký tự 止 ở cuối cùng của giá trị của mục 納入先名 thì supplier_name sẽ không phải lấy từ mục 納入先名 nữa mà sẽ lấy từ cuối cùng của table (Ví dụ: 納入先名:宇都宮支店止 thì supplier_name sẽ không phải là 宇都宮支店止 mà phải tìm ở phía bên dưới table)
- BƯỚC 1 — Lấy toàn bộ 2 chuỗi từ đầu tiên của dòng chữ ngay dưới cùng của table 
- BƯỚC 2 — Chuẩn hóa danh xưng công ty:
株式会社 biến thể: 株式会社, (株), （株）, ㈱  -> Chuyển tất cả thành:(株) 
有限会社 biến thể: 有限会社, (有), （有）, ㈲  -> Chuyển tất cả thành:(有)
- Ví dụ: ở cuối cùng của table có dòng chữ kiểu  フルサト工業株式会社    宇都宮営業所    発注者: 桑田くるみ  TEL: 028-677-4025 FAX: 028-677-4028 thì mình lấy フルサト工業株式会社 宇都宮営業所  và sau đó chuẩn hóa lại thành フルサト工業(株) 宇都宮営業所 lúc này supplier_name chính là フルサト工業(株) 宇都宮営業所

■ supplier_postal_code
- Trường này trúc xuất ở mục 郵便番号 ở trên header bắt buộc phải trích xuất ở header ở trên đầu file 
- Định dạng của trường này là XXX-XXXX, , nếu như trên file pdf chỉ có 1 dãy số kiểu XXXXXXX thì bạn phải chuẩn hóa về định dạng XXX-XXXX

■ supplier_tel 
- Trường này trúc xuất ở mục TEL ở trên header tuyệt đối không được lấy TEL ở footer dưới cùng của file chỉ được lấy TEL ở phần header trên đầu file 
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
■ product_type: trường này có 3 trường hợp xảy ra trong file pdf 
+ Trường hợp 1: 
- Trường này chính là chữ nằm cuối cùng của dòng 商品名 trong bảng thường có dạng là 1 số có 3 chữ số X với 1 số có 1 chứ số (ví dụ: ABCX D cả A, B, C, D đều là 1 số nguyên ->product_type chính là ABCD) 
- [Quy tắc quan trọng] ở trường hợp 1 này thì product_type sẽ có 4 chữ số không phải 5 nên bạn không bao giờ được đọc nhầm (vd: product_type chính là 3009 là ĐÚNG còn product_type chính là 30009 là SAI)
- Ví dụ: カドピタ9X25FBCR 300X 9 thì product_type chính là 3009 
+ Trường hợp 2: 
- Trường này chính là chữ nằm cuối cùng của dòng 商品名 trong bảng thường có dạng là 1 số có 3 chữ số X với 1 số có 2 chứ số (ví dụ: ABCX DE cả A, B, C, D, E đều là 1 số nguyên -> ABDE)
- Ví dụ: カドピタ9X25FBCR 250X 12 thì product_type chính là 2512 
+ Trường hợp 3: 
- Nếu category_small mà là BCP thì phải thêm chữ P vào đằng trước 
- Ví dụ: カドピタ9X25平BCP 550X22 thì category_small là BCP thì product_type là P5522 	
+ Trường hợp 4:  
- Trường hợp mà ở hàng sản phầm găp chữ JBCR hoặc JFE知多 hoặc col_maker mà là JFE-W thì bạn cần phải thêm chữ J vào đằng sau product_type [QUY TẮC QUAN TRỌNG KHÔNG ĐƯỢC BỎ QUA ]
- Ví dụ: カドピタGJ-R 9X50 4X18C 500X 22 JFE知多 thì product_type là 5022J 

■ product_size: chính là chữ đứng sau カドピタ hoặc GJ-R hoặc GJ, product_size sẽ có dạng AXBC (A, B, C đều là 1 số nguyên)
- Ví dụ: カドピタ9X25平BCR 250X 12 thì product_size chính là 9X25 
- product size sẽ nằm trong các giá trị sau: 9X25, 6X25, 8X24, 9X19, 9X32, 9X50, 12X25, 12X32, 12X50, 12X70, 16X32, 12X38, 5C 8X24, 5C 9X25, 18C 9X50, 3C 9X25

■ product_title: trường này sẽ nằm ngay đằng sau カドピタ trường này có thể là GJ-R hoặc GJ hoặc null (nếu trong trường hợp đằng sau không phải là GJ-R hoặc GJ thì bắt buộc là null) (đây là quy tắc quan trọng không được bỏ qua) 
- Nếu như product_title không phải GJ-R hoặc GJ thì bạn cứ mặc định product_title là null cho mình 
- Ví dụ: カドピタ9X25平BCR 250X 12 thì product_title chính là null, カドピタGJ-R 12X50 4X18C 400X 16 thì product_title chính là GJ-R,  カドピタGJ 12X50 4X18C 400X 16 thì product_title chính là GJ

■ col_maker: trường này sẽ đọc ở ngay bên dưới カドピタ và thường được căn giữa ở dưới cùng của cái ô đấy, trường này có thể sẽ được viết tay nên bạn phải đọc thật kỹ
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

■ mat_size: trường này sẽ nằm ngày đằng sau product_size và sẽ thường là 1 trong các giá trị sau đây: 3C, 5C, 18C, FB 
- Nếu trong trường hợp trong cái cell sản phầm đấy không có 3C, 5C, 18C thì mat_size chính là FB (Ví dụ: カドピタ9X25FBCR 300X 9 thì mat_size là FB)
- Nếu trong trường hợp trong cái cell sản phầm đấy không có 3C, 5C, 18C thì mat_size chính là 3C, 5C, 18C (Ví dụ: カドピタGJ-R 12X50 4X18C 400X 16 thì mat_size là 18C,  カドピタ9X25 50 BCR 250X 12 thì mat_size là 5C)

■ category_small: trường này sẽ có 2 trường hợp xảy ra đó là BCP hoặc BCR nếu như hàng sản phẩm đấy có chữ BCP thì category_small là BCP còn trên hàng sản phẩm đấy có chữ BCR thì category_small là BCR 
- Ví dụ: カドピタ9X25 50 BCR 300X 16 thì category_small là BCR カドピタ9X25平BCP 550X22 thì category_small là BCP 

■ オーダーNo (Mã đơn hàng)
- Trích xuất từ mục "発注No."
- Loại bỏ các số 0 ở đầu (ví dụ: 0020 -> 20).
- trường này thì bắt buộc phải lấy của trang tương ứng với cái bản ghi đấy chứ không được lấy của trang đầu tiên 

■ 工事名 (Tên công trình)

- Trích xuất từ nhãn: "工事名:"
- Trường này thì bắt buộc phải lấy của trang tương ứng với cái bản ghi đấy chứ không được lấy của trang đầu tiên 
- Phạm vi lấy dữ liệu:
+ Bắt đầu từ:
* Nội dung nằm ngay sau "工事名:" trên cùng một dòng, hoặc
* Dòng kế tiếp gần nhất nếu dòng chứa nhãn không có dữ liệu

+ Cho phép đọc tiếp các dòng phía dưới (dòng 2, 3, 4, ...) nếu:
* Nội dung vẫn thuộc cùng một cụm thông tin của 工事名
* Bao gồm cả các dòng bổ sung/ghi chú liên quan (ví dụ: nội dung trong ngoặc như "(事務所棟)")
* Không gặp điều kiện dừng

- Điều kiện dừng:
+ Dừng khi gặp:
* Trường "郵便番号"
* Dòng tiêu đề, hướng dẫn hoặc nội dung không liên quan

- Ràng buộc:
+ Tuyệt đối không lấy dữ liệu từ bất kỳ dòng nào phía trên "工事名:"
+ Không lấy dữ liệu từ các dòng/trường phía trên có chứa từ "業所"

- Điều kiện dữ liệu:
+ Nếu sau "工事名:" không có nội dung hợp lệ → trả về null
+ Nếu không xác định được rõ ràng giá trị từ OCR → trả về null

- Chuẩn hóa:
+ Nếu giá trị chứa chữ cái Latin hoặc chữ số → chuyển toàn bộ sang dạng full-width (全角)

- Làm sạch dữ liệu:
+ Nếu trong giá trị có chứa "裏当金" → loại bỏ cụm "裏当金" khỏi kết quả
+ Nếu trong giá trị có chứa "ウラ当" → loại bỏ cụm "ウラ当" khỏi kết quả
+ Giữ lại các nội dung trong ngoặc () nếu liên quan đến 工事名 (ví dụ: "(事務所棟)")
+ Loại bỏ khoảng trắng dư thừa ở đầu/cuối và nối các dòng thành một chuỗi

- [LOẠI TRỪ CỤ THỂ]
+ Nếu kết quả đọc được chính xác là:
* "一宮倉庫様分(０００００１００)" hoặc "(有)相澤鉄工 様分 （０００３９３６２）" hoặc "(株)京和建設 様分 (００３１９３１１)"
+ → bắt buộc trả về null

[QUAN TRỌNG - TRÁNH NHẦM LẪN]
- TUYỆT ĐỐI KHÔNG lấy nhầm data từ những dòng khác.
- TUYỆT ĐỐI KHÔNG lấy các dòng tiêu đề hoặc ghi chú chung như:
"要送り状FAX 発注番号明記のこと"
- Dòng này là header instruction, KHÔNG phải dữ liệu của 工事名.
- Nếu OCR không tìm thấy giá trị rõ ràng cho 工事名 => bắt buộc trả về null.
- trường này thì bắt buộc phải lấy của trang tương ứng với cái bản ghi đấy chứ không được lấy của trang đầu tiên 
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
