# .agents/skills/sunouchi-it/scripts/db_helper.py
import os
import sys

# Reconfigure stdout/stderr to UTF-8 to prevent cp932 encoding errors on Windows terminal
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
if sys.stderr.encoding != 'utf-8':
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

import json
import re
import argparse
import mysql.connector
from mysql.connector import Error
from rapidfuzz import fuzz


# Add project root and sunouchi_it to path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "../../../.."))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, "sunouchi_it"))

try:
    from config import DB_CONFIG
except ImportError:
    # Fallback default configuration if import fails
    DB_CONFIG = {
        'host': 'localhost',
        'database': 'test_sunouchiit2',
        'user': 'root',
        'password': '123456',
        'port': 3306
    }

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def get_active_classify_prompt():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT prompt_text 
            FROM classify_prompts 
            WHERE is_active = 1 
            LIMIT 1
        """)
        result = cursor.fetchone()
        if not result:
            return "Error: No active classify prompt found in database"
        return result['prompt_text']
    except Exception as e:
        return f"Error retrieving classify prompt: {str(e)}"
    finally:
        if conn and conn.is_connected():
            conn.close()

def get_active_schema(mode):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT shape, rules 
            FROM document_schemas 
            WHERE mode = %s AND is_active = 1
            LIMIT 1
        """, (mode,))
        result = cursor.fetchone()
        if not result:
            return None
        return {"shape": result['shape'], "rules": result['rules']}
    except Exception as e:
        print(f"Error retrieving schema for {mode}: {str(e)}", file=sys.stderr)
        return None
    finally:
        if conn and conn.is_connected():
            conn.close()

def search_product_code(cursor, title, product_type, size, col_maker=None, mat_size=None, category_small=None):
    """Tìm kiếm product code từ database - CHỈ SEARCH CHÍNH XÁC (ported from ui_file_manager.py)"""
    try:
        # 1. Search chính xác với TẤT CẢ các trường có sẵn
        conditions = []
        params = []

        if title and str(title).strip():
            conditions.append("product_title = %s")
            params.append(str(title).strip())

        if product_type and str(product_type).strip():
            conditions.append("product_type = %s")
            params.append(str(product_type).strip())

        if size and str(size).strip():
            conditions.append("product_size = %s")
            params.append(str(size).strip())
        
        if col_maker and str(col_maker).strip():
            conditions.append("col_maker = %s")
            params.append(str(col_maker).strip())
        
        if mat_size and str(mat_size).strip():
            conditions.append("mat_size LIKE %s")
            params.append(f"%{str(mat_size).strip()}%")
        
        if category_small and str(category_small).strip():
            conditions.append("category_small = %s")
            params.append(str(category_small).strip())

        if conditions:
            where_clause = " AND ".join(conditions)
            query = f"SELECT code FROM productdata WHERE {where_clause} LIMIT 1"
            cursor.execute(query, params)
            result = cursor.fetchone()
            if result and result.get('code'):
                return result['code']

        # 2. Search chính xác với TỪNG CẶP trường (ưu tiên title + type)
        if title and str(title).strip() and product_type and str(product_type).strip():
            query = "SELECT code FROM productdata WHERE product_title = %s AND product_type = %s LIMIT 1"
            params = (str(title).strip(), str(product_type).strip())
            cursor.execute(query, params)
            result = cursor.fetchone()
            if result and result.get('code'):
                return result['code']

        # 3. Search chính xác title + size
        if title and str(title).strip() and size and str(size).strip():
            query = "SELECT code FROM productdata WHERE product_title = %s AND product_size = %s LIMIT 1"
            params = (str(title).strip(), str(size).strip())
            cursor.execute(query, params)
            result = cursor.fetchone()
            if result and result.get('code'):
                return result['code']

        # 4. Search chính xác title + col_maker
        if title and str(title).strip() and col_maker and str(col_maker).strip():
            query = "SELECT code FROM productdata WHERE product_title = %s AND col_maker = %s LIMIT 1"
            params = (str(title).strip(), str(col_maker).strip())
            cursor.execute(query, params)
            result = cursor.fetchone()
            if result and result.get('code'):
                return result['code']

        # 5. Search chính xác title + mat_size
        if title and str(title).strip() and mat_size and str(mat_size).strip():
            query = "SELECT code FROM productdata WHERE product_title = %s AND mat_size LIKE %s LIMIT 1"
            params = (str(title).strip(), f"%{str(mat_size).strip()}%")
            cursor.execute(query, params)
            result = cursor.fetchone()
            if result and result.get('code'):
                return result['code']

        # 6. Search chính xác title + category_small
        if title and str(title).strip() and category_small and str(category_small).strip():
            query = "SELECT code FROM productdata WHERE product_title = %s AND category_small = %s LIMIT 1"
            params = (str(title).strip(), str(category_small).strip())
            cursor.execute(query, params)
            result = cursor.fetchone()
            if result and result.get('code'):
                return result['code']

        # 7. Search chính xác CHỈ với title
        if title and str(title).strip():
            query = "SELECT code FROM productdata WHERE product_title = %s LIMIT 1"
            cursor.execute(query, (str(title).strip(),))
            result = cursor.fetchone()
            if result and result.get('code'):
                return result['code']

        # 8. Search chính xác CHỈ với product_type
        if product_type and str(product_type).strip():
            query = "SELECT code FROM productdata WHERE product_type = %s LIMIT 1"
            cursor.execute(query, (str(product_type).strip(),))
            result = cursor.fetchone()
            if result and result.get('code'):
                return result['code']

        # 9. Search chính xác col_maker + size
        if col_maker and str(col_maker).strip() and size and str(size).strip():
            query = "SELECT code FROM productdata WHERE col_maker = %s AND product_size = %s LIMIT 1"
            params = (str(col_maker).strip(), str(size).strip())
            cursor.execute(query, params)
            result = cursor.fetchone()
            if result and result.get('code'):
                return result['code']

        # 10. Search chính xác category_small + col_maker
        if category_small and str(category_small).strip() and col_maker and str(col_maker).strip():
            query = "SELECT code FROM productdata WHERE category_small = %s AND col_maker = %s LIMIT 1"
            params = (str(category_small).strip(), str(col_maker).strip())
            cursor.execute(query, params)
            result = cursor.fetchone()
            if result and result.get('code'):
                return result['code']

    except Exception as e:
        print(f"Error searching product code: {e}", file=sys.stderr)
    return None

