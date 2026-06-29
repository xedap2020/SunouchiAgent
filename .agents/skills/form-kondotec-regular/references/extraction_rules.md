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
                    "supplier_tel": null 
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

■ customer_name1 và customer_name2 (Thông tin khách hàng đặt hàng)
- Mục tiêu: Trích xuất tên công ty tổng và tên chi nhánh/văn phòng thực hiện đơn hàng.
- Vị trí nhận diện: Tìm cụm thông tin nằm gần logo "KONDOTEC" hoặc tên công ty in ở phần Header (thường có tên công ty kèm theo địa chỉ và số điện thoại chi nhánh).
1. Quy tắc trích xuất customer_name1 (Tên công ty):
   - Tìm dòng văn bản chứa tên công ty chủ quản. 
   - Thông thường là "コンドーテック株式会社" (hoặc có thể viết tắt là コンドーテック(株)).
   - Lưu ý: Luôn chuẩn hóa các ký tự viết tắt thành dạng đầy đủ: "(株)" -> "株式会社".
   - Ví dụ: "コンドーテック(株)九州営業所" -> Trích xuất customer_name1 là "コンドーテック株式会社".

2. Quy tắc trích xuất customer_name2 (Chi nhánh/Văn phòng):
   - Trích xuất tên chi nhánh hoặc phòng giao dịch đi kèm ngay sau tên công ty hoặc nằm ở dòng ngay dưới.
   - Các từ khóa nhận diện: 営業所 (Văn phòng kinh doanh), 支店 (Chi nhánh).
   - Ví dụ: 
     + "コンドーテック(株)九州営業所" -> customer_name2 là "九州営業所".
     + "コンドーテック 北九州営業所" -> customer_name2 là "北九州営業所".
     + "コンドーテック(株)北関東支店" -> customer_name2 là "北関東支店" (Nếu đáp án mong muốn là "営業所" như ví dụ bạn đưa ra cho Ảnh 10, hãy ưu tiên giữ nguyên hậu tố trên PDF là "支店" trừ khi có quy định đổi tên cụ thể).

3. Quy tắc chuẩn hóa đặc biệt:
   - Nếu PDF ghi "コンドーテック" (Katakana), hãy đảm bảo trích xuất chính xác như văn bản trên file.
   - Loại bỏ các thông tin không liên quan như mã số, số điện thoại hoặc thời gian in đi kèm trên cùng một dòng.
   - Nếu không tìm thấy thông tin chi nhánh, gán customer_name2 là null.
   
■ customer_code
- Trường này thì để trống 

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

