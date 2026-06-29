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
					"supplier_tel": null,
					"supplier_address": null,
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
- Kết quả đầu ra phải khớp chính xác cấu trúc: {"header": {...}, "tables": {"items": [...]}}.
- Trang nào đã bị gạch bỏ thì ko cần đọc .

============================================================
KHÓA SCHEMA NGHIÊM NGẶT (STRICT SCHEMA LOCK)
============================================================
- Giữ nguyên các KEY chính xác như trong schema mẫu.
- KHÔNG thêm/xóa/đổi tên các key.
- Thông tin thiếu hoặc không rõ ràng => gán giá trị null.a
- KHÔNG tự ý suy luận giá trị trừ khi có hướng dẫn cụ thể.
- nếu gặp file pdf có nhiều trang thì header lấy data ở cái trang đầu tiên còn items thì phải lấy của tất cả các trang không được bỏ qua trang nào.

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
- Trích xuất từ mục "発注No" ở trang "部品・副資材等注文書".

■ comment 
- Trường này để chữ F. 

■ 工事名 — HEADER (Tên công trình hiển thị trên header hệ thống)

═══════════════════════════════════════════════
BƯỚC 1 — Xác định trang bắt đầu
═══════════════════════════════════════════════
Kiểm tra trang đầu tiên của PDF:

┌─────────────────────────────────────────────
│ TRƯỜNG HỢP A: Trang đầu là "部品・副資材等注文書"
└─────────────────────────────────────────────
  → Thực hiện tiếp BƯỚC 2, 3, 4, 5 bên dưới

┌─────────────────────────────────────────────
│ TRƯỜNG HỢP B: Trang đầu là "蝶番注文書"
└─────────────────────────────────────────────
  → Ghép nội dung theo công thức:

    [工事名] + " " + [工区／節] + " " + [工種]

    Quy tắc:
    - Lấy toàn bộ nội dung của từng mục
    - Thêm dấu cách giữa các mục
    - Nếu một mục bị trống thì bỏ qua,
      không thêm dấu cách thừa

    → Ví dụ:
      工事名  : 内幸町南街区
      工区／節: B工区L節（B2・B1FL）
      工種    : 大梁

      Kết quả = "内幸町南街区 B工区L節（B2・B1FL） 大梁"

  → Kết quả này chính là giá trị của ■ 工事名 — HEADER
    (không cần thực hiện BƯỚC 2, 3, 4, 5)

═══════════════════════════════════════════════
BƯỚC 2 — Trích xuất Mục 1: ※工事名
═══════════════════════════════════════════════
Lấy toàn bộ nội dung của ô "※工事名" trên trang
"部品・副資材等注文書".

Xử lý ngoặc tròn:
  - Chỉ xóa phần trong dấu ngoặc tròn （） khi nội dung
    bên trong là "仮称" hoặc các từ tương tự mang nghĩa
    "tạm gọi"
  - KHÔNG xóa ngoặc tròn chứa tên khu vực/phân loại
    như: （A工区）、（B工区）v.v...
  - KHÔNG xóa các dấu ngoặc khác như:
    「」、『』、【】、〈〉、<> v.v...

  → Ví dụ 1: "(仮称）内幸町一丁目街区南地区第一種市街地再開発事業新築工事"
             → "内幸町一丁目街区南地区第一種市街地再開発事業新築工事"
  → Ví dụ 2: "赤坂二・六丁目地区開発計画（A工区）"
             → Giữ nguyên "赤坂二・六丁目地区開発計画（A工区）"
               (vì （A工区） là tên khu vực)

Gọi kết quả này là [M1]

═══════════════════════════════════════════════
BƯỚC 3 — Trích xuất Mục 2: 備考
═══════════════════════════════════════════════
Cách nhận diện đúng ô 備考 cần lấy:
  - Trong trang "部品・副資材等注文書", có 2 ô mang tên 備考:
      + 備考 loại 1 (KHÔNG lấy): nằm trong bảng ※納入先,
        dạng hàng nằm ngang, chứa số điện thoại di động
        (ví dụ: "携帯：藤原 080-2009-2320")
      + 備考 loại 2 (CẦN LẤY): là tiêu đề cột nằm dọc
        ở phía bên phải trang, chứa các ghi chú về
        hạng mục vật tư

