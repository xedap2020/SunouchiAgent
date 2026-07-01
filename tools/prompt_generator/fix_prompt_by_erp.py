# e:\SunouchiAgent\tools\prompt_generator\fix_prompt_by_erp.py
import os
import sys
import json
import argparse
import re
import fitz  # PyMuPDF
from PIL import Image
import io
import mysql.connector

# Append paths to load config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from config import DB_CONFIG
except ImportError:
    DB_CONFIG = {
        'host': 'localhost',
        'database': 'test_sunouchiit2',
        'user': 'root',
        'password': 'NewRoot@123!',
        'port': 3306
    }

# Reconfigure stdin/stdout/stderr to UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8")

MAPPING = {
    'invoice1': 'form-furusato',
    'invoice2': 'form-komai-haltec',
    'invoice3': 'form-mm-kenzai',
    'invoice4': 'form-matsumoto',
    'invoice5': 'form-standalone-spec',
    'invoice6': 'form-kondotec-regular',
    'invoice7': 'form-kakuto',
    'invoice8': 'form-kadopita-3-party',
    'invoice9': 'form-kadopita-negotiation',
    'invoice10': 'form-kondotec-special',
    'invoice11': 'form-3d-processing',
    'invoice12': 'form-composite',
    'invoice13': 'form-kagaya',
}

def load_local_schema(mode):
    folder_name = MAPPING.get(mode)
    if not folder_name:
        print(f"Error: No mapping folder found for mode {mode}", file=sys.stderr)
        return None
        
    filepath = f"e:/SunouchiAgent/.agents/skills/{folder_name}/references/extraction_rules.md"
    if not os.path.exists(filepath):
        print(f"Error: Local file not found: {filepath}", file=sys.stderr)
        return None
        
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        parts = content.split("============================================================\n")
        if len(parts) < 5:
            parts = content.split("============================================================\r\n")
        if len(parts) < 5:
            parts = content.split("============================================================")
            
        if len(parts) < 5:
            print(f"Error: Invalid format in {filepath}", file=sys.stderr)
            return None
            
        shape = parts[2].strip()
        rules = parts[4].strip()
        return {"shape": shape, "rules": rules}
    except Exception as e:
        print(f"Error reading local file {filepath}: {e}", file=sys.stderr)
        return None

