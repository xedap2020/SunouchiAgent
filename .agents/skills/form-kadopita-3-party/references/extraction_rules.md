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
        "supplier_code": null,
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
- Vì đây là tài liệu cực kỳ quan trọng nên bạn cần phải đọc thật kỹ không được sai 1 chữ hay 1 số nào 
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

■ オーダーNo (Mã đơn hàng) lấy của trang bảng sản phẩm đầu tiên 
- Trích xuất từ mục "注文 No."
- Loại bỏ các số 0 ở đầu (ví dụ: 0020 -> 20).

■ agent (hãng)
- Trường này mình để mặc định là 042011 

■ 工事名 (Tên công trình) lấy của trang bảng sản phẩm đầu tiên 
- Trường này trích xuất ra từ 3 mục 工事名 + 区分 + 使用部位 
- Ở mục 使用部位 thì sẽ bỏ đi 2 chữ cái cuối cùng chỉ lấy các chữ cái đầu tiên 
- Chuẩn hóa: Nếu giá trị chứa chữ cái Latin hoặc chữ số → chuyển toàn bộ sang dạng full-width (全角)
- Ví dụ: 工事名 là 内幸町南街区 và 区分 là FT工区23節外装間柱 và 使用部位 là サイコロ使用 thì 工事名 ở json sẽ là 内幸町南街区　FT工区　２３節　外装　間柱　サイコロ

■ 出荷日 (Ngày xuất hàng)
- Trích xuất từ mục "発送日:"
- Hoặc chính là chữ viết tay màu đỏ ở ngay bên trên mục 納入口 có dạng MM/DD lúc này YYYY chính là YYYY của 納期
- Nếu có chữ viết tay màu đỏ dạng "A/B出 C着" (ví dụ: "6/12出 15着") thì ngày xuất hàng (出荷日) sẽ là ngày A/B (2026/A/B)
- Định dạng nghiêm ngặt: YYYY/MM/DD

■ 納期 (Ngày giao hàng)
- Trích xuất từ mục "納入日" hoặc "納入口"
- Ở mục chỉ ghi dạng A月B日 (A, B là 1 số nguyên) bạn phải tự chuẩn hóa về định dạng đúng năm sẽ là năm hiện tại (năm nay là năm 2026)
- Định dạng nghiêm ngặt: YYYY/MM/DD 

■ supplier_code
- trường này thì trích xuất từ mục 納入先
- trong trường hợp ở mục 納入先 ghi là 当社 高山工場　海沼 thì supplier_code sẽ là 361116 
- trong trường hợp ở mục 納入先 ghi là 当社 長野工場　藤森 thì supplier_code sẽ là 361113 

■ customer_code thì để null 

============================================================
NHẬN DIỆN DÒNG SẢN PHẨM (ITEM ROW DETECTION)
============================================================
- Một hàng trên PDF = Một đối tượng JSON.

============================================================
QUY TẮC ƯU TIÊN TUYỆT ĐỐI (ABSOLUTE PRIORITY RULE)
============================================================
- TUYỆT ĐỐI KHÔNG xác định trường dữ liệu dựa trên định dạng ký tự.
- Gán dữ liệu nghiêm ngặt theo các nhãn mô tả (descriptors). Nếu không có mô tả khớp -> null.

============================================================
TRÍCH XUẤT THÔNG TIN SẢN PHẨM (PRODUCT META EXTRACTION)  (đây là phần quan trọng nhất trong file pdf file nào cũng sẽ có ít nhất 1 sản phẩm nên bạn phải phân tích thật kỹ không đọc bỏ qua cái này, CẦN PHẢI TRÍCH XUẤT TẤT CẢ CÁC HÀNG SẢN PHẨM CÓ TRONG ĐƠN KHÔNG ĐƯỢC BỎ QUA HÀNG NÀO) 
============================================================
■ product_type: [TRƯỜNG DỮ LIỆU SIÊU QUAN TRỌNG. YÊU CẦU TRÍCH XUẤT CHÍNH XÁC TUYỆT ĐỐI TỪNG CON SỐ, KHÔNG ĐƯỢC ĐOÁN MÒ, KHÔNG ĐƯỢC NHẦM DÒNG VÀ KHÔNG ĐƯỢC NHẦM LẪN GIỮA BCR/BCP. ]

