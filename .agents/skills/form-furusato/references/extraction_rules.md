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
    "agent": null,
    "comment": null 
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
- Trang nào đã bị gạch bỏ thì ko cần đọc 

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
- "搬入口" PHẢI LÀ null.
- "代理店" PHẢI LÀ null.
- "受注担当者" PHẢI LÀ null.

============================================================
QUY TẮC TRÍCH XUẤT PHẦN HEADER
============================================================

■ 受注区分 (Phân loại nhận đơn)
- Trích xuất từ con dấu màu đỏ tròn hoặc văn bản viết tay ở góc trên bên phải/trên cùng. Nếu thấy con dấu tròn đỏ chứa chữ "ア" và chữ viết tay "本文" bên cạnh, hoặc có dấu "本受注", gán "本受注". Nếu không có, gán null.

■ 出荷倉庫 (Kho xuất hàng)
- Trích xuất từ ký tự viết tay hoặc con dấu tròn màu đỏ ở góc trên bên phải. Nếu thấy con dấu tròn đỏ ghi chữ "ア", gán "綾瀬倉庫". Nếu không tìm thấy, gán null.

■ shipping_warehouse
- Đồng bộ với giá trị của "出荷倉庫".

■ オーダーNo (Mã đơn hàng)
- Trích xuất từ mục "発注No."
- Loại bỏ các số 0 ở đầu (ví dụ: 0020 -> 20).

■ agent (hãng)
- Trích xuất từ mục "発注No."
- Loại bỏ các số 0 ở đầu (ví dụ: 0020 -> 20).
- Chỉ lấy 2 số đầu tiên (ví dụ: 123456 -> 12)

■ comment 
	- Trường này để chữ F. 

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
		* "一宮倉庫様分(０００００１００)"
		* "(有)相澤鉄工 様分 （０００３９３６２）"
		* "(株)京和建設 様分 (００３１９３１１)"
		* Bất kỳ chuỗi nào có dạng "XXX 様分 (số)" hoặc "XXX様分(số)"
		  (tức là tên công ty/cá nhân + 様分 + mã số trong ngoặc)
	+ → bắt buộc trả về null
	[QUAN TRỌNG - TRÁNH NHẦM LẪN]
	- TUYỆT ĐỐI KHÔNG lấy các dòng tiêu đề hoặc ghi chú chung như:
	  "要送り状FAX 発注番号明記のこと"
	- Dòng này là header instruction, KHÔNG phải dữ liệu của 工事名.
	- TUYỆT ĐỐI KHÔNG lấy dòng chứa thông tin 納入先名
	  (dạng: tên công ty + 様 + mã số, ví dụ: "(有)越川鋼業物産 様分 (00329114)")
	  vì đây là thông tin người nhận hàng, KHÔNG phải 工事名.
	- Nếu OCR không tìm thấy giá trị rõ ràng cho 工事名 → bắt buộc trả về null.
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
- Trích xuất từ mục "着日:"
- Định dạng nghiêm ngặt: YYYY/MM/DD

■ supplier_name (Địa điểm giao hàng)
- Trường này sẽ có 2 trường hợp xảy ra:
+ Trường hợp 1: nếu như mà ở mục 納入先名 có chữ ㈱ thì làm theo các bước dưới đây 		
Trích xuất từ mục: 納入先名:
   BƯỚC 1 — Lấy toàn bộ dòng sau nhãn "納入先名:".
   BƯỚC 2 — Loại bỏ phần văn bản kết thúc bằng chữ "様".
   BƯỚC 3 — Chuẩn hóa danh xưng công ty:
   - 株式会社 biến thể: 株式会社, (株), （株）, ㈱ -> Chuyển tất cả thành: (株)
   - 有限会社 biến thể: 有限会社, (有), （有）, ㈲ -> Chuyển tất cả thành: (有)
   - Nếu danh xưng ở đầu: 株式会社山田 -> ㈱山田
   - Nếu danh xưng ở cuối: 山田株式会社 -> 山田㈱
   BƯỚC 4 — Loại bỏ các hậu tố hành chính: 事務所, 本社, 本店, 管理部, 営業部.
   BƯỚC 5 — CHỈ GIỮ LẠI các hậu tố địa điểm: 工場, ヤード, センター, 倉庫, 置場.
   BƯỚC 6 — Loại bỏ khoảng trắng thừa ở chữ (株) và dòng chữ phía sau (vd: (株) 中瀬鐵工所 第二工場 -> (株)mã hoặc tên công ty...). (vd: (株) 中瀬鐵工所 第二工場 -> (株)mã hoặc tên công ty...). (vd: (株) 中瀬鐵工所 第二工場 -> (株)中瀬鐵工所 第二工場).
   BƯỚC 7 - Nếu gặp chữ 止 ở cuối cùng thì bỏ đi, nếu gặp chữ (旧:K-TECH) thì bỏ đi 
