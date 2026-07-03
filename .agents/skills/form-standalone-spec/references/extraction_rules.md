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
- Sản phẩm thì bạn phải đọc của tất cả các cái trang không phải là đọc của 1 trang 

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
TRÍCH XUẤT THÔNG TIN SẢN PHẨM (PRODUCT META EXTRACTION)  (đây là phần quan trọng nhất trong file pdf file nào cũng sẽ có ít nhất 1 sản phẩm nên bạ phải phân tích thật kỹ không đọc bỏ qua cái này 
============================================================
■ product_title: trường này thì để null lúc nào cũng là null 
■ product_type: trường này thì lấy data ở cái cột 名称
	+ trong trường hợp cột 名称 có 1 trong các cái chữ ST, STEX, 特ST, 特STEX, STミニ, EXミニ, 特STミニ, 特EXミニ, EX, 特EX, 特AP, AP, CR-F, L型, K型 thì data của product_type lấy ở cột 名称 nhưng chỉ lấy chữ không lấy số (vd:  AP36 thì lấy AP, EX26 thì lấy EX, CRF ウR105 thì product_type là CR-F, K型 thì product_type là K型) 
	+ lưu ý 名称 là APRON thì product_type chính là AP 
    + nếu product_type bạn đọc ra là K thì phải đổi về  K型
	+ trong đơn có thể sẽ có trường hợp là người làm đơn họ gạch đi và viết lại bằng mực đỏ nên bạn cũng phải để ý thật kỹ 
	+ trường này trong trường hợp mà ở cột 摘要 có chữ 180型 thì product_type sẽ là B-180 hoặc ở cột 摘要 có chữ 120型 thì product_type B-120
	+ trường hợp  product_type là FB thì product_size sẽ là 9X25 hoặc 9X32 hoặc 9X50 và 長さ sẽ là số còn lại nằm ở cột 長 サ 
	+ trong trường hợp mà ở bên cạnh hàng sản phẩm có chữ NS45° thì product_type là NS45° (lưu ý: đôi khi họ sẽ viết tay và viết 1 mũi tên đỏ kéo dài từ sản phẩm NS45° đầu tiên đến sản phẩm NS45° cuối cùng thì bạn phải lấy tất cả các sản phẩm nằm trong khoảng mũi tên màu đỏ)
	+ trong trường hợp có chữ CR hoặc NS hoặc NS15° (trừ CR-F và NS45°) (vị trí chữ CR hoặc NS hoặc NS15° có thể nằm ở cùng hàng với hàng sản phẩm nhưng cũng có thể nằm ở bên dưới các hàng sản phẩm gần bản vẽ kỹ thuật, lúc này tất cả các bản ghi bên trên của trang đấy sẽ bị ảnh hưởng, chữ CR, NS, NS15° có thể viết tay)  thì product_type là FB và product_size sẽ có 2 trường hợp xảy ra
		- nếu ký tự ở 長 サ mà nhỏ hơn 80 thì product_size sẽ là là 9X25X hoặc 9X32X tùy thuộc vào hàng sản phẩm đấy hiển thị 9X25 hay 9X32  (Lưu ý : product_size lúc này sẽ chỉ là 9X25X  hoặc 9X32X  không X thêm số gì vào sau) và 長さ sẽ là con số ở cột 長 サ
		- nếu ký tự ở 長 サ mà lớn hơn 80 thì product_size là 9X25Xsố ở cột 長 サ hoặc 9X32Xsố ở cột 長 サ tùy thuộc vào hàng sản phẩm đấy hiển thị 9X25 hay 9X32 
	+ trường hợp nếu gặp các hàng sản phẩm là LL-A (L 65x65x6) và LL-B (L 50x50x6) thì trích xuất thành 1 hàng sản phẩm trong json có: product_type là null, product_size là null, product_title là null, và category_small là "LL蝶番"
	+ trường hợp nếu gặp 2 hàng sản phẩm 1 cái là LL-A 65X65X6 và 1 cái là LL-B 50X50X6 thì 2 cái hàng sản phẩm đấy bạn sẽ trích xuất ra 1 hàng sản phẩm trong json có: product_type là null, product_size là null, product_title là null, và category_small là "LL蝶番"
	+ trường hợp mà ngay ở dưới các hàng sản phẩm có chữ CR-F thì product_type của tất cả các sản phẩm bên trên là CR-F 
	+ đôi khi sẽ có những trường hợp là người ta gạch product_type cũ được in bằng mực đen đi và ghi lại bằng mục đỏ thì bạn phải lấy product_type được ghi lại bằng mục đỏ (ví dụ họ hoàn toàn có thể gạch bỏ EX đi và ghi 1 loại product_type khác ở bên cạnh như ST chẳng hạn , product_type mới được ghi lại có thể nằm ở bên trên, bên cạnh hoặc bên dưới  product_type cũ không nhất thiết phải cùng hàng đấy)
	+ Một số  product_type khác có thể gặp: B-120, B-180, VS, VM, VL, VB-55, VB-75, VB-110, VWS, VW, VWB, VM-30, VL-30, VB-5530, VS-4, VM-4, VL-4, VL-25, VB-25, FS, FM, FL, FB-55, FB-75, FB-110, FWS, FW, FWB, FWN-20, FWN-32, FM-30, FL-30, FB-5530, FS-4, FM-4, FL-4, FM-25, FL-25, FB-25, FB-7525, FM-328, FL-340, SC, SC-3T, SC-4T, SC-5, RT-25, A, AW, AW-2, A-50, A-80, A-110, DF-40, DF-55, DF-75, DF-120, CP-40, CP-50, CP-100, YV-25, FMG-28, FHT-30, YHR-25N, YHR-32N, YHR-50N, ND, TR-25, TR-40, VSHD, VLHD, JS, L-1, L-2, LB-12, LB-17, LCB-19, LCB-20, LB-23T, LCB-27T, LCB-29T, LB-46T, RV-3245, RV-3250, RV-3255, SRF-30, SRF-40, CAT-30, NST-1, VW-32R, VW-55R, CAT-16, BPX140-35, IT-50, PSK-50, PSK-503, SS, V-S, V-M, V-L, F-S, F-M, F-L, CBW-30NP, TGW-30L, CBW-G34NP, CBW-F40NP, CBW-271NP, CBW-276NP, CBW-TR90NP, CBW-07φNP, CBW-10φNP, CBW-12φNP, CBW-15φNP, CBW-S01NP, CBW-S02NP, CBW-S03NP, CBW-3C, CBW-36, CBW-J27, CBW-TR901, CBWR300TR, CBWR300G35, CBX-S02, CBX-F30P, CBX-30KG, CBM8067, CBX-WTD16, CBX-WTD41, CBX-WTD51, P-S, P-L, TC-25, TC-40
	+ Nếu gặp các chữ giống với một số product_type có thể gặp mà các chữ đấy không có dấu gạch ngang ở giữa thì bạn tự chủ động thêmdấu gạch ngang vào (ví dụ: CP40 -> CP-40)
■ product_size:
	+ trong trường hợp product_type là AP, CR-F thì product_size lấy ở cột 品名 và 長サ, product_size lúc này sẽ có dạng 品名 là 16X38 thì  (ví dụ: 品名 là 16X38 và 長サ là 50 thì product_size lúc này là 16X38X50) 
	+ trong trường hợp product_type là L型, EX, ST thì product_size lấy ở 品名 và cột 長サ. Nếu cột 品名 có chứa chiều rộng (thường ghi dạng PL [độ dày] x 38) và cột 長サ ghi góc vát (dạng [góc]°), thì product_size chỉ lấy dạng [độ dày]X[góc vát]° (bỏ qua kích thước chiều rộng 38). Ví dụ: 品名 là PL 12 x 38 và 長サ là 35° thì product_size là 12X35°. Ví dụ: 品名 là PL 16 x 38 và 長サ là 45° thì product_size là 16X45°.
	+ trong trường hợp product_type là L型, EX thì product_size lấy ở 品名, product_size lúc này sẽ có dạng AXB° (A,B là 1 số nguyên, ví dụ: 品名 là 22X45° thì product_size là 22X45°)
	+ trong trường hợp file pdf không có dấu X thì bạn phải tự bổ sung vào
	+ trong trường hợp product_type là K型 thì product_size lấy ở 品名 nhưng chỉ lấy số đầu tiên (ví dụ: 品名 là 32  45/60 thì product_size là 32)
	+ trong trường hợp product_type là K thì product_size chính là cái số ở trong 名称 (ví dụ: 名称 là K11 thì product_type là K còn product_size là 11) 
	+ trong trường hợp product_type là EX đôi khi cũng gặp phải trường hợp đó là ở 品名 chỉ có 1 số và chữ 度 (ví dụ: 35度) thì lúc này product_size chính là cái số ở 名称 X với số ở 品名 thêm ký tự độ (ví dụ: 名称 là EX25 còn 品名 là 35度 thì lúc này product_type là EX còn product_size là 25X35°)
	+ dấu nhân là chữ X chữ ko phải là x, lúc nào cũng phải dùng X không được x VD: AxBxC phải đổi thành AXBXC 
- Cái dấu 〃 tức là giá trị giống hệt với cái hàng bên trên của cái cột đấy (đây là quy tắc quan trọng không được bỏ qua)
- nếu ở trên bảng có chữ viết tay thì cũng phải phân tích thật kỹ xem có phải sản phẩm ko nếu là sản phẩm thì cũng phải đưa vào json, các cái chữ viết tay thông tường sẽ khá xấu nên phải đọc thật kỹ không được để sai 
- có nhiểu trường hợp là sẽ có cái kiểu viết tay ý các cái bản ghi giống nhau ở trong file mà lặp đi lặp lại thì họ chỉ viết mỗi dòng đầu tiên thôi sau đó nó sẽ kẻ 1 dòng kẻ từ cái bản ghi mẫu từ trên xuống cái hàng cuối cùng mà bị lặp lại (đây là quy tắc quan trọng không được bỏ qua)
- các cái chữ viết tay thường màu đỏ
- product_size được sắp xếp theo thứ tự tăng dần Nếu đang là A X B X C (với A, B, C là các số), sắp xếp lại thành {số nhỏ nhất} X {số lớn hơn} X {số lớn nhất}
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

■ 員数: Extract the numeric value from the "数量" column.

■ 長さ: trường này mặc định để null trừ trường hợp product_type là FB thì product_size sẽ là 9X25 hoặc 9X32 (tùy vào hiển thị của sản phẩm đấy trên đơn là 9X25 hay 9X32 ) và 長さ sẽ là số còn lại nằm ở cột 長 サ 

■ is_processing
- trường này nếu trong trường hợp mà product_type là CR-F hoặc FB hoặc NS45°  thì là TRUE còn lại là FALSE 
- Trường hợp đặc biệt nếu product_type là FB và product_size của nó là 9X25X hoặc 9X32X hoặc 9X25 hoặc 9X32 hoặc 9X50  thì is_processing là FALSE 

============================================================
CHỐT AN TOÀN DỮ LIỆU (PRODUCT META SAFETY LOCK)
============================================================
- product_type KHÔNG ĐƯỢC trùng với mã sản phẩm (商品コード).
- KHÔNG tự ý suy luận dữ liệu không có sẵn trên PDF.
- KHÔNG kết hợp hoặc "mượn" dữ liệu giữa các hàng khác nhau.
- Nếu không chắc chắn hoặc mơ hồ -> Trả về null.
- 長さ: trong trường hợp product type là FB thì cái 長さ để null 
- 長さ: trong trường hợp đặc biệt product_type là FB và product_size là 19X25X hoặc 9X32X hoặc 9X25 hoặc 9X32 hoặc 9X50 thì 長さ sẽ là ký tự của cột 長 サ 
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