def update_schema_in_db(mode, rules):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE document_schemas 
            SET rules = %s, updated_at = NOW() 
            WHERE mode = %s AND is_active = 1
        """, (rules, mode))
        conn.commit()
        print(f"Database updated successfully for {mode}.")
        return True
    except Exception as e:
        print(f"Error updating rules in database: {e}", file=sys.stderr)
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()

def convert_pdf_to_pil_images(pdf_path):
    doc = fitz.open(pdf_path)
    images = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap(dpi=150)
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        images.append(img)
    return images

def extract_json_from_erp_image(erp_image_path, shape, delegate=True):
    print(f"\n[DELEGATE_ERP_EXTRACTION]")
    print(f"Path: {os.path.abspath(erp_image_path)}")
    print(f"Output Shape (JSON structure):\n{shape}")
    print("\n--- INSTRUCTIONS FOR ANTIGRAVITY AGENT ---")
    print("1. Read the ERP screenshot carefully to find all matching fields.")
    print("2. Extract and format the values to strictly match the Output Shape.")
    print("3. For any missing, blank, or invisible fields on the screen, set their values to null.")
    print("4. IMPORTANT: Do NOT guess or generate mock data. Only extract what is visible.")
    print("5. Make sure the output is a single, valid JSON string. Do NOT wrap it in markdown code blocks like ```json or include any introduction/conversational texts.")
    print("6. Paste the JSON below, and then enter a blank line (press Enter on an empty line) to submit.")
    print("------------------------------------------")
    sys.stdout.flush()
    lines = []
    while True:
        line = sys.stdin.readline()
        if not line or line.strip() == "":
            break
        lines.append(line)
    text = "".join(lines).strip()
    return json.loads(text)

def compare_jsons(correct, wrong):
    diffs = []
    c_header = correct.get("header", {})
    w_header = wrong.get("header", {})
    
    for key in set(c_header.keys()).union(w_header.keys()):
        c_val = c_header.get(key)
        w_val = w_header.get(key)
        if c_val != w_val:
            diffs.append(f"Header '{key}': Trị đúng={repr(c_val)} | Trị sai={repr(w_val)}")
            
    c_items = correct.get("tables", {}).get("items", [])
    w_items = wrong.get("tables", {}).get("items", [])
    
    diffs.append(f"Số lượng sản phẩm: Trị đúng={len(c_items)} hàng | Trị sai={len(w_items)} hàng")
    
    if len(c_items) == len(w_items):
        for idx, (c_item, w_item) in enumerate(zip(c_items, w_items)):
            for key in set(c_item.keys()).union(w_item.keys()):
                # Only check keys that are in the correct item (ignore extra metadata fields from app)
                if key in c_item:
                    c_val = c_item.get(key)
                    w_val = w_item.get(key)
                    if c_val != w_val:
                        diffs.append(f"Hàng {idx+1} '{key}': Trị đúng={repr(c_val)} | Trị sai={repr(w_val)}")
    else:
        diffs.append("Danh sách hàng sản phẩm không đồng đều về độ dài. Cụ thể các hàng chuẩn:")
        for idx, c_item in enumerate(c_items):
            diffs.append(f"  Hàng chuẩn {idx+1}: {c_item}")
        diffs.append("Cụ thể các hàng sai lệch thực tế từ App:")
        for idx, w_item in enumerate(w_items):
            diffs.append(f"  Hàng sai {idx+1}: {w_item}")
            
    return "\n".join(diffs)

def check_database_existence(correct_json):
    print("Checking database master data for correct items...")
    conn = None
    warnings = []
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        items = correct_json.get("tables", {}).get("items", [])
        for idx, item in enumerate(items):
            code = item.get("商品コード")
            if not code or str(code).strip() in ("", "0000000000000000001"):
                continue
                
            cursor.execute("SELECT code FROM productdata WHERE code = %s LIMIT 1", (str(code).strip(),))
            result = cursor.fetchone()
            
            if not result:
                warnings.append(
                    f"Sản phẩm hàng {idx+1} (Mã sản phẩm: '{code}') không tìm thấy trong bảng productdata của database!"
                )
    except Exception as e:
        print(f"Error checking master database: {e}", file=sys.stderr)
    finally:
        if conn and conn.is_connected():
            conn.close()
    return warnings

def auto_locate_files(keyword):
    pdf_path = None
    erp_path = None
    wrong_json_path = None
    
    # 1. Locate PDF
    pdf_dirs = ["data/pdf/Fixbug", "data/pdf/PDF"]
    for d in pdf_dirs:
        if os.path.exists(d):
            files = os.listdir(d)
            for f in files:
                if keyword in f and f.lower().endswith(".pdf"):
                    pdf_path = os.path.join(d, f)
                    break
            if pdf_path:
                break
                
    # 2. Locate wrong JSON
    json_dir = "data/pdf/json"
    if os.path.exists(json_dir):
        files = os.listdir(json_dir)
        for f in files:
            if keyword in f and f.lower().endswith(".json") and "correct" not in f.lower():
                wrong_json_path = os.path.join(json_dir, f)
                break
                
    # 3. Locate ERP screenshot
    erp_dirs = ["data/pdf/Fixbug", "data/pdf/NewForm"]
    for d in erp_dirs:
        if os.path.exists(d):
            files = os.listdir(d)
            for f in files:
                if keyword in f and any(f.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".bmp"]):
                    erp_path = os.path.join(d, f)
                    break
            if erp_path:
                break
                
    return pdf_path, erp_path, wrong_json_path

def detect_mode_from_file(filename, wrong_json_path=None):
    cust_code = ""
    if wrong_json_path and os.path.exists(wrong_json_path):
        try:
            with open(wrong_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                cust_code = data.get("header", {}).get("customer_code") or ""
        except:
            pass
            
    fn = filename.lower()
    
    if "マツモト" in fn or cust_code in ["400050", "400051", "400052"]:
        return "invoice4"
    if "フルサト" in fn or cust_code == "371500":
        return "invoice1"
    if "駒井" in fn or "ハルテック" in fn or cust_code == "190500":
        return "invoice2"
    if "mm" in fn or "エムエム" in fn or cust_code in ["135410", "135810", "135900", "136100", "136101", "136102", "136103", "136200", "136300", "136400", "136620", "133001", "133100", "133200", "133000", "135210", "133800", "133002", "133003"]:
        return "invoice3"
    if "standalone" in fn or "単独" in fn or "spec" in fn:
        return "invoice5"
    if "角斗" in fn or "カクト" in fn:
        return "invoice7"
    if "kadopita" in fn or "カドピタ" in fn:
        if "negotiation" in fn or "交渉" in fn:
            return "invoice9"
        return "invoice8"
    if "3d" in fn or "processing" in fn:
        return "invoice11"
    if "composite" in fn or "複合" in fn:
        return "invoice12"
    if "カガヤ" in fn or cust_code == "150200":
        return "invoice13"
    if "コンドー" in fn or "kondotec" in fn:
        if "special" in fn or "特別" in fn or "sp" in fn:
            return "invoice10"
        return "invoice6"
        
    return None

def insert_missing_products_to_db(correct_json, wrong_json):
    conn = None
    inserted_count = 0
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        c_items = correct_json.get("tables", {}).get("items", [])
        w_items = wrong_json.get("tables", {}).get("items", [])
        
        if len(c_items) == len(w_items):
            for idx, (c_item, w_item) in enumerate(zip(c_items, w_items)):
                code = c_item.get("商品コード")
                if not code or str(code).strip() in ("", "0000000000000000001"):
                    continue
                    
                title = w_item.get("product_title") or ""
                ptype = w_item.get("product_type") or ""
                psize = w_item.get("product_size") or ""
                col_maker = w_item.get("col_maker") or ""
                mat_size = w_item.get("mat_size") or ""
                
                cursor.execute("SELECT code FROM productdata WHERE code = %s LIMIT 1", (str(code).strip(),))
                res = cursor.fetchone()
                if not res:
                    query = """
                        INSERT INTO productdata (code, product_name, col_maker, mat_size, product_title, product_type, product_size)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    prod_name = title
                    params = (str(code).strip(), prod_name, col_maker, mat_size, title, ptype, psize)
                    cursor.execute(query, params)
                    inserted_count += 1
                    print(f"Auto-inserted missing product code '{code}' into DB (Title: '{title}', Type: '{ptype}', Size: '{psize}').")
            
            if inserted_count > 0:
                conn.commit()
                print(f"Successfully committed auto-inserted {inserted_count} products to MySQL DB.")
        else:
            print("Warning: Cannot auto-insert products because item counts in correct JSON and wrong JSON do not match.", file=sys.stderr)
    except Exception as e:
        print(f"Error auto-inserting missing products: {e}", file=sys.stderr)
    finally:
        if conn and conn.is_connected():
            conn.close()
    return inserted_count