Ví dụ:
   冬木工業（株）倉賀野工場 → 冬木工業（株） 倉賀野工場
   山田㈱東京倉庫 → 山田㈱ 倉庫
+ Trường hợp 2: nếu như mà ở mục 納入先名 không có chữ ㈱ thì supplier_name sẽ là chữ フルサト工業(株) cộng với dữ liệu trích xuất từ mục 納入先名
Ví dụ: 納入先名 là 北九州営業所　様 thì supplier_name sẽ là フルサト工業(株) 北九州営業所
Lưu ý: 
— Loại bỏ các hậu tố hành chính: 事務所, 本社, 本店, 管理部, 営業部.
— CHỈ GIỮ LẠI các hậu tố địa điểm: 工場, ヤード, センター, 倉庫, 置場.
— Loại bỏ khoảng trắng thừa.
— Nếu gặp chữ 止 ở cuối cùng thì bỏ đi

■ supplier_postal_code
- Trường này trích xuất ở mục 郵便番号 ở trên header
- Định dạng của trường này là XXX-XXXX, nếu như trên file pdf chỉ có 1 dãy số kiểu XXXXXXX thì bạn phải chuẩn hóa về định dạng XXX-XXXX

■ supplier_tel 
- Trường này trích xuất ở mục 納入先Tel ở trên header
- Định dạng của trường này là XXX-XXX-XXXX hoặc XXXX-XX-XXXX, nếu như trên file pdf chỉ có 1 dãy số kiểu XXXXXXXXXX thì bạn phải chuẩn hóa về định dạng XXX-XXX-XXXX hoặc XXXX-XX-XXXX

■ supplier_code
- Gán giá trị null để hệ thống tự động tra cứu từ database dựa trên tên supplier_name (không được ghi đè cứng bằng null sau khi đã tra cứu).

■ customer_name1 và customer_name2 thì để là null 

============================================================
NHẬN DIỆN DÒNG SẢN PHẨM (ITEM ROW DETECTION)
============================================================
- Một hàng chỉ được tính là tồn tại nếu CẢ 数量 (Số lượng) VÀ 単価 (Đơn giá) đều có giá trị.
- Một hàng trên PDF = Một đối tượng JSON.

============================================================
TRÍCH XUẤT THÔNG TIN SẢN PHẨM (PRODUCT META EXTRACTION)
============================================================

■ product_type (Quy tắc trích xuất & Chuẩn hóa)
Định nghĩa: Ký hiệu phân loại ngắn trong mô tả sản phẩm.
Ràng buộc: Độ dài 1–12 ký tự. Không có khoảng trắng.
- KHÔNG ĐƯỢC chứa "MM", "mm", hoặc dấu độ "°".
- KHÔNG ĐƯỢC cắt bỏ các hậu tố tiếng Nhật dính liền (ví dụ: 型, ミニ, 枠) trừ trường hợp B-120型 và B-180型 thì chỉ lấy B-120 và B-180 .
Chuẩn hóa ưu tiên cao:
- Dòng CR-F: Nếu mô tả chứa cả "CR" và "F", nếu gặp CRF thì product_type là CR-F 
- Nếu gặp chữ CR thì product_type là FB và product_size sẽ có 2 trường hợp xảy ra 
	+ nếu ký tự đằng sau chữ L mà nhỏ hơn 80 thì product_size sẽ là là 9X25X hoặc 9X32X tùy thuộc vào hàng sản phẩm đấy hiển thị 9X25 hay 9X32 
	+ nếu ký tự đằng sau chữ L mà lớn hơn 80 thì product_size là 9X25Xsố đằng sau chữ L hoặc 9X32Xsố đằng sau chữ L tùy thuộc vào hàng sản phẩm đấy hiển thị 9X25 hay 9X32 
	+ Trường hợp đặc biệt nếu gặp chữ CR và 15.5R hoặc CR và R15.5 thì product_type là CR-F