def search_matsumoto_customer_branch_code(cursor, matsumoto_customer):
    try:
        if matsumoto_customer and str(matsumoto_customer).strip():
            clean = str(matsumoto_customer).strip()
            query = "SELECT branch_code FROM matsumoto_agency_mapping WHERE agency_code = %s LIMIT 1"
            cursor.execute(query, (clean,))
            result = cursor.fetchone()
            if result and result.get('branch_code'):
                return result['branch_code']
            
            query = "SELECT branch_code FROM matsumoto_agency_mapping WHERE agency_code LIKE %s LIMIT 1"
            cursor.execute(query, (f"%{clean}%",))
            result = cursor.fetchone()
            if result and result.get('branch_code'):
                return result['branch_code']
    except Exception as e:
        print(f"Error mapping Matsumoto branch: {e}", file=sys.stderr)
    return None

def search_customer_code(cursor, name1, name2):
    try:
        conditions = []
        params = []
        if name1 and str(name1).strip() and name2 and str(name2).strip():
            conditions.append("name_1 = %s AND name_2 = %s")
            params.extend([str(name1).strip(), str(name2).strip()])
        elif name1 and str(name1).strip():
            conditions.append("name_1 = %s")
            params.append(str(name1).strip())
        elif name2 and str(name2).strip():
            conditions.append("name_2 = %s")
            params.append(str(name2).strip())

        if conditions:
            where_clause = " AND ".join(conditions) if len(conditions) > 1 else conditions[0]
            query = f"SELECT code FROM m_customer WHERE {where_clause} LIMIT 1"
            cursor.execute(query, params)
            result = cursor.fetchone()
            if result and result.get('code'):
                return result['code']

        # Fallback LIKE search
        if name1 and str(name1).strip() or name2 and str(name2).strip():
            like_conditions = []
            like_params = []
            if name1 and str(name1).strip():
                like_conditions.append("name_1 LIKE %s")
                like_params.append(f"%{str(name1).strip()}%")
            if name2 and str(name2).strip():
                like_conditions.append("name_2 LIKE %s")
                like_params.append(f"%{str(name2).strip()}%")
            
            if like_conditions:
                like_clause = " AND ".join(like_conditions)
                query = f"SELECT code FROM m_customer WHERE {like_clause} LIMIT 1"
                cursor.execute(query, like_params)
                result = cursor.fetchone()
                if result and result.get('code'):
                    return result['code']
    except Exception as e:
        print(f"Error searching customer code: {e}", file=sys.stderr)
    return None

