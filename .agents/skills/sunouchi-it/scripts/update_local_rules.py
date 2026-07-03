# .agents/skills/sunouchi-it/scripts/update_local_rules.py
import os
import sys
import argparse
import mysql.connector

# Reconfigure stdout/stderr to UTF-8
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

# Add path to config.py
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "../../../.."))
sys.path.append(project_root)

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

# Mapping between DB mode and local skill directory name
MODE_TO_SKILL_FOLDER = {
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

def update_rules(target_mode):
    conn = None
    try:
        print(f"Connecting to database '{DB_CONFIG['database']}' on '{DB_CONFIG['host']}'...")
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # Read-only query to retrieve latest rules and shapes (satisfying read-only database restriction)
        if target_mode.lower() == 'all':
            query = "SELECT mode, description, shape, rules FROM document_schemas WHERE is_active = 1"
            cursor.execute(query)
        else:
            query = "SELECT mode, description, shape, rules FROM document_schemas WHERE mode = %s AND is_active = 1"
            cursor.execute(query, (target_mode,))
            
        records = cursor.fetchall()
        if not records:
            print(f"No active document schema records found for mode '{target_mode}' in database.")
            return False
            
        print(f"Retrieved {len(records)} active schema records from database. Updating local extraction rules...")
        
        success_count = 0
        for row in records:
            mode = row['mode']
            desc = row.get('description', '')
            shape = row.get('shape', '').strip()
            rules = row.get('rules', '').strip()
            
            skill_folder = MODE_TO_SKILL_FOLDER.get(mode)
            if not skill_folder:
                print(f"Warning: No local skill folder mapped for mode '{mode}' (Description: {desc}). Skipping.")
                continue
                
            local_rules_path = os.path.join(project_root, ".agents", "skills", skill_folder, "references", "extraction_rules.md")
            local_rules_dir = os.path.dirname(local_rules_path)
            
            # Ensure the directory exists
            os.makedirs(local_rules_dir, exist_ok=True)
            
            # Assemble the standard rule file content
            content = f"""============================================================
OUTPUT SHAPE (CẤU TRÚC JSON ĐẦU RA BẮT BUỘC)
============================================================
{shape}

============================================================
RULES (QUY TẮC TRÍCH XUẤT)
============================================================
{rules}
"""
            
            # Write to file
            with open(local_rules_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print(f"Successfully updated rules for {mode} ({desc}) at: .agents/skills/{skill_folder}/references/extraction_rules.md")
            success_count += 1
            
        print(f"\nUpdate completed: Successfully updated {success_count} local extraction rule files.")
        return True
        
    except Exception as e:
        print(f"Error during update: {e}", file=sys.stderr)
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update local extraction rules from the MySQL database (READ-ONLY database access).")
    parser.add_argument("--mode", default="all", help="Specific invoice mode (e.g. invoice4) or 'all' to update all active templates.")
    args = parser.parse_args()
    
    success = update_rules(args.mode)
    sys.exit(0 if success else 1)