[Nguồn dữ liệu]: Cột "コラム種類" (để xác định loại) và cột "コラムサイズ" (để lấy thông số số học) trên cùng một hàng (hàng nào phải đi với đúng số của hàng đó).
[Quy trình xử lý và Logic xác định]:
BƯỚC 1: Xác định loại Thép (BCP, BCR, hoặc STKR hoặc 385n) dựa vào cột "コラム種類":
- Nếu cột chỉ ghi duy nhất 1 chữ (BCR hoặc BCP hoặc STKR): Lấy luôn chữ đó.
- Nếu cột ghi chuỗi chứa cả 3 loại (BCP・BCR・STKR・テーパー・レジューサー): Bắt buộc phải quan sát hình ảnh để tìm ký tự được KHOANH TRÒN . (Ví dụ: Nếu BCP được khoanh thì coi như loại Thép là BCP. Nếu BCR được khoanh thì coi như loại Thép là BCR).
- Nếu cột ghi G385 hoặc N385 thì là 385n
BƯỚC 2: Trích xuất và xử lý chuỗi số từ cột "コラムサイズ":
Nhìn vào giá trị số của đúng hàng đó tại cột "コラムサイズ" và áp dụng nghiêm ngặt quy tắc cắt chuỗi sau:
- Trường hợp thông thường (Dạng: 3 chữ số x 3 chữ số x 2 chữ số. Ví dụ: 850×850×32): Lấy 2 số đầu tiên (85) và 2 số cuối cùng (32) để tạo thành chuỗi 4 chữ số (8532).
- Trường hợp đặc biệt (Dạng 4 chữ số: ABCD x FFG x KH. Ví dụ: 1000×1000×28): Lấy 2 số đầu tiên là "BC" (00) và 2 số cuối cùng là "KH" (28) để tạo thành chuỗi 4 chữ số (0028).
BƯỚC 3: Công thức thiết lập giá trị cuối cùng cho `product_type`:
- Nếu loại Thép xác định ở Bước 1 là BCP: Thêm chữ "P" vào trước chuỗi số tìm được ở Bước 2. (Ví dụ: P8532, P0028).
- Nếu loại Thép xác định ở Bước 1 là BCR hoặc STKR: Giữ nguyên chuỗi số tìm được ở Bước 2, KHÔNG thêm chữ P. (Ví dụ: 8532, 0028).
- Nếu loại thép xác định ở Bước 1 là 385n: Thì thêm chữ "G" vào trước chuối số tìm được ở Bước 2 (Ví dụ: 8532 thì sẽ là G8532, 0028 thì sẽ là G0028)
[CÁC ĐIỀU CẤM VÀ ĐIỀU KIỆN KIỂM TRA BẮT BUỘC TRƯỚC KHI TRẢ KẾT QUẢ]:
1. KIỂM TRA ĐỘ DÀI PHẦN SỐ: Phần số trong `product_type` bắt buộc ĐÚNG 4 chữ số (Không được thừa hay thiếu số 0. Ví dụ: 3009 là ĐÚNG, 30009 là SAI).
2. CẤM NHẦM LẪN HÀNG: Tuyệt đối không được lấy nhầm thông số của hàng này râu ông nọ cắm cằm bà kia sang hàng khác.
3. CẤM NHẦM SỐ ĐUÔI (Lỗi cực kỳ nghiêm trọng): Hãy nhìn thật kỹ độ dày (2 số cuối cùng). Hãy căng mắt quét từng pixel ảnh để đảm bảo tính chính xác của con số gốc trên file PDF.

■ product_size: trích xuất từ cột サイズ
- product_size sẽ có dạng AXBC (A, B, C đều là 1 số nguyên)
- Ví dụ: サイズ có giá trị là FB-9X25 thì product_size chính là 9X25 , nếu cột サイズ có giá trị là FB-12X50 thì product_size chính là 12X50 
- product size sẽ chỉ có thể là 1 trong các giá trị sau 1 trong các giá trị sau: 9X25, 6X25, 8X24, 9X19, 9X32, 9X50, 12X25, 12X32, 12X50, 12X70, 16X32, 12X38
- Bạn cần phải trích xuất chính xác giá trị có trong cột サイズ không được đoán bừa  