def normalize_phone(phone):
    if not phone:
        return ""
    return re.sub(r'[^0-9]', '', str(phone))

def search_supplier_code(cursor, supplier_name=None, supplier_name2=None, supplier_location=None, 
                         supplier_memo=None, supplier_postal_code=None, supplier_tel=None):
    """Tìm kiếm supplier code - fuzzy matching (ported from ui_file_manager.py)"""
    try:
        fuzzy_name = str(supplier_name).strip() if supplier_name else ""
        postal = str(supplier_postal_code).strip() if supplier_postal_code else ""
        tel_raw = str(supplier_tel).strip() if supplier_tel else ""
        tel_normalized = normalize_phone(tel_raw)
        company = str(supplier_name2).strip() if supplier_name2 else ""
        location = str(supplier_location).strip() if supplier_location else ""
        memo = str(supplier_memo).strip() if supplier_memo else ""
        
        cursor.execute("SELECT * FROM m_supplier")
        all_suppliers = cursor.fetchall()
        
        results = []
        for supplier in all_suppliers:
            score = 0
            total_weight = 0
            
            if fuzzy_name:
                name = str(supplier.get('name', ''))
                if name:
                    name_score = (
                        fuzz.ratio(fuzzy_name, name) * 0.15 +
                        fuzz.partial_ratio(fuzzy_name, name) * 0.45 +
                        fuzz.token_sort_ratio(fuzzy_name, name) * 0.2 +
                        fuzz.token_set_ratio(fuzzy_name, name) * 0.2
                    )
                    score += name_score * 0.40
                    total_weight += 40
            
            if postal:
                sup_postal = str(supplier.get('postal_code', ''))
                if sup_postal:
                    postal_score = fuzz.ratio(postal, sup_postal)
                    score += postal_score * 0.25
                    total_weight += 25
            
            if tel_normalized:
                sup_tel_raw = str(supplier.get('tel_no', ''))
                sup_tel_normalized = normalize_phone(sup_tel_raw)
                if sup_tel_normalized:
                    tel_score = max(
                        fuzz.ratio(tel_normalized, sup_tel_normalized),
                        fuzz.partial_ratio(tel_normalized, sup_tel_normalized)
                    )
                    score += tel_score * 0.25
                    total_weight += 25
            
            if company:
                sup_company = str(supplier.get('company_name', ''))
                if sup_company:
                    company_score = fuzz.partial_ratio(company, sup_company)
                    score += company_score * 0.05
                    total_weight += 5
            
            if location:
                sup_location = str(supplier.get('location_name', ''))
                if sup_location:
                    location_score = fuzz.partial_ratio(location, sup_location)
                    score += location_score * 0.03
                    total_weight += 3
            
            if memo:
                sup_sup_memo = str(supplier.get('supplier_memo', ''))
                sup_del_memo = str(supplier.get('delivery_memo', ''))
                memo_score = max(
                    fuzz.partial_ratio(memo, sup_sup_memo),
                    fuzz.partial_ratio(memo, sup_del_memo)
                )
                score += memo_score * 0.02
                total_weight += 2
                
            if total_weight > 0:
                final_score = (score / total_weight) * 100
            else:
                final_score = 0
                
            if final_score > 45:
                results.append({
                    'code': supplier.get('code'),
                    'score': final_score
                })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        if results:
            return results[0]['code']
    except Exception as e:
        print(f"Error searching supplier: {e}", file=sys.stderr)
    return None

