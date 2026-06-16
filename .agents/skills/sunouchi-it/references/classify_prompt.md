Classify text into ONLY one of: "invoice1" to "invoice13". Return code ONLY (no explanation/markdown).

Rules:
- invoice1 (Furusato): Title "発注票" + Issuer "フルサト工業株式会社" + Recipient "(株) スノウチ 様" or "株式会社スノウチ 様". Exclude: "エムエム建材", "カドピタ", "コンドーテック", "KONDOTEC".
- invoice2 (Komai Haltec): Title "工事（形鋼）注文明細書兼材料出庫指令票（鉄構）" + Issuer "(株)駒井ハルテック" + contains "工事番号" and drawings.
- invoice3 (MM Kenzai): Title "発注票" (or Furusato table) + Issuer "エムエム建材販売(株)" or "エムエム建材(株)" + Product contains "カドピタ". Exclude titles: "引合書", "カドピタ引合書", "カドピタ 注文書", "様式NO.QMB4.6.1-12B-03".
- invoice4 (Matsumoto): Title "発注書" + Issuer "マツモト産業（株）" + Table cols: "注番", "品名・規格", "数量", "売上", "仕入".
- invoice5 (Standalone Spec): Title "現寸指示書" + keywords: "大梁", "APRON", "エンドタブ", "ウラ当て", "スプライス", "引引き". Exclude: preceded by "注文書" cover sheet (if page 1 is MM Kenzai order to Sunouchi, it is invoice12).
- invoice6 (Kondotec Regular): Name "コンドーテック株式会社" or "KONDOTEC" + Title "発注書". Exclude steel grades: BCR, BCP, STKT, GJ-R, GJ (if present, use invoice10).
- invoice7 (Kakuto): Title "部品・副資材等注文書" + Recipient "ムラタ産業(株) 御中" + Issuer "(株)角藤 鉄構事業部".
- invoice8 (Kadopita 3-party): Code "様式NO.QMB4.6.1-12B-03" or "様式NO.QMB4.6.1-128-03" + Title "カドピタ 注文書" + contains "エムエム建材(株)", "ムラタ産業(株)", "(株)角藤" + note "※ 数量 là カドピタの本数(1箇所2本)" (or referencing "数量" and "カドピタ").
- invoice9 (Kadopita Negotiation): Title "カドピタ引合書" + Issuer "エムエム建材販売株式会社".
- invoice10 (Kondotec Special): Name "コンドーテック株式会社" or "KONDOTEC" + Title "発注書" or "注文書" + contains steel grade: BCR, BCP, STKT, GJ-R, GJ.
- invoice11 (3D Processing): Title "引合書" (no "カドピタ") + Recipient "宛先:株式会社スノウチ" + 6 technical 3D drawings (TP, HP, SR, NS, SP, BC) + Table cols: "行番", "商品分類", "型番", "size(型番・厚さ・幅)".
- invoice12 (Composite): Page 1 is cover "注文書" from "エムエム建材株式会社" to "株式会社スノウチ". Subsequent pages are "現寸指示書". Contains: "カドピタ", "コラム柱", "メーカー: 佐々木製罐工業" (or ササキ), "川岸工業".
- invoice13 (Kagaya): Title "発注明細書" + Issuer "株式会社カガヤ" or "株式会社 カガヤ" + Recipient "(株) スノウチ" or "(株)スノウチ" + Table cols: "符号", "材質", "長さ", "本数".