Quy tắc lấy giá trị từ 備考 loại 2:
  - Chỉ lấy các từ/cụm từ là tên hạng mục như:
    "13節"、"27階"、"2F"、"3F" v.v...
  - KHÔNG lấy "本体"
  - Tuyệt đối KHÔNG lấy các ký hiệu đặc biệt như:
    "＊"、"※"、"区分け有り" và các ghi chú khác
  - Nếu có nhiều ô, ghép theo thứ tự từ ô dưới lên trên,
    mỗi ô cách nhau bằng 1 dấu cách " "

Gọi kết quả này là [M2]

═══════════════════════════════════════════════
BƯỚC 4 — Trích xuất Mục 3
═══════════════════════════════════════════════
Xác định trang tiếp theo sau "部品・副資材等注文書":

┌─────────────────────────────────────────────
│ TRƯỜNG HỢP A: Trang tiếp theo là "溶接副資材発注書"
└─────────────────────────────────────────────
  → Lấy nội dung của ô "発注名" của trang đầu tiên
    trong số các trang "溶接副資材発注書"

  Loại bỏ trùng lặp:
    - So sánh với [M1] và [M2]
    - Xóa các cụm từ đã xuất hiện trong [M2] hoặc [M1]
    - Xóa các địa danh/tên viết tắt ở đầu chuỗi
      (ví dụ: "内幸町南"、"赤坂" v.v...)
    - Chỉ giữ lại phần KHÔNG trùng

  Gọi kết quả này là [M3]

┌─────────────────────────────────────────────
│ TRƯỜNG HỢP B: Trang tiếp theo là "現場材料発注連絡票"
└─────────────────────────────────────────────
  → Lấy nội dung của ô "発注理由"
  → Chỉ lấy phần nội dung tương ứng với "本体"
  → Loại bỏ các cụm từ đã xuất hiện trong [M1] hoặc [M2]

  Gọi kết quả này là [M3]
 
┌─────────────────────────────────────────────
│ TRƯỜNG HỢP C: Trang tiếp theo là "タブ・フラックス注文書"
└─────────────────────────────────────────────
  → Lấy toàn bộ nội dung của ô "物件名"
  → Loại bỏ các cụm từ đã xuất hiện trong [M1] hoặc [M2]

  Gọi kết quả này là [M3]

  Ví dụ:
    [M1] = 渋谷一丁目
    物件名 = 渋谷1丁目 A工区 7節 大梁（第4工場）
    [M3] = A工区 7節 大梁（第4工場）  (bỏ "渋谷1丁目" vì trùng M1)

  Kết quả = 渋谷一丁目 A工区 7節 大梁（第4工場）

═══════════════════════════════════════════════
BƯỚC 5 — GHÉP CHUỖI
═══════════════════════════════════════════════
Ghép theo thứ tự: [M1] + " " + [M2] + " " + [M3]
- Nếu một mục trống thì bỏ qua, không thêm dấu cách thừa.

Kết quả cuối cùng là giá trị của ■ 工事名 — HEADER

