---
name: form-kadopita-3-party
description: Sử dụng kỹ năng này để trích xuất dữ liệu có cấu trúc từ tệp PDF hóa đơn Kadopita 3-party (invoice8) cho Sunouchi IT. Kích hoạt kỹ năng này khi người dùng yêu cầu xử lý/trích xuất/phân loại hóa đơn Kadopita 3-party, hoặc khi tài liệu được phân loại là invoice8 / Kadopita 3-party.
compatibility: Windows OS, Python 3.x với venv, cơ sở dữ liệu MySQL cục bộ.
---

# Sunouchi IT - Bộ trích xuất hóa đơn Kadopita 3-party

Kỹ năng này cung cấp các quy tắc, schema và hướng dẫn để trích xuất dữ liệu có cấu trúc từ hóa đơn Kadopita 3-party (invoice8).

## Các tài liệu tham khảo có sẵn
- **`references/extraction_rules.md`** — Chứa schema JSON mục tiêu và các quy tắc trích xuất/chuẩn hóa chi tiết cho hóa đơn Kadopita 3-party.

## Danh sách kiểm tra quy trình
- [ ] **Bước 1: Lấy các quy tắc**
  - Đọc schema trích xuất và các hướng dẫn từ [references/extraction_rules.md](references/extraction_rules.md).
- [ ] **Bước 2: Thực hiện trích xuất**
  - Trích xuất văn bản và dữ liệu từ tệp PDF hóa đơn Kadopita 3-party.
  - Định dạng đầu ra khớp với cấu trúc JSON và áp dụng các quy tắc chính xác được xác định trong tệp tham khảo.
  - **QUAN TRỌNG**: Kiểm tra tên tệp so với bảng ánh xạ bên dưới để giải quyết `customer_code`.

## Lưu ý & Trường hợp biên
- **Tên tệp quyết định `customer_code`**: Trước khi trích xuất dữ liệu, bạn **BẮT BUỘC** phải kiểm tra tên tệp PDF. Nếu tên tệp khớp với bất kỳ từ khóa nào bên dưới, hãy gán mã `customer_code` gồm 6 chữ số tương ứng vào header đã trích xuất. **KHÔNG** ghi đè mã này bằng logic khác.
  * "アイテック南関東" hoặc "アイテック南関東支店" → customer_code = "102020"
  * "ｵｰｴﾑｺｰﾎﾟﾚｰｼｮﾝ" hoặc "㈲ｵｰｴﾑｺｰﾎﾟﾚｰｼｮﾝ" → customer_code = "140200"
  * "石崎ボルト" → customer_code = "110500"
  * "石崎ボルト長岡" → customer_code = "110510"
  * "大川スティール" → customer_code = "140500"
  * "大津鉄工" → customer_code = "140600"
  * "小野建沖縄" → customer_code = "140830"
  * "カガヤ" → customer_code = "150200"
  * "川田工業" → customer_code = "151300"
  * "岸" → customer_code = "160100"
  * "駒井ハルテック" → customer_code = "190500"
  * "サンコー丸亀" → customer_code = "203010"
  * "大陽日酸ｶﾞｽ大阪" → customer_code = "250100"
  * "大陽日酸ｶﾞｽ業務" → customer_code = "250110"
  * "砂山商事" → customer_code = "220400"
  * "星和小山" → customer_code = "230110"
  * "ＴＯＫＡＩ" → customer_code = "290300"
  * "日鉄物産" → customer_code = "311000"
  * "フルサト" → customer_code = "371500"
  * "ムラタ北関東" → customer_code = "420110"
  * "室賀ファスナー" → customer_code = "420200"
  * "MMK開発" hoặc "MMK開発課" → customer_code = "135410"
  * "MMK東北" → customer_code = "135810"
  * "MMK中部" → customer_code = "135900"
  * "MMK関西" → customer_code = "136100"
  * "MMK関西兵庫" → customer_code = "136101"
  * "MMK関西第一課" → customer_code = "136102"
  * "MMK関西第一課兵庫" → customer_code = "136103"
  * "MMK四国" → customer_code = "136200"
  * "MMK北陸" → customer_code = "136300"
  * "MMK中国" → customer_code = "136400"
  * "MMK九州" → customer_code = "136620"
  * "MMKH札幌" → customer_code = "133001"
  * "MMHK関東" → customer_code = "133100"
  * "MMKH東京" → customer_code = "133200"
  * "MMKH東北" → customer_code = "133000"
  * "MMK1-2" → customer_code = "135210"
  * "MMKH新潟" → customer_code = "133800"
  * "金太" → customer_code = "160500"
  * "JKW大阪" → customer_code = "210500"
  * "MMK新潟" → customer_code = "133800"
  * "MMK札幌帯広" → customer_code = "133002"
  * "MMK旭川" → customer_code = "133003"
  * "原産業" → customer_code = "350200"
  * "アイン" → customer_code = "100500"
  * "星和" → customer_code = "230100"
  * "日鉄物産東北" → customer_code = "311030"
  * "日鉄物産九州" → customer_code = "311040"