■ product_title: trường này sẽ trích xuất từ cột 面取り trường này có thể là GJ-R hoặc GJ hoặc Nothing 
- Nếu cột 右図 có giá trị là 右図 thì product_title là Nothing 
- Nếu như product_title không phải GJ-R hoặc GJ thì bạn cứ mặc định product_title là Nothing cho mình 

■ col_maker: trường này sẽ đọc ở cột コラムメーカー
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
- Nếu như mà gặp các chữ nằm trong các chữ mà mình đã chỉ định ở trên thì mình phải chuyển về định dạng giống với mấy chữ ở trên (ví du: ナカジマ -> ﾅｶｼﾞﾏ) [ĐÂY LÀ QUY TẮC QUAN TRỌNG KHÔNG ĐƯỢC BỎ QUA]
- Cái trường này sẽ có một số trường hợp là họ sẽ sửa hoặc bổ xung bằng mực đỏ nên bạn cũng phải để ý rất kỹ (ví dụ: mực in của file có thể là JFE nhưng nó hoàn toàn có thể thêm -w bằng mực đỏ vào để tạo thành JFE-W ), nếu mà có một cái mũi tên được viết bằng mực đỏ kẻ từ trên xuống thì có nghĩa là tất cả các sản phẩm bị kẻ cũng sẽ bị ảnh hưởng theo 

■ mat_size: trường này sẽ được viết tay ở cột 材質 và sẽ thường là 1 trong các giá trị sau đây: 3C, 5C, 18C, FB 
- trường này thông thường sẽ được viết tay bằng mực đỏ và sẽ chỉ ghi ở bản ghi đầu tiên rồi kéo 1 mũi tên màu đỏ thằng từ đầu đến chỗ bản ghi cuối cùng bị ảnh hưởng 
- Nếu trong trường hợp ở cột 材質 không có 3C, 5C, 18C, FB  hoặc không rơi vào trường hợp gạch đầu dòng bên trên thì thì mat_size mặc định sẽ là 3C 
- Nếu product_title là GJ-R và product_size là 12X50 thì mat_size sẽ là 18C 
- Nếu product_title là GJ và product_size là 12X50 thì mat_size sẽ là FB 

■ category_small (SIÊU QUAN TRỌNG):
   - Nguồn: Cột "コラム種類".
   - Quy trình xử lý nghiêm ngặt:
       1. [THỊ GIÁC] Quét khu vực cột "コラム種類" để tìm nét vẽ tay (khoanh tròn, oval, dấu tích).
       2. [XÁC ĐỊNH] Nếu thấy một trong các ký tự `BCP`, `BCR`, hoặc `STKR` được khoanh tròn:
          -> category_small = Ký tự được khoanh tròn đó (Ví dụ: thấy BCP được khoanh -> "BCP").
       3. [FALLBACK] Nếu không có khoanh tròn nào:
          -> Đọc văn bản thuần. Nếu chỉ có 1 loại -> Lấy loại đó. Nếu có nhiều loại -> Dùng logic mặc định (ưu tiên BCP nếu không rõ).
    - Nếu như trên cộ ghi G385 hoặc N385 thì category_small là n385 

■ オーダーNo (Mã đơn hàng)
- Trích xuất từ mục "発注No."
- Loại bỏ các số 0 ở đầu (ví dụ: 0020 -> 20).
- trường này thì bắt buộc phải lấy của trang tương ứng với cái bản ghi đấy chứ không được lấy của trang đầu tiên 

■ 工事名 (Tên công trình)
- Trường này trích xuất ra từ 3 mục 工事名 + 区分 + 使用部位 
- Ở mục 使用部位 thì sẽ bỏ đi 2 chữ cái cuối cùng chỉ lấy các chữ cái đầu tiên 
- Chuẩn hóa: Nếu giá trị chứa chữ cái Latin hoặc chữ số → chuyển toàn bộ sang dạng full-width (全角)
- Ví dụ: 工事名 là 内幸町南街区 và 区分 là FT工区23節外装間柱 và 使用部位 là サイコロ使用 thì 工事名 ở json sẽ là 内幸町南街区　FT工区　２３節　外装　間柱　サイコロ
- trường này thì bắt buộc phải lấy của trang tương ứng với cái bản ghi đấy chứ không được lấy của trang đầu tiên 

■ is_processing
- trường này để là True 

■ 員数
- trường này trích xuất từ cột 数量 chỉ lấy số không lấy chữ cái đơn vị 

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