- Dòng AP: Nếu mã là "AP" + số (ví dụ: AP36, AP48) -> CHỈ lấy "AP" làm product_type.
- Dòng CP: Nếu mã là "CP" + số nhưng thiếu dấu gạch ngang (ví dụ: CP40) -> Phải chuyển thành "CP-40".
Các mẫu phổ biến: EX, SC, B-120, L型, CP-40, AP, RGｸﾘｯﾌﾟ, VS, VM, VB-55, VWS, CBW-S02NP, TGW-30, F-S, LB-12, A-80, STミニ, EXミニ ...
- Lưu ý không được nhầm product_type từ STミニ chứ không STﾐﾆ,...
- Bạn không được nhầm chữ L型 với chữ レ型, trường hợp mà bạn đọc ra được chữ レ型 thì phải chuẩn hóa về L型 ngay 
- product_type sẽ có dạng là chữ cái viết hoa (A-Z), số (0-9) và dấu gạch ngang (-) và 1 số ký tự tiếng nhật khác (ví dụ: 型, ｸﾘｯﾌ
- trong trường hợp mà có chữ 流止め thì product_type chính là 特AP còn product_size chính là chữ bên cạnh có dạng AXBXC (A, B, C là 1 số) 
- trong trường hợp mà có chữ ストレート 9X25 平 SN490B L thì product_type chính là FB 
- nếu gặp chữ RGクリップ thì chuyển về RGｸﾘｯﾌﾟ
- nếu gặp DC丸AXB (A, B là số) thì product_type là DC và product_size là AXB (Ví dụ: ボンDC丸6.5X355 thì product_type là DC và product_size là 6.5X355)
- Một số product_type khác có thể gặp: B-120, B-180, VS, VM, VL, VB-55, VB-75, VB-110, VWS, VW, VWB, VM-30, VL-30, VB-5530, VS-4, VM-4, VL-4, VL-25, VB-25, FS, FM, FL, FB-55, FB-75, FB-110, FWS, FW, FWB, FWN-20, FWN-32, FM-30, FL-30, FB-5530, FS-4, FM-4, FL-4, FM-25, FL-25, FB-25, FB-7525, FM-328, FL-340, S-C, SC-3T, SC-4T, SC-5, RT-25, A, AW, AW-2, A-50, A-80, A-110, DF-40, DF-55, DF-75, DF-120, CP-40, CP-50, CP-100, YV-25, FMG-28, FHT-30, YHR-25N, YHR-32N, YHR-50N, ND, TR-25, TR-40, VSHD, VLHD, JS, L-1, L-2, LB-12, LB-17, LCB-19, LCB-20, LB-23T, LCB-27T, LCB-29T, LB-46T, RV-3245, RV-3250, RV-3255, SRF-30, SRF-40, CAT-30, NST-1, VW-32R, VW-55R, CAT-16, BPX140-35, IT-50, PSK-50, PSK-503, SS, V-S, V-M, V-L, F-S, F-M, F-L, CBW-30NP, TGW-30L, CBW-G34NP, CBW-F40NP, CBW-271NP, CBW-276NP, CBW-TR90NP, CBW-07φNP, CBW-10φNP, CBW-12φNP, CBW-15φNP, CBW-S01NP, CBW-S02NP, CBW-S03NP, CBW-3C, CBW-36, CBW-J27, CBW-TR901, CBWR300TR, CBWR300G35, CBX-S02, CBX-F30P, CBX-30KG, CBM8067, CBX-WTD16, CBX-WTD41, CBX-WTD51, P-S, P-L, TC-25, TC-40
- Nếu gặp các chữ giống với một số product_type có thể gặp mà các chữ đấy không có dấu gạch ngang ở giữa thì bạn tự chủ động thêm dấu gạch ngang vào (ví dụ: CP40 -> CP-40)

■ product_size (Chuẩn hóa kích thước động)
Trường hợp đặc biệt 
- Dòng AP:
	Mẫu: "AP" + <số> + "MM"
	Trích xuất: Lấy <số> và thêm số 38 và 50 vào kết quả, kết quả sẽ có dạng AXBXC (A, B, C là 1 số nguyên; A, B, C luôn có dạng tăng dần)
	Ví dụ: AP36MM -> 38X36X50 -> 36X38X50 ; AP48MM -> 38X48X50 -> 38X48X50; AP60MM -> 38X50X60. 
- Trong trường hợp mà product_type là CR-F thì product_size sẽ là AXBX with cái số đằng sau chữ L (ví dụ: スノウチノンスカCRF 9X25 SN490B L60 thì product_size là 9X25X60)
	+ Trường hợp đặc biệt dòng AP: nếu gặp エンドタブ AXB SN490B CMM AP (A, B , C là số ) thì product_size sẽ là AXBXC (Nếu A, B, C chưa phải dạng tăng dần thì bạn phải chuẩn hóa về dạng tăng dần) (Ví dụ: エンドタブ 38X12 SN490B 28MM thì product_size sẽ là 38X12X28 -> 12X28X38)

Trường hợp tiêu chuẩn:
	Mẫu: <số>MM và <số>°
	Chuẩn hóa: Định dạng thành <số>X<số>°.
	Ví dụ: 25MM 35° -> 25X35°.

Trường hợp có chiều dài (Mẫu chữ L):
	Mẫu: Nếu kích thước (ví dụ: 9X25) có kèm theo chữ "L" + <số> (ví dụ: L260).
	Chuẩn hóa: Nối chiều dài bằng dấu "X".
	Ví dụ: "9X25 ... L260" -> 9X25X260.
Nếu kích thước 12X32 (ví dụ: 12X32 ... L260) thì là 1 trường hợp đặc biệt khác lúc đấy product_size sẽ là 12X32X
	
- trong trường hợp product_type là FB thì product_size chính là AXBXC thì phải chuẩn hóa lại cho các cái con số của nó tăng dần (A, B, C là 1 số, C thường nằm sau chữ L) (VD: nếu thấy chữ ストレート 9X25 平 SN490B L680 thì product_size chính là 9X25X680)
- trong trường hợp nếu thấy chữ ストレート 12X32 平 SN490B L680 thì product_type là FB và product_size chính là 12X32X 
- các cái trường trong product_size mà có dạng AXBXC thì phải chuẩn hóa lại cho các cái con số của nó tăng dần (VD: A>B>C thì phải đổi lại thành CXBXA)
- trong trường hợp mà product_type là RGｸﾘｯﾌﾟ thì product_size là 6 hoặc 7.
Quy tắc định dạng: Bắt buộc viết hoa chữ X, không có khoảng trắng, giữ nguyên ký hiệu độ ° nếu có.
- trong trường hợp product_type là K型 thì product_size sẽ chỉ là 1 con số (ví dụ: product_type là K型 product_size sẽ là 36 không phải 36MM)
- Nếu product_type mà là CR thì product_size là 9X25X (Lưu ý : product_size lúc này sẽ chỉ là 9X25X không X thêm số gì vào sau)

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
	* "一宮倉庫様分(０００００１００)"
	* "(有)相澤鉄工 様分 （０００３９３６２）"
	* "(株)京和建設 様分 (００３１９３１１)"
	* Bất kỳ chuỗi nào có dạng "XXX 様分 (số)" hoặc "XXX様分(số)"
	  (tức là tên công ty/cá nhân + 様分 + mã số trong ngoặc)
+ → bắt buộc trả về null
[QUAN TRỌNG - TRÁNH NHẦM LẪN]
- TUYỆT ĐỐI KHÔNG lấy nhầm data từ những dòng khác.
- TUYỆT ĐỐI KHÔNG lấy các dòng tiêu đề hoặc ghi chú chung như:
  "要送り状FAX 発注番号明記のこと"
- Dòng này là header instruction, KHÔNG phải dữ liệu của 工事名.
- TUYỆT ĐỐI KHÔNG lấy dòng chứa thông tin 納入先名
  (dạng: tên công ty + 様 + mã số, ví dụ: "(有)越川鋼業物産 様分 (00329114)")
  vì đây là thông tin người nhận hàng, KHÔNG phải 工事名.
- Nếu OCR không tìm thấy giá trị rõ ràng cho 工事名 → bắt buộc trả về null.
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
- nếu product_type mà là FB, CR-F thì is_processing phải là TRUE còn nếu như product_type mà không phải là FB thì bắt buộc is_processing phải là FALSE 
- trường hợp đặc biệt nếu product_type là FB và product_size là 12X32X hoặc 9X25X hoặc 9X32X hoặc 9X25 hoặc 9X32 hoặc 9X50 thì is_processing là FALSE 

============================================================
CHỐT AN TOÀN DỮ LIỆU (PRODUCT META SAFETY LOCK)
============================================================
- product_type KHÔNG ĐƯỢC trùng với mã sản phẩm (商品コード).
- KHÔNG tự ý suy luận dữ liệu không có sẵn trên PDF.
- KHÔNG kết hợp hoặc "mượn" dữ liệu giữa các hàng khác nhau.
- Nếu không chắc chắn hoặc mơ hồ -> Trả về null.
- 長さ: trong trường hợp product type là FB, CR-F thì cái 長さ để null 
- 長さ: trong trường hợp đặc biệt product_type là FB và product_size là 12X32X hoặc 9X25X thì 長さ chính là giá trị nằm sau chữ L (ví dụ: 12X32 ... L260 thì 長さ là 260)

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
