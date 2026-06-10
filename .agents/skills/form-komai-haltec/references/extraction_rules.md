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
- Return ONLY valid JSON. No markdown. No comments.
- Output must match exactly: {"header": {...}, "tables": {"items": [...]}}

[STRICT SCHEMA LOCK]
- Keep keys EXACTLY as schema. Do NOT add/remove/rename keys.
- Missing/unknown => null.

[HEADER EXTRACTION - DYNAMIC KEYWORDS]
- supplier_code: trường nãy sẽ trích xuất ở 納入場所 (có thể nằm ở trong ô hoặc bên ngoài ngay sát ô) (trường này cũng có thể sẽ được viết tay nên bạn phải để ý)
	+ nếu gặp chữ 特殊加工棟 thì supplier_code sẽ là 253145 
	+ nếu gặp chữ 橋梁倉庫 thì supplier_code sẽ là 253144 
	+ nếu gặp chữ 8A thì supplier_code sẽ là 253148
	+ nếu gặp chữ 鉄B東 thì supplier_code sẽ là 253147 
	+ nếu gặp chữ 鉄A東 thì supplier_code sẽ là 253146 
	+ nếu gặp chữ 8B thì supplier_code sẽ là 258124 
	+ nếu gặp chữ 鉄構守衛前 thì supplier_code sẽ là 258120 
	+ nếu gặp chữ 8c thì supplier_code sẽ là 253149  
	+ nếu gặp chữ SN1  thì supplier_code sẽ là 255560   
	
- customer_name1 và customer_name2 thì để là null 
- オーダーNo: Extract the specific identifier found on Page 1 (typically a decimal format like "1.6566").
- 工事名:
                1. CÔNG THỨC GHÉP CHUỖI TỔNG QUÁT:
                    [工事名]　[節]　[名称]　[Mã gạch đỏ (nếu có)]　[工事番号]
                2. QUY TẮC CHI TIẾT CHO TỪNG TRƯỜNG:
                    - [工事名]: Lấy sau "工事名:". Chuyển sang Full-width.
                    - [節]: Lấy toàn bộ nội dung trong ngoặc. Thêm hậu tố "節" (nếu chưa có). Định dạng: Full-width (VD: 16 -> １６節).
                    - [名称]:
                        + GIỮ KHOẢNG TRẮNG GỐC: Nếu văn bản gốc có khoảng trắng giữa các từ (VD: 十字柱 内ダイヤフラム), BẮT BUỘC phải giữ lại và chuyển thành dấu cách Full-width (　).
                        + QUY TẮC TỰ ĐỘNG THÊM KHOẢNG CÁCH: 
                            * Sau từ "小梁", BẮT BUỘC thêm một dấu cách Full-width (Ví dụ: "小梁変更" -> "小梁　変更",...).
                            * Sau từ "主材", BẮT BUỘC thêm một dấu cách Full-width (Ví dụ: "主材現場用" -> "主材　現場用",...).
                            * Sau từ "階", BẮT BUỘC thêm một dấu cách Full-width (Ví dụ: "１８階小梁" -> "１８階　小梁",...).
                            * Sau từ "十字柱", BẮT BUỘC thêm một dấu cách Full-width (Ví dụ: "十字柱 内ダイヤフラム" -> "十字柱　内ダイヤフラム",...).
                        + QUY TẮC LƯỢC BỎ & THAY THẾ:
                            * Nếu có "ウラ当て(現場)": Xóa toàn bộ cả cụm.
                            * Nếu cụm từ có chứa "ウラ板" ở cuối: Thay bằng "　工場用", còn trường hợp khác thì thôi không thay thế gì cả.
                            * Danh sách chứa các từ xóa nếu từ đó có chứa các từ sau: (裏当て金, 裏当て, 裏板, ワラ当て, ウラ当て, ウラ当, タブウラ板, エプロン, タブ, ウラ板AP流れ止め).
                            * Quy tắc: Chỉ xóa đúng từ khóa trong danh sách, GIỮ LẠI các nội dung khác đi kèm (Ví dụ: "23階エプロン" -> "23階", "現場裏板" -> "現場").
                        + ĐỊNH DẠNG: Chuyển toàn bộ nội dung trường này sang Full-width.	
                    - [Mã gạch đỏ]: Tại mục (SCAW), kiểm tra các dãy số (9110, 9120...). CHỈ lấy nếu có GẠCH CHÂN ĐỎ hoặc KHOANH TRÒN ĐỎ. Giữ nguyên Half-width.	
                    - [工事番号]: Lấy dãy số trong khung "工事番号". Giữ nguyên Half-width.
                3. VÍ DỤ MINH HỌA:
                    - Ví dụ thay thế: 
                    + Gốc: 名称: 十字柱ウラ板
                    + Kết quả: 十字柱　工場用
                    - Ví dụ giữ khoảng trắng & xóa bỏ:
                    + Gốc: 名称: 十字柱 内ダイヤフラム 現場裏板
                    + Kết quả: 十字柱　内ダイヤフラム　現場