═══════════════════════════════════════════════
VÍ DỤ MINH HỌA 1
═══════════════════════════════════════════════
Input:
  ※工事名  : (仮称）内幸町一丁目街区南地区第一種市街地再開発事業新築工事
  備考(cột): 本体 / 13節 / ＊区分け有り
  発注名   : 内幸町南　13節地組梁

  [M1] = 内幸町一丁目街区南地区第一種市街地再開発事業新築工事
         (xóa "(仮称）")
  [M2] = 13節
         (chỉ lấy "13節", bỏ "本体" và "＊区分け有り")
  [M3] = 地組梁
         (xóa "内幸町南" vì là địa danh,
          xóa "13節" vì đã trùng với M2)

Kết quả = 内幸町一丁目街区南地区第一種市街地再開発事業新築工事 13節 地組梁

═══════════════════════════════════════════════
VÍ DỤ MINH HỌA 2
═══════════════════════════════════════════════
Input:
  ※工事名  : 赤坂二・六丁目地区開発計画（A工区）
  備考(cột): 本体 / 2・3F / ＊区分け有り
  発注名   : 3F (trang 溶接副資材発注書 đầu tiên)

  [M1] = 赤坂二・六丁目地区開発計画（A工区）
         (giữ nguyên （A工区）)
  [M2] = 2・3F
         (chỉ lấy "2・3F", bỏ "本体" và "＊区分け有り")
  [M3] = (trống, vì "3F" đã có trong M2)

Kết quả = 赤坂二・六丁目地区開発計画（A工区） 2・3F
		
■ 出荷日 (Ngày xuất hàng)
Đọc chữ viết tay màu đỏ, thường xuất hiện ở cuối trang đầu tiên.
- Chỉ ghi ngày/tháng, năm lấy theo năm hiện tại.
- Định dạng nghiêm ngặt: YYYY/MM/DD
- Ví dụ: đọc được 3/10 → kết quả là 2026/03/10
---
■ 納期 (Ngày giao hàng)
Đọc chữ viết tay màu đỏ, nằm ngay sau ký tự "土".
- "土" là ký tự phân cách giữa 出荷日 và 納期.
- Tháng lấy theo tháng của 出荷日, năm lấy theo năm hiện tại.
- Định dạng nghiêm ngặt: YYYY/MM/DD
- Ví dụ: 出荷日 đọc được 3/10, sau đó gặp 土 12 → 納期 là 2026/03/12

■ supplier_name (Địa điểm giao hàng)
Xem nội dung ở mục "※納入先" và áp dụng logic sau:
Trường hợp 1 — Nếu ô "工事現場" được tích chọn:
Trích xuất nội dung từ mục "納入先住所", chỉ lấy đến cấp 丁目.
Quy tắc:
- Địa chỉ Nhật Bản có cấu trúc: 都/道/府/県 → 市/区/町/村 → 町丁目 → 番地
- Chỉ lấy đến hết phần 丁目 (ví dụ: 一丁目, 二丁目, ...)
- KHÔNG lấy phần 番, 番地, 号 trở đi
Ví dụ:
- Input:  東京都渋谷区渋谷一丁目 18 番 2、3、28 番 5
- Output: 渋谷一丁目
---
Trường hợp 2 — Nếu cả hai ô "工事現場" và "下請負先" đều KHÔNG được tích chọn:
→ Để giá trị là null.

■ supplier_tel
- Kiểm tra mục "※納入先":
	Nếu ô "工事現場" không được tích chọn → để giá trị là null, dừng lại.
	Nếu ô "工事現場" được tích chọn → thực hiện các bước dưới đây.
		Bước 1 — Xác định tên cần đối chiếu
			Đọc nội dung mục "受入担当者" và lấy 2 chữ cuối làm từ khóa đối chiếu.
			Ví dụ: (株)角藤 三井 → từ khóa là 三井
		Bước 2 — Tìm số điện thoại khớp trong "備考"
			Đọc nội dung mục "備考". Tìm số điện thoại mà ngay trước nó có xuất hiện từ khóa trùng với 2 chữ ở Bước 1.
			Ví dụ: 備考 có nội dung 藤原 080-2009-2320　三井 070-4176-3829
			藤原 ≠ 三井 → bỏ qua 080-2009-2320
			三井 = 三井 → chọn 070-4176-3829
		Bước 3 — Trích xuất 5 ký tự cuối
			Lấy 5 ký tự cuối của số điện thoại đã chọn ở Bước 2 (dấu - được tính là 1 ký tự).
			Ví dụ: 070-4176-3829 → 6-3829

■ supplier_code 
- Kiểm tra mục "※納入先":
	Kiểm tra trong form, nếu ô "(株)角藤 鉄構事業部" được tích chọn
	→ Đọc nội dung trên cùng hàng với ô đó và áp dụng logic sau:
	- Nếu cùng hàng có xuất hiện "第1工場" hoặc "第一工場" → supplier_code = 361113
	- Nếu cùng hàng có xuất hiện "高山"                   → supplier_code = 361116
	Nếu ô "(株)角藤 鉄構事業部" KHÔNG được tích chọn → để null.

■ customer_code
- Trường này thì để null.

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

■ product_type (Quy tắc trích xuất & Chuẩn hóa)
Chỉ xem và tham khảo tại các cột sau: 裏板サイズ, 流れ止めサイズ, タブ厚, AP厚, 発注数量. Những cột nào có dấu gạch X đỏ thì bỏ không cần đọc, và toàn bộ hàng tương ứng với cột bị X đỏ đó cũng bị bỏ qua hoàn toàn, không đọc bất kỳ thông tin nào trong hàng đó kể cả ở các cột khác.
Quy tắc đọc bảng タブ厚 / AP厚 / 流止め / 裏板長さ:

Quy tắc ưu tiên: Dù cột 合計/合計1 (hoặc 合計/合計2, 合計/合計3, 合計/合計4) bị đánh dấu X đỏ, nếu cột 発注数量 vẫn có giá trị > 0 thì vẫn đọc hàng đó bình thường.
Chỉ bỏ qua hoàn toàn hàng nào mà cột 発注数量 không có giá trị hoặc = 0.
Nếu cột 合計 bị X đỏ VÀ cột 発注数量 cũng không có giá trị → bỏ qua toàn bộ bảng đó.
TUYỆT ĐỐI KHÔNG được trích xuất các product_type sau dù tìm thấy ở bất kỳ đâu:

Dòng V: VL, VM, VS, VB-55, VB-75, VB-110, VWS, VW, VWB, VB-5530, VS-4, VB-25, VM-30, VL-30, VL-4, VM-4, VL-25, V-M, V-L, V-S, VSHD, VLHD, VW-32R, VW-55R
Dòng F (ngoại trừ FB): FL, FM, FS, FB-55, FB-75, FB-110, FWS, FW, FWB, FWN-20, FWN-32, FM-30, FL-30, FB-5530, FS-4, FM-4, FL-4, FM-25, FL-25, FB-25, FB-7525, FM-328, FL-340, F-S, F-M, F-L



Quy tắc đọc bảng dạng 添付明細書 (có cột 種類/サイズ/注文数):
- product_type và product_size lấy từ hàng 裏板 (ví dụ: 裏板 9x25 → product_type = FB, product_size = 9X25).
- Chỉ đọc các cột 注文数 có tiêu đề phụ hợp lệ nằm phía trên hoặc phía dưới chữ "注文数"
  (ví dụ: 5節8階, 地組梁, 5節9階, 5節...).
- Nếu ô tiêu đề chỉ ghi "注文数" mà KHÔNG có tên phân loại kèm theo → không đọc cột đó.
- Nếu ô tiêu đề hoàn toàn trống → không đọc cột đó.
- Mỗi ô có giá trị trong cột 注文数 hợp lệ → tạo 1 record riêng với 長さ và 員数 tương ứng.
- Nếu cùng 1 hàng (同じ長さ) có nhiều cột 注文数 có giá trị → tạo nhiều record riêng biệt.
- Không đọc cột tổng (tiêu đề chỉ là 合計 hoặc tên節 đứng một mình không kèm 階/分類,
  ví dụ: "5節" đứng một mình → bỏ qua).
- Với bảng chỉ có cột 積別(規格・等級等) / 数量等 / 備考...

Định nghĩa: Ký hiệu phân loại ngắn trong mô tả sản phẩm.
Ràng buộc: Độ dài 1–12 ký tự. Không có khoảng trắng.

KHÔNG ĐƯỢC chứa "MM", "mm", hoặc dấu độ "°".
KHÔNG ĐƯỢC cắt bỏ các hậu tố tiếng Nhật dính liền (ví dụ: 型, ミニ, 枠) trừ trường hợp B-120型 và B-180型 thì chỉ lấy B-120 và B-180.

Chuẩn hóa ưu tiên cao:

Dòng CR-F: Nếu mô tả chứa cả "CR" và "F", nếu gặp CRF thì product_type là CR-F
- Khi gặp ký hiệu dạng CR + ký tự phía sau (dù in hay viết tay), phải đọc toàn bộ
  cụm ký tự liền kề trước khi xác định product_type.
  Ví dụ: CR-F (dù phần "-F" là viết tay) → product_type = CR-F, KHÔNG được đọc là CR.
- Nếu thấy CR có thêm bất kỳ ký tự nào phía sau → đọc toàn bộ cụm đó,
  không được cắt bỏ phần viết tay.

Nếu gặp chữ CR đứng một mình (không kèm -F hoặc F) thì product_type là FB
và product_size sẽ có 2 trường hợp xảy ra:
- Nếu ký tự đằng sau chữ L mà nhỏ hơn 80 thì product_size sẽ là 9X25X hoặc 9X32X
  tùy thuộc vào hàng sản phẩm đấy hiển thị 9X25 hay 9X32
  (Lưu ý: product_size lúc này sẽ chỉ là 9X25X hoặc 9X32X không X thêm số gì vào sau)
- Nếu ký tự đằng sau chữ L mà lớn hơn 80 thì product_size là 9X25X số đằng sau chữ L
  hoặc 9X32X số đằng sau chữ L tùy thuộc vào hàng sản phẩm đấy hiển thị 9X25 hay 9X32

Dòng AP: Nếu mã là "AP" + số (ví dụ: AP36, AP48) -> CHỈ lấy "AP" làm product_type.
- Nếu gặp bảng ②エプロン (38X25) hoặc ②エプロン (38X50) trong trang タブ・フラックス注文書:
  → product_type = AP
  → 員数 lấy từ cột 個数.
Dòng CP: Nếu mã là "CP" + số nhưng thiếu dấu gạch ngang (ví dụ: CP40) -> Phải chuyển thành "CP-40".

Dòng 割矢:
- Nếu gặp ※割矢 trong cột 種別(規格・等級等):
  → Đọc dòng tiếp theo để lấy product_type
  → product_type = phần trước chữ シングル hoặc ダブル
    (ví dụ: Aタイプ シングル → product_type = Aタイプ)
  → 員数 lấy từ cột 数量等
  → product_size = null

Quy tắc từ cột 裏板サイズ:
Nếu cột 裏板サイズ có giá trị dạng 9X25X hoặc 12X32X thì mặc định:
product_type = FB
product_size = giá trị tương ứng (9X25X hoặc 12X32X)



Quy tắc từ cột 流れ止めサイズ:

Nếu cột 流れ止めサイズ có giá trị dạng A = BxBxC (ví dụ: 38 = 38x38x4.5) thì:

product_type = 特AP
product_size = chuẩn hóa tăng dần các số (ví dụ: 38x38x4.5 → 4.5X38X38)



Các mẫu phổ biến: EX, SC, B-120, L型, CP-40, AP, RGｸﾘｯﾌﾟ, VB-55, VWS, CBW-S02NP, TGW-30, F-S, LB-12, A-80, STミニ, EXミニ ...

Lưu ý không được nhầm product_type từ STミニ chứ không STﾐﾆ
Bạn không được nhầm chữ L型 với chữ レ型, trường hợp mà bạn đọc ra được chữ レ型 thì phải chuẩn hóa về L型 ngay
product_type sẽ có dạng là chữ cái viết hoa (A-Z), số (0-9) và dấu gạch ngang (-) và 1 số ký tự tiếng nhật khác (ví dụ: 型, ｸﾘｯﾌ)
Trong trường hợp mà có chữ 流止め thì product_type chính là 特AP còn product_size chính là chữ bên cạnh có dạng AXBXC (A, B, C là 1 số)
Trong trường hợp mà có chữ ストレート 9X25 平 SN490B L thì product_type chính là FB
Nếu gặp chữ RGクリップ thì chuyển về RGｸﾘｯﾌﾟ
Nếu gặp DC丸AXB (A, B là số) thì product_type là DC và product_size là AXB (Ví dụ: ボンDC丸6.5X355 thì product_type là DC và product_size là 6.5X355)
Nếu gặp các chữ giống với một số product_type có thể gặp mà các chữ đấy không có dấu gạch ngang ở giữa thì bạn tự chủ động thêm dấu gạch ngang vào (ví dụ: CP40 -> CP-40)


■ product_size (Chuẩn hóa kích thước động)
Chỉ xem và tham khảo tại các cột sau: 裏板サイズ, 流れ止めサイズ, タブ厚, AP厚. Những cột nào có dấu gạch X đỏ thì bỏ không cần đọc, và toàn bộ hàng tương ứng với cột bị X đỏ đó cũng bị bỏ qua hoàn toàn, không đọc bất kỳ thông tin nào trong hàng đó kể cả ở các cột khác.
Quy tắc đọc bảng タブ厚 / AP厚 / 流止め / 裏板長さ:

Quy tắc ưu tiên: Dù cột 合計/合計1 (hoặc 合計/合計2, 合計/合計3, 合計/合計4) bị đánh dấu X đỏ, nếu cột 発注数量 vẫn có giá trị > 0 thì vẫn đọc hàng đó bình thường.
Chỉ bỏ qua hoàn toàn hàng nào mà cột 発注数量 không có giá trị hoặc = 0.
Nếu cột 合計 bị X đỏ VÀ cột 発注数量 cũng không có giá trị → bỏ qua toàn bộ bảng đó.

Trường hợp đặc biệt:

Dòng AP:
Mẫu: "AP" + <số> + "MM"
Trích xuất: Lấy <số> và thêm số 38 và 50 vào kết quả, kết quả sẽ có dạng AXBXC (A, B, C là 1 số nguyên; A, B, C luôn có dạng tăng dần)
Ví dụ: AP36MM -> 38X36X50 -> 36X38X50 ; AP48MM -> 38X48X50 -> 38X48X50; AP60MM -> 38X50X60
- Nếu gặp bảng ②エプロン (38X25) hoặc ②エプロン (38X50):
  → Lấy 板厚 + 2 số trong ngoặc của エプロン, gộp 3 số lại
    và chuẩn hóa tăng dần.
  Ví dụ: ②エプロン (38X25), 板厚=19 → 19, 25, 38 → product_size = 19X25X38
Trong trường hợp mà product_type là CR-F thì product_size sẽ là AXBX với cái số đằng sau chữ L (ví dụ: スノウチノンスカCRF 9X25 SN490B L60 thì product_size là 9X25X60)

Trường hợp đặc biệt dòng AP: nếu gặp エンドタブ AXB SN490B CMM AP (A, B, C là số) thì product_size sẽ là AXBXC (Nếu A, B, C chưa phải dạng tăng dần thì bạn phải chuẩn hóa về dạng tăng dần) (Ví dụ: エンドタブ 38X12 SN490B 28MM thì product_size sẽ là 38X12X28 -> 12X28X38)



Trường hợp tiêu chuẩn:
Mẫu: <số>MM và <số>°
Chuẩn hóa: Định dạng thành <số>X<số>°.
Ví dụ: 25MM 35° -> 25X35°.
Trường hợp có chiều dài (Mẫu chữ L):
Mẫu: Nếu kích thước (ví dụ: 9X25) có kèm theo chữ "L" + <số> (ví dụ: L260).
Chuẩn hóa: Nối chiều dài bằng dấu "X".
Ví dụ: "9X25 ... L260" -> 9X25X260.
Nếu kích thước 12X32 (ví dụ: 12X32 ... L260) thì là 1 trường hợp đặc biệt khác lúc đấy product_size sẽ là 12X32X
Quy tắc từ cột 流れ止めサイズ:

Nếu đọc được dạng A = BxBxC (ví dụ: 38 = 38x38x4.5) thì product_size = chuẩn hóa tăng dần (ví dụ: 4.5X38X38)
Trong trường hợp product_type là FB thì product_size chính là AXBXC thì phải chuẩn hóa lại cho các cái con số của nó tăng dần (A, B, C là 1 số, C thường nằm sau chữ L) (VD: nếu thấy chữ ストレート 9X25 平 SN490B L680 thì product_size chính là 9X25X680)
Trong trường hợp nếu thấy chữ ストレート 12X32 平 SN490B L680 thì product_type là FB và product_size chính là 12X32X
Các cái trường trong product_size mà có dạng AXBXC thì phải chuẩn hóa lại cho các cái con số của nó tăng dần (VD: A>B>C thì phải đổi lại thành CXBXA)
Trong trường hợp mà product_type là RGｸﾘｯﾌﾟ thì product_size là 6 hoặc 7.

Quy tắc chuẩn hóa đặc biệt cho FB từ cột 裏板サイズ:

Nếu product_type là FB và cột 裏板サイズ là 9X25X → product_size luôn luôn là 9X25, KHÔNG được nối thêm bất kỳ số nào vào sau (kể cả 裏板長さ hay bất kỳ số nào khác trong bảng).

Quy tắc định dạng: Bắt buộc viết hoa chữ X, không có khoảng trắng, giữ nguyên ký hiệu độ ° nếu có.

Trong trường hợp product_type là K型 thì product_size sẽ chỉ là 1 con số (ví dụ: product_type là K型 product_size sẽ là 36 không phải 36MM)
Nếu product_type mà là CR thì product_size là 9X25X (Lưu ý: product_size lúc này sẽ chỉ là 9X25X không X thêm số gì vào sau)

■ オーダーNo (Mã đơn hàng)
- Trích xuất từ mục "注文No.".
- Trường này thì bắt buộc phải lấy của trang tương ứng với cái bản ghi đấy chứ không được lấy của trang đầu tiên.

■ 工事名 — BODY (Tên công trình hiển thị trong từng dòng bản ghi)

LƯU Ý QUAN TRỌNG:
  - Mỗi bản ghi lấy 工事名 từ trang tương ứng với chính nó
  - KHÔNG lấy từ trang đầu tiên của tài liệu
  - 工事名 trên trang 溶接副資材発注書 có thể ở dạng viết tắt
    (ví dụ: "赤坂2・6") → KHÔNG dùng trực tiếp,
    thay bằng ※工事名 từ trang 部品・副資材等注文書

═══════════════════════════════════════════════
BƯỚC 1 — Xác định trang tương ứng với bản ghi
═══════════════════════════════════════════════
Xác định bản ghi hiện tại thuộc trang nào, sau đó
áp dụng logic tương ứng bên dưới.

═══════════════════════════════════════════════
BƯỚC 2 — Áp dụng logic theo loại trang
═══════════════════════════════════════════════

┌─────────────────────────────────────────────
│ TRƯỜNG HỢP 1: Trang là "溶接副資材発注書"
└─────────────────────────────────────────────
  [M1] = ※工事名 từ trang "部品・副資材等注文書"
         Xử lý ngoặc tròn:
         - Chỉ xóa （） khi nội dung bên trong là "仮称"
         - KHÔNG xóa ngoặc chứa tên khu vực như （A工区）

  [M2] = Nội dung ô "発注名" trên trang 溶接副資材発注書
         đang xử lý
         - Loại bỏ địa danh/tên viết tắt ở đầu chuỗi
           (ví dụ: "内幸町南"、"赤坂" v.v...)
         - Chỉ giữ lại phần phân loại như:
           "3F"、"2F"、"13節地組梁" v.v...
         - Loại bỏ các cụm đã có trong [M1]

  Ghép: [M1] + " " + [M2]

  → Ví dụ 1:
    ※工事名 (trang 1): (仮称）内幸町一丁目街区南地区第一種市街地再開発事業新築工事
    発注名  (trang này): 内幸町南 13節地組梁

    [M1] = 内幸町一丁目街区南地区第一種市街地再開発事業新築工事
    [M2] = 13節地組梁  (bỏ "内幸町南")

    Kết quả = 内幸町一丁目街区南地区第一種市街地再開発事業新築工事 13節地組梁

  → Ví dụ 2:
    ※工事名 (trang 1): 赤坂二・六丁目地区開発計画（A工区）
    発注名  (trang này): 3F

    [M1] = 赤坂二・六丁目地区開発計画（A工区）  (giữ nguyên （A工区）)
    [M2] = 3F

    Kết quả = 赤坂二・六丁目地区開発計画（A工区） 3F

┌─────────────────────────────────────────────
│ TRƯỜNG HỢP 2: Trang là "現場材料発注連絡書"
└─────────────────────────────────────────────
  [M1] = 現場名 trên trang này

  [M2] = Nội dung "発注理由" mục con "1:本体"
         - Tách thành: 節番号 + 内容 (KHÔNG lấy "本体")
         - Loại bỏ các cụm đã có trong [M1]

  Ghép: [M1] + " " + [M2]

  → Ví dụ:
    現場名   : 渋谷一丁目再開発事業
    発注理由 : 1:本体 → 2節溶接材料

    [M1] = 渋谷一丁目再開発事業
    [M2] = 2節 溶接材料  (bỏ "本体")

    Kết quả = 渋谷一丁目再開発事業 2節 溶接材料

┌─────────────────────────────────────────────
│ TRƯỜNG HỢP 3: Trang là "蝶番注文書"
└─────────────────────────────────────────────
  Ghép theo công thức:

    [工事名] + " " + [工区／節] + " " + [工種]

  - Nếu một mục trống thì bỏ qua,
    không thêm dấu cách thừa

  → Ví dụ:
    工事名  : 内幸町南街区
    工区／節: B工区L節（B2・B1FL）
    工種    : 大梁

    Kết quả = 内幸町南街区 B工区L節（B2・B1FL） 大梁

┌─────────────────────────────────────────────
│ TRƯỜNG HỢP 4: Trang là "タブ・フラックス注文書"
└─────────────────────────────────────────────
  → Lấy toàn bộ nội dung từ mục "物件名"

  → Ví dụ:
    物件名 : SUBARU大泉ボディ・トリム棟 C工区2節柱 ラチス用

    Kết quả = SUBARU大泉ボディ・トリム棟 C工区2節柱 ラチス用

┌─────────────────────────────────────────────
│ TRƯỜNG HỢP 5: Trang là "部品・副資材等注文書"
│ (không có trang phụ đi kèm)
└─────────────────────────────────────────────
  [M1] = ※工事名 trên trang này
         - Chỉ xóa （） khi nội dung bên trong là "仮称"
         - KHÔNG xóa ngoặc chứa tên khu vực như （A工区）

  [M2] = Xác định loại bảng:
		Nếu bảng dạng thông thường (có cột 備考):
			- Lấy từ cột "備考" thuộc bảng "※注文明細"
			- KHÔNG lấy ô "備考" trong mục "※納入先"
			- Chỉ lấy các từ là tên hạng mục: "13節"、"27階"、"2F" v.v...
			- KHÔNG lấy "本体"
			- KHÔNG lấy: "＊"、"※"、"区分け有り" v.v...
			- Nếu nhiều ô: ghép từ ô dưới lên trên, cách nhau 1 dấu cách " "
		Nếu bảng dạng 添付明細書 (có cột 種類/サイズ/注文数):
			- [M2] = tiêu đề cột 注文数 tương ứng với record đang xử lý
			(ví dụ: 5節8階, 地組梁, 5節9階...)
			- Mỗi nhóm record thuộc cùng 1 cột sẽ có cùng 工事名
			
  Ghép: [M1] + " " + [M2]
  
    → Ví dụ (bảng 添付明細書):
    ※工事名 : 渋谷一丁目地区共同開発事業
    Cột đang đọc: 5節8階

    Kết quả = 渋谷一丁目地区共同開発事業 5節8階

■ is_processing
- nếu product_type mà là FB, CR-F thì is_processing phải là TRUE còn nếu như product_type mà không phải là FB thì bắt buộc is_processing phải là FALSE 
- trường hợp đặc biệt nếu product_type là FB và product_size là 12X32X thoặc 9X25X thì is_processing là FALSE 
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

■ 長さ
- Trường 長さ sẽ trích xuất giá trị tương ứng từ cột 裏板長さ hoặc cột サイズ.
- Nếu cả 2 cột đều không có giá trị → để null, KHÔNG tự ý suy đoán từ bất kỳ nguồn nào khác.
- Nếu file không xuất hiện cả 2 cột 裏板長さ và サイズ → để null, KHÔNG đọc từ bất kỳ cột nào khác.
- TUYỆT ĐỐI KHÔNG trích xuất 長さ từ cột 積別(規格・等級等) hoặc bất kỳ cột mô tả
  sản phẩm nào khác, dù trong đó có chứa "L=" hay số đo chiều dài.
  
■ 員数
- Trường 員数 sẽ trích xuất giá trị tương ứng từ cột 発注数量 hoặc cột 注文数.
- Chỉ đọc các cột 注文数 có tiêu đề phụ hợp lệ nằm phía trên hoặc phía dưới chữ "注文数"
  (ví dụ: 5節8階, 地組梁, 5節9階...).
- Nếu ô tiêu đề chỉ ghi "注文数" mà KHÔNG có tên phân loại kèm theo → không đọc cột đó.
- Nếu ô tiêu đề hoàn toàn trống → không đọc cột đó.
- Không đọc cột tổng (tiêu đề chỉ là 合計 hoặc tên節 đứng một mình không kèm 階/分類,
  ví dụ: "5節" đứng một mình → bỏ qua).
- Mỗi ô có giá trị trong cột 注文数 hợp lệ → tạo 1 record riêng với 長さ và 員数 tương ứng.
- Nếu cùng 1 hàng (同じ長さ) có nhiều cột 注文数 có giá trị → tạo nhiều record riêng biệt.
- Thứ tự tạo record phải theo từng cột 注文数 từ trái sang phải.
  Trong mỗi cột, đọc các hàng từ trên xuống dưới.
  Phải đọc hết toàn bộ hàng của cột hiện tại trước khi chuyển sang cột tiếp theo bên phải.
  KHÔNG đọc theo hàng ngang.

■ BẢO TỒN VĂN BẢN:		
- Giữ nguyên văn bản tiếng Nhật (Kanji/Kana) chính xác như trên file.
- Chỉ chuẩn hóa các khoảng trắng thừa.
- KHÔNG diễn giải lại, không dịch, không rút ngắn văn bản.