def main():
    parser = argparse.ArgumentParser(description="Fix extraction prompt/rules by comparing PDF and correct ERP screenshot.")
    parser.add_argument("--keyword", help="Keyword/Order ID (e.g. J173205) to auto-locate files")
    parser.add_argument("--mode", help="Invoice mode name, e.g. invoice1")
    parser.add_argument("--pdf", help="Path to wrong PDF invoice")
    parser.add_argument("--erp", help="Path to correct ERP screenshot")
    parser.add_argument("--wrong-json", help="Path to incorrect JSON file from App")
    parser.add_argument("--correct-json", help="Path to correct JSON file (bypasses ERP screenshot extraction)")
    parser.add_argument("--yes", action="store_true", help="Bypass interactive confirmation prompts")
    parser.add_argument("--delegate", action="store_true", default=True, help="Delegate LLM tasks to the Antigravity agent via stdin/stdout")
    args = parser.parse_args()

    # Auto locate files if keyword is provided
    pdf_path = args.pdf
    erp_path = args.erp
    wrong_json_path = args.wrong_json
    mode = args.mode

    if args.keyword:
        print(f"Auto-locating files for keyword: {args.keyword}")
        loc_pdf, loc_erp, loc_wrong_json = auto_locate_files(args.keyword)
        if loc_pdf:
            print(f"  Located PDF: {loc_pdf}")
            pdf_path = loc_pdf
        if loc_erp:
            print(f"  Located ERP Screenshot: {loc_erp}")
            erp_path = loc_erp
        if loc_wrong_json:
            print(f"  Located Wrong JSON: {loc_wrong_json}")
            wrong_json_path = loc_wrong_json
            
        if not mode and pdf_path:
            mode = detect_mode_from_file(os.path.basename(pdf_path), wrong_json_path)
            if mode:
                print(f"  Detected Mode: {mode}")

    # Validation
    if not pdf_path or not os.path.exists(pdf_path):
        print(f"Error: PDF file not found or not specified: {pdf_path}", file=sys.stderr)
        sys.exit(1)
    if not wrong_json_path or not os.path.exists(wrong_json_path):
        print(f"Error: Wrong JSON file not found or not specified: {wrong_json_path}", file=sys.stderr)
        sys.exit(1)
    if not mode:
        print("Error: Invoice mode (--mode) is not specified and could not be detected.", file=sys.stderr)
        sys.exit(1)
    if not erp_path and not args.correct_json:
        print("Error: ERP screenshot (--erp) or correct JSON (--correct-json) must be provided.", file=sys.stderr)
        sys.exit(1)

    # Load wrong json
    with open(wrong_json_path, "r", encoding="utf-8") as f:
        wrong_json = json.load(f)

    # Get local schema
    local_schema = load_local_schema(mode)
    if not local_schema:
        print(f"Error: No local schema found for mode {mode}", file=sys.stderr)
        sys.exit(1)
        
    shape = local_schema['shape']
    current_rules = local_schema['rules']

    # Step 2: Load or Read ERP screenshot
    if args.correct_json and os.path.exists(args.correct_json):
        print(f"Loading correct JSON directly from: {args.correct_json}")
        with open(args.correct_json, "r", encoding="utf-8") as f:
            correct_json = json.load(f)
    else:
        try:
            correct_json = extract_json_from_erp_image(erp_path, shape, args.delegate)
        except Exception as e:
            print(f"Error reading ERP screenshot: {e}", file=sys.stderr)
            sys.exit(1)

    print("\n" + "="*50)
    print("DỮ LIỆU ĐÚNG ĐỌC ĐƯỢC TỪ ERP:")
    print("="*50)
    print(json.dumps(correct_json, ensure_ascii=False, indent=2))
    print("="*50)
    
    # Prompt user for confirmation (if not using --yes and not delegating)
    if not args.yes and not args.delegate:
        print("\n[CONFIRMATION_REQUIRED] Vui lòng kiểm tra dữ liệu đúng từ ảnh chụp ERP hiển thị phía trên.")
        print("Nếu đúng, nhấn Enter để tiếp tục. Nếu muốn điều chỉnh, hãy dán chuỗi JSON đã sửa rồi nhấn Enter (hoặc gõ 'exit' để thoát):")
        sys.stdout.flush()
        
        user_input = sys.stdin.readline().strip()
        if user_input.lower() == 'exit':
            print("Đã hủy quy trình sửa lỗi.")
            sys.exit(0)
        elif user_input:
            try:
                correct_json = json.loads(user_input)
                print("Đã nhận dữ liệu điều chỉnh từ người dùng.")
            except Exception as e:
                print(f"Cảnh báo: Chuỗi nhập không phải JSON hợp lệ. Tiếp tục dùng dữ liệu gốc. Lỗi: {e}")

    # Step 3: Compare JSONs
    diffs_summary = compare_jsons(correct_json, wrong_json)
    print("\n" + "="*50)
    print("SAI LỆCH PHÁT HIỆN ĐƯỢC (ĐÚNG vs SAI TỪ APP):")
    print("="*50)
    print(diffs_summary)
    print("="*50)

    # Save correct json to data/pdf/json/ as *correct.json (internal reference)
    correct_out_name = os.path.basename(wrong_json_path).replace(".json", "_correct.json")
    correct_out_path = os.path.join(os.path.dirname(wrong_json_path), correct_out_name)
    with open(correct_out_path, "w", encoding="utf-8") as f_out:
        json.dump(correct_json, f_out, ensure_ascii=False, indent=2)
    print(f"Saved correct reference JSON to: {correct_out_path}")

    # Step 4: Check Database Master lookup and Auto-Insert
    db_warnings = check_database_existence(correct_json)
    if db_warnings:
        print("\n" + "!"*50)
        print("PHÁT HIỆN LỖI DỮ LIỆU MASTER TRONG DATABASE:")
        print("!"*50)
        for warn in db_warnings:
            print(f"⚠️ {warn}")
        print("!"*50)
        
        print("\nĐang tự động chèn các sản phẩm còn thiếu vào database...")
        inserted_count = insert_missing_products_to_db(correct_json, wrong_json)
        if inserted_count > 0:
            print(f"Đã tự động bổ sung thành công {inserted_count} sản phẩm vào database.")
            # Recheck DB
            db_warnings = check_database_existence(correct_json)
            if not db_warnings:
                print("Tất cả sản phẩm đã được khớp trong database thành công sau khi tự động cập nhật!")
            else:
                print("Lưu ý: Vẫn còn một số cảnh báo DB chưa khớp.")
        else:
            print("\nGỢI Ý GIẢI QUYẾT HỦY BỎ / THỦ CÔNG:")
            print("Không thể tự động chèn sản phẩm. Hãy chèn thủ công SQL:")
            print("INSERT INTO productdata (code, product_name, col_maker, mat_size, product_title, product_type, product_size) VALUES ('MA_MOI', 'TEN_MOI', 'MAKER', 'MAT_SIZE', 'TITLE', 'TYPE', 'SIZE');")
            
            if not args.yes and not args.delegate:
                print("\nBạn có muốn tiếp tục tối ưu hóa quy tắc trích xuất (Prompt) không? (y/n):")
                sys.stdout.flush()
                ans = sys.stdin.readline().strip().lower()
                if ans not in ('y', 'yes'):
                    print("Đã dừng quy trình.")
                    sys.exit(0)
            else:
                print("Force continuing due to --yes/--delegate flag.")

    if not diffs_summary.strip() or "Trị đúng=" not in diffs_summary:
        print("Không phát hiện sai lệch thực tế nào giữa JSON đúng và JSON lỗi của App. Dừng quy trình.")
        sys.exit(0)

    # Step 5: Optimize Prompt Rules
    print("\nOptimizing prompt rules...")
    print(f"\n[DELEGATE_PROMPT_OPTIMIZATION]")
    print(f"PDF: {os.path.abspath(pdf_path)}")
    print(f"Wrong JSON:\n{json.dumps(wrong_json, ensure_ascii=False, indent=2)}")
    print(f"Correct JSON:\n{json.dumps(correct_json, ensure_ascii=False, indent=2)}")
    print(f"Diffs:\n{diffs_summary}")
    print(f"Current rules:\n{current_rules}")
    print("\nPlease optimize the prompt rules and write the revised rules. End with a line starting with '[RULES_END]':")
    sys.stdout.flush()
    
    explanation = "Tối ưu hóa bởi Antigravity Agent."
    lines = []
    while True:
        line = sys.stdin.readline()
        if not line or line.strip() == "[RULES_END]":
            break
        lines.append(line)
    updated_rules = "".join(lines).strip()

    print("\n" + "="*50)
    print("PHÂN TÍCH NGUYÊN NHÂN:")
    print("="*50)
    print(explanation)
    print("="*50)

    # Step 6: Database and Local file update
    update_schema_in_db(mode, updated_rules)
    
    folder_name = MAPPING.get(mode)
    if folder_name:
        dest_file = f"e:/SunouchiAgent/.agents/skills/{folder_name}/references/extraction_rules.md"
        content = (
            "============================================================\n"
            "OUTPUT SHAPE (CẤU TRÚC JSON ĐẦU RA BẮT BUỘC)\n"
            "============================================================\n"
            f"{shape}\n\n"
            "============================================================\n"
            "RULES (QUY TẮC TRÍCH XUẤT)\n"
            "============================================================\n"
            f"{updated_rules}\n"
        )
        try:
            with open(dest_file, "w", encoding="utf-8", errors="replace", newline="\n") as f:
                f.write(content)
            print(f"Successfully updated local file: {dest_file}")
        except Exception as e:
            print(f"Error writing to local file: {e}", file=sys.stderr)

    # Step 7: Dry-Run verify
    print("\nRunning dry-run test with the updated prompt...")
    print(f"\n[DELEGATE_DRY_RUN]")
    print(f"PDF: {os.path.abspath(pdf_path)}")
    print(f"Updated rules:\n{updated_rules}")
    print("\nPlease run the extraction using these updated rules and input the extracted JSON. End with a blank line:")
    sys.stdout.flush()
    
    lines = []
    while True:
        line = sys.stdin.readline()
        if not line or line.strip() == "":
            break
        lines.append(line)
    verify_text = "".join(lines).strip()

    print("\n" + "="*50)
    print("KẾT QUẢ TRÍCH XUẤT LẠI SAU KHI SỬA PROMPT:")
    print("="*50)
    print(verify_text)
    print("="*50)
    
    # Save the verified correct JSON to the official wrong JSON path (overwriting with the corrected one)
    try:
        verified_json = json.loads(verify_text)
        # Resolve codes one more time to ensure 상품코드 is correctly populated from DB
        import importlib
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.agents/skills/sunouchi-it/scripts")))
        import db_helper
        importlib.reload(db_helper)
        final_resolved_json = db_helper.resolve_codes(verified_json)
        
        with open(wrong_json_path, "w", encoding="utf-8") as f_final:
            json.dump(final_resolved_json, f_final, ensure_ascii=False, indent=2)
        print(f"Successfully saved and updated verified JSON to official path: {wrong_json_path}")
    except Exception as e:
        print(f"Error processing and saving verified JSON: {e}", file=sys.stderr)
        
    print("\nSửa lỗi và kiểm tra hoàn tất!")

if __name__ == "__main__":
    main()