- 出荷日: trường này thông thường sẽ được viết tay bằng chữ màu đỏ ở ngay dưới ô 入材要望日 và nó chỉ ghi tháng và ngày năm sẽ là năm hiện tại (VD: 9/25 -> năm hiện tại/9/25) (năm nay là năm 2026) trong trường hợp không có chữ viết tay sẽ lùi vào 1 ngày so với trường 納期 (VD: 納期 là 2025/9/25 thì 出荷日 là 2025/9/24) nếu vướng thứ 7 chủ nhật thì lùi 3 ngày 
- 納期: trường này sẽ nằm ở ô 入材要望日 và nó chỉ ghi tháng và ngày năm sẽ là năm hiện tại (VD: 9/25 -> năm hiện tại/9/25) (năm nay là năm 2026) 

[ITEM ROW DETECTION]
- Each data page (excluding the Table of Contents "目次") is treated as a single item row.
- An item is valid if it contains a page-specific identifier (e.g., 1.6566) and technical specifications.

[FIELD RULES - ITEMS]
- 商品コード: trường này luôn luôn để null 
- オーダーNo: Extract the specific identifier for each page (e.g., 1.6566, 1.6567, 1.6568).
- product_title: trường này thì để null lúc nào cũng là null 
- product_type: trường này thì lấy data ở cái cột 断面 hoặc cột 部材マーク
      + trong trường hợp cột 部材マーク có 1 trong các cái chữ ST, STEX, 特ST, 特STEX, STミニ, EXミニ, 特STミニ, 特EXミニ, EX, 特EX, 特AP, AP thì data của product_type lấy ở cột 部材マーク nhưng chỉ lấy chữ không lấy số (vd: K36 thì lấy K, AP36 thì lấy AP, EX26 thì lấy EX) nếu không phải là 1 trong các cái từ trên thì lấy ở cột 断面
      + trong trường hợp cột 部材マーク không có các giá trị ST, STEX, 特ST, 特STEX, STミニ, EXミニ, 特STミニ, 特EXミニ, EX, 特EX, 特AP, AP thì lấy ở cột 断面 data ở cột 断面 thường là (FB, NS45°, CR-F)
      + trong trường hợp cột 断面 không có gì thì lấy ở cột 部材マーク data ở cột này sẽ có cả chữ và số nhưng mà mình sẽ loại bỏ số đi chỉ giữ lại chữ thôi (VD: EX25 -> EX)
      + trong trường hợp cột 部材マーク là ND hoặc ở cột 材質 là SS400 thì product_type sẽ là 特AP 
		- nếu 
      + trong trường hợp cột 部材マーク là K cộng với 1 con số thì product_type sẽ bắt buộc là K型 và product_size chính là con số đấy (vd: cột 部材マーク là K28 thì product_type là K型 và product_size là 28)
      + trong trường hợp product_type là AP, EX, 特AP, K型 thì 長さ sẽ là rỗng 
      + trong trường hợp product_size mà đọc ra có chữ số thập phân thì product_type sẽ là 特AP chứ không phải AP, bạn cần phải chú ý nếu product_type là AP hoặc 特AP product_size sẽ có dạng AXBXC tức là lúc nào cũng có 3 số hoặc chữ cái chứ ko phải 2 [Quy tắc quan trọng]
      + Nếu ở bản vẽ kĩ thuật có chữ NS45°  thì  product_type chính là NS45° và product_size data ở cột 寸法 X với 長さ sau đó chuẩn hóa về dạng tăng dần (Ví dụ: 寸法 là 9X25 và 長さ là 32 thì product_size là 9X25X32)  và is_processing là TRUE 
				