■ product_type (Quy tắc trích xuất & Chuẩn hóa): trường này trích xuất từ cột 品名・規格・サイズ
Định nghĩa: Ký hiệu phân loại ngắn trong mô tả sản phẩm.
Ràng buộc: Độ dài 1–12 ký tự. Không có khoảng trắng.
- KHÔNG ĐƯỢC chứa "MM", "mm", hoặc dấu độ "°".
- KHÔNG ĐƯỢC cắt bỏ các hậu tố tiếng Nhật dính liền (ví dụ: 型, ミニ, 枠) trừ dòng AP.
Chuẩn hóa ưu tiên cao:
- Dòng CR-F: Nếu mô tả chứa cả "CR" và "F" hoặc nếu chỉ có chữ "CR" (bao gồm cả chữ viết tay như CRF), luôn chuẩn hóa thành "CR-F".
- Dòng AP: Nếu mã là "AP" + số (ví dụ: AP36, AP48, AP型) -> CHỈ lấy "AP" làm product_type.
- Dòng CP: Nếu mã là "CP" + số nhưng thiếu dấu gạch ngang (ví dụ: CP40) -> Phải chuyển thành "CP-40".
Các mẫu phổ biến: EX, ST, SC, B-120, L型, L, K型, STEX, 特ST, 特STEX, STミニ, EXミニ, 特STミニ, 特EXミニ, KEX, 特KEX, 特EX, 特AP, 特L型, 特K型, 
CP-40, AP, RGｸﾘｯﾌﾟ, ＬＬタイプ, VS, VM, VB-55, VWS, CBW-S02NP, TGW-30, F-S, LB-12, A-80, ...
- Bạn không được nhầm chữ L型 với chữ レ型, trường hợp mà bạn đọc ra được chữ レ型 thì phải chuẩn hóa về L型 ngay 
- product_type sẽ có dạng là chữ cái viết hoa (A-Z), số (0-9) và dấu gạch ngang (-) và 1 số ký tự tiếng nhật khác (ví dụ: 型, ｸﾘｯﾌ)
- trong trường hợp mà có chữ 流止め thì product_type chính là 特AP còn product_size chính là chữ bên cạnh có dạng AXBXC (A, B, C là 1 số) 
- trong trường hợp mà có chữ ストレート 9X25 平 SN490B L thì product_type chính là FB 
- nếu gặp chữ RGクリップ thì chuyễn về RGｸﾘｯﾌﾟ
- Một số  product_type đặc biệt khác có thể gặp: B-120, B-180, VS, VM, VL, VB-55, VB-75, VB-110, VWS, VW, VWB, VM-30, VL-30, VB-5530, VS-4, VM-4, VL-4, VL-25, VB-25, FS, FM, FL, FB-55, FB-75, FB-110, FWS, FW, FWB, FWN-20, FWN-32, FM-30, FL-30, FB-5530, FS-4, FM-4, FL-4, FM-25, FL-25, FB-25, FB-7525, FM-328, FL-340, SC, SC-3T, SC-4T, SC-5, RT-25, A, AW, AW-2, A-50, A-80, A-110, DF-40, DF-55, DF-75, DF-120, CP-40, CP-50, CP-100, YV-25, FMG-28, FHT-30, YHR-25N, YHR-32N, YHR-50N, ND, TR-25, TR-40, VSHD, VLHD, JS, L-1, L-2, LB-12, LB-17, LCB-19, LCB-20, LB-23T, LCB-27T, LCB-29T, LB-46T, RV-3245, RV-3250, RV-3255, SRF-30, SRF-40, CAT-30, NST-1, VW-32R, VW-55R, CAT-16, BPX140-35, IT-50, PSK-50, PSK-503, SS, V-S, V-M, V-L, F-S, F-M, F-L, CBW-30NP, TGW-30L, CBW-G34NP, CBW-F40NP, CBW-271NP, CBW-276NP, CBW-TR90NP, CBW-07φNP, CBW-10φNP, CBW-12φNP, CBW-15φNP, CBW-S01NP, CBW-S02NP, CBW-S03NP, CBW-3C, CBW-36, CBW-J27, CBW-TR901, CBWR300TR, CBWR300G35, CBX-S02, CBX-F30P, CBX-30KG, CBM8067, CBX-WTD16, CBX-WTD41, CBX-WTD51, P-S, P-L, TC-25, TC-40
- Nếu gặp các chữ giống với một số product_type đặc biệt có thể gặp mà các chữ đấy không có dấu gạch ngang ở giữa thì bạn tự chủ động thêm dấu gạch ngang vào (ví dụ: CP40 -> CP-40 ) đây là quy tắc quan trọng không được bỏ qua hay quên.
■ product_size (Chuẩn hóa kích thước động): trường này trích xuất từ cột 品名・規格・サイズ
- Nếu product_type là AP thì product size sẽ có kết quả sẽ có dạng AXBXC (A, B, C là 1 số nguyên; A, B, C luôn có dạng tăng dần)
- Nếu product_type là EX, ST, STEX, STミニ, EXミニ, KEX, L型   thì product_size sẽ có dạng: 
	Mẫu: <số>MM và <số>°
	Chuẩn hóa: Định dạng thành <số>X<số>°.
	Ví dụ: 25MM 35° -> 25X35°.
- các cái trường trong product_size mà có dạng AXBXC thì phải chuẩn hóa lại cho các cái con số của nó tăng dần (VD: A>B>C thì phải đổi lại thành CXBXA)
- trong trường hợp mà product_type là RGｸﾘｯﾌﾟ thì product_size là 6 hoặc 7.
Quy tắc định dạng: Bắt buộc viết hoa chữ X, không có khoảng trắng, giữ nguyên ký hiệu độ ° nếu có.
- trong trường hợp product_type là K型 , 特K型thì product_size sẽ chỉ là 1 con số (ví dụ:  product_type là K型 product_size sẽ là 36 không phải 36MM)
- trong trường hợp product_type mà là ST, EX thì product_size sẽ là con số nằm đằng sau chứ t= X với số nằm đằng trước ký hiệu 度, số nằm đằng trước ký hiệu 度 phải cho thêm ký hiệu ° đằng sau 
(ví dụ: nếu data ở cột 品名・規格・サイズ là SUNOX スチールタップ EX 35度　t=16 thì product_type sẽ là EX và product_size là 16X35°)
- trong trường hợp product_type mà là AP, L型 thì product_size sẽ là con số nằm đằng sau chữ t=  
(ví dụ: nếu data ở cột 品名・規格・サイズ là SN490B Iブ ユウ AP型　T=28 × 38 × 80 thì product_type sẽ là AP và product_size là 28X38X80, SN490B スチールタップ L型　T=25 × 35° thì product_type sẽ là L型 và product_size là 25X35°)
- Nếu product_type mà là 1 trong các cái product_type đặc biệt có thể gặp thì product_size sẽ là null 

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
- nếu product_type mà là FB, CR-F thì is_processing phải là TRUE còn nếu như product_type mà không phải là FB thì bắt buộc is_processing phải là FALSE 
- trường hợp đặc biệt nếu product_type là FB và product_size là 12X32X thì is_processing là FALSE 

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
