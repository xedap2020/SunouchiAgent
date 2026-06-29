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

# Append paths to load config and libraries from the project
sys.path.append("E:/project/sunouchi-it/sunouchi_it")
try:
    from config.config import DB_CONFIG, GEMINI_API_KEY
except ImportError:
    DB_CONFIG = {
        'host': 'localhost',
        'database': 'test_sunouchiit2',
        'user': 'root',
        'password': 'NewRoot@123!',
        'port': 3306
    }
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

import google.generativeai as genai

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Reconfigure stdout/stderr to UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

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
}

def get_schema_from_db(mode):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT shape, rules 
            FROM document_schemas 
            WHERE mode = %s AND is_active = 1
            LIMIT 1
        """, (mode,))
        row = cursor.fetchone()
        return row
    except Exception as e:
        print(f"Error querying schema from database: {e}", file=sys.stderr)
        return None
    finally:
        if conn and conn.is_connected():
            conn.close()

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

def extract_json_from_erp_image(erp_image_path, shape):
    print("Reading ERP screenshot via Gemini Vision...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    img = Image.open(erp_image_path)
    
    prompt = f"""
    Hãy đọc ảnh chụp màn hình ứng dụng ERP này và trích xuất thông tin khớp với cấu trúc JSON mẫu dưới đây.
    Chỉ trả về chuỗi JSON hợp lệ, không chứa ký tự markdown, khối code ```json hay chú thích ngoài lề.
    Các trường không hiển thị hoặc không có dữ liệu hãy để là null.
    
    Cấu trúc JSON mẫu:
    {shape}
    """
    
    response = model.generate_content([prompt, img])
    text = response.text.strip()
    
    # Remove markdown code fences if model output contains them
    text = re.sub(r'^```json\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    text = text.strip()
    
    try:
        return json.loads(text)
    except Exception as e:
        print("Failed to parse extracted JSON from ERP screenshot. Raw response:")
        print(text)
        raise e

def compare_jsons(correct, wrong):
    diffs = []
    
    # Check header
    c_header = correct.get("header", {})
    w_header = wrong.get("header", {})
    
    for key in set(c_header.keys()).union(w_header.keys()):
        c_val = c_header.get(key)
        w_val = w_header.get(key)
        if c_val != w_val:
            diffs.append(f"Header '{key}': Trị đúng='{c_val}' | Trị sai='{w_val}'")
            
    # Check items
    c_items = correct.get("tables", {}).get("items", [])
    w_items = wrong.get("tables", {}).get("items", [])
    
    diffs.append(f"Số lượng sản phẩm: Trị đúng={len(c_items)} hàng | Trị sai={len(w_items)} hàng")
    
    # Simple line by line comparison of items if count matches
    if len(c_items) == len(w_items):
        for idx, (c_item, w_item) in enumerate(zip(c_items, w_items)):
            for key in set(c_item.keys()).union(w_item.keys()):
                c_val = c_item.get(key)
                w_val = w_item.get(key)
                if c_val != w_val:
                    diffs.append(f"Hàng {idx+1} '{key}': Trị đúng='{c_val}' | Trị sai='{w_val}'")
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
            title = item.get("product_title")
            ptype = item.get("product_type")
            psize = item.get("product_size")
            maker = item.get("col_maker")
            mat = item.get("mat_size")
            cat = item.get("category_small")
            
            # Run simple lookup check like search_product_code in db_helper
            conditions = []
            params = []
            if title:
                conditions.append("product_title = %s")
                params.append(str(title).strip())
            if ptype:
                conditions.append("product_type = %s")
                params.append(str(ptype).strip())
            if psize:
                conditions.append("product_size = %s")
                params.append(str(psize).strip())
                
            if not conditions:
                continue
                
            where_clause = " AND ".join(conditions)
            query = f"SELECT code FROM productdata WHERE {where_clause} LIMIT 1"
            cursor.execute(query, params)
            result = cursor.fetchone()
            
            if not result:
                warnings.append(
                    f"Sản phẩm hàng {idx+1} (Title: '{title}', Type: '{ptype}', Size: '{psize}') "
                    "không tìm thấy trong bảng productdata của database!"
                )
    except Exception as e:
        print(f"Error checking master database: {e}", file=sys.stderr)
    finally:
        if conn and conn.is_connected():
            conn.close()
    return warnings