- product_size: trường này thì lấy data ở cột 部材マーク hoặc cột 寸法
       + trong trường hợp product_type là 1 trong các cái ST, STEX, 特ST, 特STEX, STミニ, EXミニ, 特STミニ, 特EXミニ, EX, 特EX và data ở cột 寸法 là độ góc vd: X35° thì product_size sẽ là data ở cột 部材マーク (nhưng chỉ lấy số ko lấy chữ) X với data ở cột 寸法 (vd: data ở cột 部材マーク là EX25 data ở cột 寸法 là 35° thì product_size sẽ là 25X35°)
       + trong trường hợp ở cột 寸法 mà có chữ 度 thì phải chuẩn hóa về ° (ví dụ: 35度 -> 35°)
       + trong trường hợp data ở cột product_type là AP thì product_size sẽ là data ở cột 長さ X với data ở cột 寸法 vd:data ở cột 長さ là A data ở cột 寸法 là BXC thì product_size là AXBXC, nhưng phải chuẩn hóa lại thành tăng dần từ nhỏ đến lớn 
       + trong trường hợp product_type là 1 trong các cái FB, NS45°, CR-F thì product_size lấy ở cột 寸法
       + thông thường các cái số ở cột 寸法 luôn là từ nhỏ đến lớn vd: 3X1 thì phải đổi thành 1X3 
       + trong trường hợp product_type là 特AP và data ở cột 寸法 là 4.5X38 và data ở cột 長さ là 38 thì product_size sẽ là 4.5X38X38
       + trong trường hợp product_type là 特AP và data ở cột 寸法 là 4.5X50 và data ở cột 長さ là 50 thì product_size sẽ là 4.5X50X50  
       + trong trường hợp product_type là 特AP và data ở cột 寸法 là 4.5X38 và data ở cột 長さ là 1 số bất kỳ ngoại trừ 38 thì product_size sẽ là 4.5X38XL1 
       + trong trường hợp product_type là 特AP và data ở cột 寸法 là 4.5X50 và data ở cột 長さ là 1 số bất kỳ ngoại trừ 50 thì product_size sẽ là 4.5X50XL1
       + trong trường hợp product_type là 特AP và data ở cột 寸法 là 4.5XA  (A là 1 số bất kỳ ngoại 38 và 50) thì product_size sẽ là 4.5XW1XL1
       + trong trường hợp product_type là EX thì product_size giữ nguyên như trong file pdf không cần phải chuẩn hóa lại cho nó tăng dần từ nhỏ đến lớn (vd: 32G-EX55-35 thì product_size sẽ là 55X35°) chỉ có cái EX này mới giũ nguyên như vậy thôi còn những cái trường hợp khác vd: của product_type là FB mà product_size là 25X9 thì vấn phải chuẩn hóa về 9X25  
       + bạn phải thật để ý vì trong đơn có thể sẽ có chữ viết tay ví dụ 25X36X38 thì dấu nhân có thể viết tay bằng chữ đỏ 
       + trong trường hợp product_type là K型 thì product_size sẽ ở cột 部材マーク nhưng chỉ lấy số ko lấy chữ, các sản phẩm product_type là K型 thì product_size sẽ chỉ là 1 con số (vd: cột 部材マーク là K28 thì product_size là 28 ) (đây sẽ là 1 quy tắc quan trọng bạn không được quên)