def resolve_codes(data, filename=None):
    """Nhận JSON trích xuất thô và đối chiếu tìm kiếm các mã trong database"""
    if not isinstance(data, dict):
        return data
        
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        warnings = []
        
        # 1. Resolve Customer Code
        header = data.get("header", {})
        customer_code = header.get("customer_code")
        
        # Resolve customer_code from filename (takes highest precedence)
        if header:
            if not filename:
                filename = data.get("_original_filename")
            if filename:
                clean_filename = os.path.basename(filename)
                try:
                    mapping_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "customer_mapping.json")
                    if os.path.exists(mapping_path):
                        with open(mapping_path, 'r', encoding='utf-8') as f_map:
                            mapping_data = json.load(f_map)
                        # Sort by length descending to match longest keyword first
                        mapping_data = sorted(mapping_data, key=lambda x: len(x.get("keyword", "")), reverse=True)
                        for item in mapping_data:
                            kw = item.get("keyword")
                            code = item.get("customer_code")
                            if kw and code and kw in clean_filename:
                                header["customer_code"] = code
                                customer_code = code
                                break
                except Exception as e:
                    print(f"Error resolving customer code from filename: {e}", file=sys.stderr)

        # Keep track of initial presence of customer name fields
        has_cust_names = False
        c_name1 = None
        c_name2 = None
        m_cust = None
        
        if header and ("customer_name1" in header or "customer_name2" in header or "matsumoto_customer" in header):
            has_cust_names = True
            c_name1 = header.get("customer_name1")
            c_name2 = header.get("customer_name2")
            m_cust = header.get("matsumoto_customer")
            
        if not customer_code and header:
            matsumoto_customer = header.get("matsumoto_customer")
            if matsumoto_customer and str(matsumoto_customer).strip():
                branch = search_matsumoto_customer_branch_code(cursor, matsumoto_customer)
                if branch:
                    header["customer_code"] = branch
                    customer_code = branch
            
            if not customer_code:
                c_name1_val = header.get("customer_name1")
                c_name2_val = header.get("customer_name2")
                if c_name1_val or c_name2_val:
                    code = search_customer_code(cursor, c_name1_val, c_name2_val)
                    if code:
                        header["customer_code"] = code
                        customer_code = code

        # Log customer warnings
        if has_cust_names and (not customer_code or not str(customer_code).strip()):
            c_name1_str = str(c_name1 or "").strip()
            c_name2_str = str(c_name2 or "").strip()
            m_cust_str = str(m_cust or "").strip()
            
            if not c_name1_str and not c_name2_str and not m_cust_str:
                warnings.append("Thiếu trường tên khách hàng (customer_name1/customer_name2/matsumoto_customer) để tìm customer_code")
            else:
                if m_cust_str:
                    warnings.append(f"Không đối chiếu được customer_code từ mã đại lý Matsumoto: '{m_cust_str}'")
                else:
                    warnings.append(f"Không đối chiếu được customer_code từ tên khách hàng: '{c_name1_str}' / '{c_name2_str}'")
                        
        # 2. Resolve Supplier Code
        has_sup_name = False
        sup_name = None
        if header and ("supplier_name" in header or "supplier_name2" in header):
            has_sup_name = True
            sup_name = header.get("supplier_name")
            
        if header:
            found_supplier = search_supplier_code(
                cursor,
                supplier_name=header.get("supplier_name"),
                supplier_name2=header.get("supplier_name2"),
                supplier_location=header.get("supplier_location"),
                supplier_memo=header.get("supplier_memo"),
                supplier_postal_code=header.get("supplier_postal_code"),
                supplier_tel=header.get("supplier_tel")
            )
            if found_supplier:
                header["supplier_code"] = found_supplier

        # Log supplier warnings
        if has_sup_name:
            sup_code_val = header.get("supplier_code")
            sup_name_str = str(sup_name or "").strip()
            if not sup_code_val or not str(sup_code_val).strip():
                if not sup_name_str:
                    warnings.append("Thiếu trường tên nhà cung cấp (supplier_name) để tìm supplier_code")
                else:
                    warnings.append(f"Không đối chiếu được supplier_code từ tên nhà cung cấp: '{sup_name_str}'")

        # 3. Resolve Product Codes for Items
        tables = data.get("tables", {})
        if "items" in tables and isinstance(tables["items"], list):
            for idx, item in enumerate(tables["items"]):
                if not isinstance(item, dict):
                    continue
                product_title = item.get("product_title")
                product_type = item.get("product_type")
                product_size = item.get("product_size")
                col_maker = item.get("col_maker")
                mat_size = item.get("mat_size")
                category_small = item.get("category_small")
                
                # Check presence of input fields in item
                has_prod_inputs = any(k in item for k in ["product_title", "product_type", "product_size", "col_maker", "mat_size", "category_small"])
                
                found_prod_code = None
                if product_title or product_type or product_size or col_maker or mat_size or category_small:
                    found_prod_code = search_product_code(
                        cursor,
                        title=product_title,
                        product_type=product_type,
                        size=product_size,
                        col_maker=col_maker,
                        mat_size=mat_size,
                        category_small=category_small
                    )
                    if found_prod_code:
                        item["商品コード"] = found_prod_code
                        item["found_by_search"] = True
                    else:
                        item["商品コード"] = ""
                        item["found_by_search"] = False
                else:
                    item["商品コード"] = ""
                    
                # Log product warnings
                if has_prod_inputs:
                    prod_code_val = item.get("商品コード")
                    if not prod_code_val or not str(prod_code_val).strip():
                        title_str = str(product_title or "").strip()
                        type_str = str(product_type or "").strip()
                        size_str = str(product_size or "").strip()
                        
                        if not title_str and not type_str and not size_str and not col_maker and not mat_size and not category_small:
                            warnings.append(f"Dòng sản phẩm thứ {idx+1}: Thiếu trường dữ liệu đầu vào (product_title/product_type/product_size) để tìm 商品コード")
                        else:
                            warnings.append(f"Dòng sản phẩm thứ {idx+1}: Không đối chiếu được 商品コード từ: title='{title_str}', type='{type_str}', size='{size_str}'")
                    
        if warnings:
            data["mapping_warnings"] = warnings
                    
        return data
    except Exception as e:
        print(f"Error resolving codes: {str(e)}", file=sys.stderr)
        return data
    finally:
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sunouchi IT Database Helper for Antigravity")
    parser.add_argument("--action", choices=["get_prompts", "get_schema", "resolve"], required=True)
    parser.add_argument("--mode", help="Document mode (e.g. invoice1, invoice2)")
    parser.add_argument("--json_file", help="Path to raw JSON file for resolution")
    parser.add_argument("--json_str", help="JSON string for resolution")
    
    args = parser.parse_args()
    
    if args.action == "get_prompts":
        prompt = get_active_classify_prompt()
        print("=== ACTIVE CLASSIFY PROMPT ===")
        print(prompt)
        print("=== END CLASSIFY PROMPT ===")
        
    elif args.action == "get_schema":
        if not args.mode:
            print("Error: --mode is required for get_schema", file=sys.stderr)
            sys.exit(1)
        schema = get_active_schema(args.mode)
        if schema:
            print(json.dumps(schema, ensure_ascii=False, indent=2))
        else:
            print(f"Error: Schema not found for mode {args.mode}", file=sys.stderr)
            sys.exit(1)
            
    elif args.action == "resolve":
        raw_data = None
        filename_val = None
        if args.json_file:
            with open(args.json_file, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            filename_val = os.path.basename(args.json_file).replace(".json", ".pdf")
        elif args.json_str:
            raw_data = json.loads(args.json_str)
        else:
            print("Error: Either --json_file or --json_str is required for resolve", file=sys.stderr)
            sys.exit(1)
            
        resolved = resolve_codes(raw_data, filename=filename_val)
        print(json.dumps(resolved, ensure_ascii=False, indent=2))