def main():
    parser = argparse.ArgumentParser(description="Fix extraction prompt/rules by comparing PDF and correct ERP screenshot.")
    parser.add_argument("--mode", required=True, help="Invoice mode name, e.g. invoice1")
    parser.add_argument("--pdf", required=True, help="Path to wrong PDF invoice")
    parser.add_argument("--erp", required=True, help="Path to correct ERP screenshot")
    parser.add_argument("--wrong-json", required=True, help="Path to incorrect JSON file from App")
    args = parser.parse_args()

    # Load wrong json
    if not os.path.exists(args.wrong_json):
        print(f"Error: Wrong JSON file not found: {args.wrong_json}", file=sys.stderr)
        sys.exit(1)
    with open(args.wrong_json, "r", encoding="utf-8") as f:
        wrong_json = json.load(f)

    # Get DB schema
    db_schema = get_schema_from_db(args.mode)
    if not db_schema:
        print(f"Error: No schema found in database for mode {args.mode}", file=sys.stderr)
        sys.exit(1)
        
    shape = db_schema['shape']
    current_rules = db_schema['rules']

    # Step 2: Read ERP screenshot using Gemini Vision
    try:
        correct_json = extract_json_from_erp_image(args.erp, shape)
    except Exception as e:
        print(f"Error reading ERP screenshot: {e}", file=sys.stderr)
        sys.exit(1)

    print("\n" + "="*50)
    print("DỮ LIỆU ĐÚNG ĐỌC ĐƯỢC TỪ ẢNH CHỤP ERP:")
    print("="*50)
    print(json.dumps(correct_json, ensure_ascii=False, indent=2))
    print("="*50)
    
    # Prompt user for confirmation (via stdout markers that the agent can parse/interact with)
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
            print(f"Cảnh báo: Chuỗi nhập không phải JSON hợp lệ. Tiếp tục dùng dữ liệu gốc từ ảnh ERP. Lỗi: {e}")

    # Step 3: Compare JSONs
    diffs_summary = compare_jsons(correct_json, wrong_json)
    print("\n" + "="*50)
    print("SAI LỆCH PHÁT HIỆN ĐƯỢC (ĐÚNG vs SAI TỪ APP):")
    print("="*50)
    print(diffs_summary)
    print("="*50)

    if not diffs_summary.strip() or "Trị đúng=" not in diffs_summary:
        print("Không phát hiện sai lệch thực tế nào giữa JSON đúng và JSON lỗi của App. Dừng quy trình.")
        sys.exit(0)

    # Step 4: Check Database Master lookup
    db_warnings = check_database_existence(correct_json)
    if db_warnings:
        print("\n" + "!"*50)
        print("PHÁT HIỆN LỖI DỮ LIỆU MASTER TRONG DATABASE:")
        print("!"*50)
        for warn in db_warnings:
            print(f"⚠️ {warn}")
        print("!"*50)
        print("\nGỢI Ý GIẢI QUYẾT:")
        print("Các lỗi trên là do thiếu dữ liệu mã sản phẩm trong bảng productdata của MySQL.")
        print("Để khắc phục, hãy thêm các bản ghi tương ứng vào database MySQL trước khi chạy lại App.")
        print("Ví dụ SQL mẫu:")
        print("INSERT INTO productdata (code, product_name, col_maker, mat_size, product_title, product_type, product_size) VALUES ('MA_MOI', 'TEN_MOI', 'MAKER', 'MAT_SIZE', 'TITLE', 'TYPE', 'SIZE');")
        print("\nBạn có muốn tiếp tục tối ưu hóa quy tắc trích xuất (Prompt) không? (y/n):")
        sys.stdout.flush()
        ans = sys.stdin.readline().strip().lower()
        if ans not in ('y', 'yes'):
            print("Đã dừng quy trình.")
            sys.exit(0)

    # Step 5: Optimize Prompt Rules via Gemini
    print("\nAnalyzing PDF and current rules to optimize the prompt...")
    pdf_images = convert_pdf_to_pil_images(args.pdf)
    
    prompt = f"""
    Bạn là chuyên gia AI viết prompt trích xuất hóa đơn Nhật Bản.
    Khi trích xuất PDF này bằng quy tắc hiện tại, AI đã sinh ra kết quả sai:
    {json.dumps(wrong_json, ensure_ascii=False, indent=2)}
    
    Nhưng kết quả đúng thực tế phải là:
    {json.dumps(correct_json, ensure_ascii=False, indent=2)}
    
    Các lỗi sai lệch cụ thể cần khắc phục:
    {diffs_summary}
    
    Dưới đây là tài liệu quy tắc trích xuất hiện tại của hóa đơn này:
    {current_rules}
    
    Nhiệm vụ của bạn:
    1. Phân tích hình ảnh PDF đơn hàng để tìm ra nguyên nhân tại sao AI trích xuất sai các trường này.
    2. Cập nhật lại phần hướng dẫn trong mục tương ứng của quy tắc trích xuất hiện tại để sửa các lỗi này.
    
    Yêu cầu:
    - Chỉ sửa đổi hoặc thêm các lưu ý/quy tắc đặc biệt cho các trường bị sai, giữ nguyên toàn bộ các cấu trúc và hướng dẫn khác của các trường đúng.
    - Viết bằng Tiếng Việt rõ ràng, dễ hiểu.
    - Kết quả trả về gồm 2 phần được bao bởi thẻ xml:
      <explanation>Mô tả ngắn gọn nguyên nhân sai lệch và cách sửa đổi bằng tiếng Việt</explanation>
      <rules>[Toàn bộ nội dung quy tắc trích xuất mới]</rules>
    """
    
    model = genai.GenerativeModel('gemini-1.5-pro')
    contents = [prompt]
    contents.extend(pdf_images)
    
    response = model.generate_content(contents)
    response_text = response.text.strip()
    
    # Extract tags
    explanation_match = re.search(r'<explanation>(.*?)</explanation>', response_text, re.DOTALL)
    rules_match = re.search(r'<rules>(.*?)</rules>', response_text, re.DOTALL)
    
    explanation = explanation_match.group(1).strip() if explanation_match else "Không thể trích xuất phần giải thích."
    updated_rules = rules_match.group(1).strip() if rules_match else None
    
    if not updated_rules:
        # Fallback if XML parsing failed
        print("Warning: XML tags not found. Attempting to parse raw response as rules.")
        updated_rules = response_text
        explanation = "Quy tắc được cập nhật trực tiếp từ phản hồi của mô hình."

    print("\n" + "="*50)
    print("PHÂN TÍCH NGUYÊN NHÂN TỪ GEMINI:")
    print("="*50)
    print(explanation)
    print("="*50)

    # Step 6: Database and Local file update
    update_schema_in_db(args.mode, updated_rules)
    
    # Save locally
    folder_name = MAPPING.get(args.mode)
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
            with open(dest_file, "w", encoding="utf-8", newline="\n") as f:
                f.write(content)
            print(f"Successfully updated local file: {dest_file}")
        except Exception as e:
            print(f"Error writing to local file: {e}", file=sys.stderr)

    # Step 7: Dry-Run verify
    print("\nRunning dry-run test with the updated prompt...")
    verify_prompt = f"""
    Hãy trích xuất thông tin từ PDF này tuân thủ chính xác theo định dạng JSON đầu ra bắt buộc và quy tắc trích xuất dưới đây.
    Chỉ trả về chuỗi JSON hợp lệ, không chứa ký tự markdown hay chú thích.
    
    ============================================================
    OUTPUT SHAPE (CẤU TRÚC JSON ĐẦU RA BẮT BUỘC)
    ============================================================
    {shape}
    
    ============================================================
    RULES (QUY TẮC TRÍCH XUẤT)
    ============================================================
    {updated_rules}
    """
    
    verify_model = genai.GenerativeModel('gemini-1.5-flash')
    verify_contents = [verify_prompt]
    verify_contents.extend(pdf_images)
    
    verify_response = verify_model.generate_content(verify_contents)
    verify_text = verify_response.text.strip()
    verify_text = re.sub(r'^```json\s*', '', verify_text)
    text = re.sub(r'\s*```$', '', verify_text)
    
    print("\n" + "="*50)
    print("KẾT QUẢ TRÍCH XUẤT LẠI SAU KHI SỬA PROMPT:")
    print("="*50)
    print(verify_text)
    print("="*50)
    print("\nSửa lỗi và kiểm tra hoàn tất!")

if __name__ == "__main__":
    main()