- dấu nhân là chữ X chữ ko phải là x, lúc nào cũng phải dùng X không được x VD: AxBxC phải đổi thành AXBXC 
- cái product_type với product_size nó thẳng hàng nên bạn phải thật là để ý không được nhầm 
- Cái dấu 〃 tức là giá trị giống hệt với cái hàng bên trên của cái cột đấy (đây là quy tắc quan trọng không được bỏ qua)
- nếu ở trên bảng có chữ viết tay thì cũng phải phân tích thật kỹ xem có phải sản phẩm ko nếu là sản phẩm thì cũng phải đưa vào json, các cái chữ viết tay thông tường sẽ khá xấu nên phải đọc thật kỹ không được để sai 
- có nhiểu trường hợp là sẽ có cái kiểu viết tay ý các cái bản ghi giống nhau ở trong file mà lặp đi lặp lại thì họ chỉ viết mỗi dòng đầu tiên thôi sau đó nó sẽ kẻ 1 dòng kẻ từ cái bản ghi mẫu từ trên xuống cái hàng cuối cùng mà bị lặp lại (đây là quy tắc quan trọng không được bỏ qua)
- các cái chữ viết tay thường màu đỏ 
- 長さ: Extract the numeric value from the "長さ" column các sản phẩm có product_type là AP, EX, 特AP, K型 , ST, NS45°  thì không có 長さ nên trường 長さ này mặc định để rỗng (null) (đây là quy tắc đặc biệt quan trọng không được bỏ qua).
- 員数: Extract the numeric value from the "員数" column.
- オーダーNo: Trích xuất mã định danh cụ thể được tìm thấy ở ô 注文回数 nằm ở cuối trang của cái trang chứa sản phẩm đấy (thường ở định dạng thập phân như "1.6566").
- 工事名:
                1. CÔNG THỨC GHÉP CHUỖI TỔNG QUÁT:
                    [工事名]　[節]　[名称]　[Mã gạch đỏ (nếu có)]　[工事番号]
                2. QUY TẮC CHI TIẾT CHO TỪNG TRƯỜNG:
                    - [工事名]: Lấy sau "工事名:". Chuyển sang Full-width.
                    - [節]: Lấy toàn bộ nội dung trong ngoặc. Thêm hậu tố "節" (nếu chưa có). Định dạng: Full-width (VD: 16 -> １６節).
                    - [名称]:
                        + GIỮ KHOẢNG TRẮNG GỐC: Nếu văn bản gốc có khoảng trắng giữa các từ (VD: 十字柱 内ダイヤフラム), BẮT BUỘC phải giữ lại và chuyển thành dấu cách Full-width (　).
                        + QUY TẮC TỰ ĐỘNG THÊM KHOẢNG CÁCH: 
                            * Sau từ "小梁", BẮT BUỘC thêm một dấu cách Full-width (Ví dụ: "小梁変更" -> "小梁　変更",...).
                            * Sau từ "主材", BẮT BUỘC thêm một dấu cách Full-width (Ví dụ: "主材現場用" -> "主材　現場用",...).
                            * Sau từ "階", BẮT BUỘC thêm một dấu cách Full-width (Ví dụ: "１８階小梁" -> "１８階　小梁",...).
                            * Sau từ "十字柱", BẮT BUỘC thêm một dấu cách Full-width (Ví dụ: "十字柱 内ダイヤフラム" -> "十字柱　内ダイヤフラム",...).
                            階
                        + QUY TẮC LƯỢC BỎ & THAY THẾ:
                            * Nếu cụm từ có chứ "(現場)" thì xóa cả cụm đó đi, trừ trường hợp nếu cụm đó đó chứa FLG thì giữ lại FLG thôi.
                            * Nếu có "ウラ当て(現場)": Xóa toàn bộ cả cụm.
                            * Nếu cụm từ có chứa "ウラ板" ở cuối: Thay bằng "　工場用", còn trường hợp khác thì thôi không thay thế gì cả.
                            * Danh sách chứa các từ xóa nếu từ đó có chứa các từ sau: (裏当て金, 裏当て, 裏板, ワラ当て, ウラ当て, ウラ当, タブウラ板, エプロン, タブ, ウラ板AP流れ止め, ＣＲ裏当て, 流れ止め).
                            * Quy tắc: Chỉ xóa đúng từ khóa trong danh sách, GIỮ LẠI các nội dung khác đi kèm (Ví dụ: "23階エプロン" -> "23階", "現場裏板" -> "現場").
                        + ĐỊNH DẠNG: Chuyển toàn bộ nội dung trường này sang Full-width.	
                    - [Mã gạch đỏ]: Tại mục (SCAW), kiểm tra các dãy số (9110, 9120...). CHỈ lấy nếu có GẠCH CHÂN ĐỎ hoặc KHOANH TRÒN ĐỎ. Giữ nguyên Half-width.	
                    - [工事番号]: Lấy dãy số trong khung "工事番号". Giữ nguyên Half-width.
                3. VÍ DỤ MINH HỌA:
                    - Ví dụ thay thế: 
                    + Gốc: 名称: 十字柱ウラ板
                    + Kết quả: 十字柱　工場用
                    - Ví dụ giữ khoảng trắng & xóa bỏ:
                    + Gốc: 名称: 十字柱 内ダイヤフラム 現場裏板
                    + Kết quả: 十字柱　内ダイヤフラム　現場
- is_processing: trong trường hợp product_type là 特AP và product_size bên trong có chữ cái chứ không phải toàn số (vd: product_size là 12X38XL1 thì is_processing là TRUE còn nếu product_size là 4.5X38X38 hoặc 4.5X38X50 thì is_processing vẫn là False) thì is_processing là TRUE còn lại là FALSE (đây là quy tắc đặc biệt quan trọng không được bỏ qua).
- 員数: Extract the numeric value from the "員数" column.
[TEXT PRESERVATION]
- Preserve original Japanese text as-is.
- Normalize whitespace but do NOT modify or paraphrase the text content.
