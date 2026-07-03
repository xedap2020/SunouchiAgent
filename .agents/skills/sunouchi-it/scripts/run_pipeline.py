# .agents/skills/sunouchi-it/scripts/run_pipeline.py
import os
import sys
import json
import shutil
import argparse
import fitz  # PyMuPDF

# Add paths to load db_helper and compress_pdf
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

import db_helper
from compress_pdf import compress_pdf
from update_local_rules import update_rules


def clean_directory(dir_path):
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    os.makedirs(dir_path, exist_ok=True)

def run_compress_all(input_dir, temp_dir, image_dir=None, files_to_compress=None):
    if not os.path.exists(input_dir):
        print(f"Error: Input directory {input_dir} does not exist", file=sys.stderr)
        sys.exit(1)
        
    if files_to_compress:
        pdf_files = [f.strip() for f in files_to_compress if f.strip().lower().endswith('.pdf')]
    else:
        pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
        
    if not pdf_files:
        print(f"Warning: No PDF files to process")
        return
        
    print(f"Found {len(pdf_files)} PDF files to process:")
    for f in pdf_files:
        print(f"  - {f}")
        
    print(f"Cleaning temporary directory: {temp_dir}")
    clean_directory(temp_dir)
    for pdf_file in pdf_files:
        in_path = os.path.join(input_dir, pdf_file)
        out_path = os.path.join(temp_dir, pdf_file)
        print(f"Compressing: {pdf_file}...")
        compress_pdf(in_path, out_path, image_dir=image_dir)
    print("PDF files compressed successfully!")

def run_resolve_batch(batch_json_path, output_dir, temp_dir):
    # Enable terminal coloring on Windows
    os.system("")
    
    if not os.path.exists(batch_json_path):
        print(f"Error: Batch JSON file {batch_json_path} does not exist", file=sys.stderr)
        sys.exit(1)
        
    with open(batch_json_path, 'r', encoding='utf-8') as f:
        batch_data = json.load(f)
        
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Resolving database codes for {len(batch_data)} documents...")
    all_warnings = {}
    for filename, raw_json in batch_data.items():
        # Strip path or extensions from filename if needed for output
        base_name, _ = os.path.splitext(filename)
        output_filename = f"{base_name}.json"
        
        print(f"Resolving: {filename}...")
        resolved_json = db_helper.resolve_codes(raw_json)
        
        # Collect warnings
        warnings = resolved_json.get("mapping_warnings", [])
        if warnings:
            all_warnings[filename] = warnings
        
        # Write to data/pdf/json/<filename>.json
        out_path = os.path.join(output_dir, output_filename)
        with open(out_path, 'w', encoding='utf-8') as f_out:
            json.dump(resolved_json, f_out, ensure_ascii=False, indent=2)
            
        print(f"Saved resolved JSON to {out_path}")
        
    # Clean up temporary directory
    print(f"Cleaning up temporary directory: {temp_dir}")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        
    # Clean up batch raw JSON file
    print(f"Cleaning up batch raw JSON file: {batch_json_path}")
    if os.path.exists(batch_json_path):
        os.remove(batch_json_path)
        
    # Print warnings summary if any
    if all_warnings:
        print("\n\033[93m\033[1m⚠️  CẢNH BÁO ĐỐI CHIẾU THIẾU TRƯỜNG DỮ LIỆU / THẤT BẠI:\033[0m")
        for file, warns in all_warnings.items():
            print(f"  📂 File: \033[96m{file}\033[0m")
            for w in warns:
                print(f"    - \033[93m{w}\033[0m")
        print()
        
    print("Batch resolution and cleanup completed successfully!")

def run_delete_slip(files_to_delete, input_dir="data/pdf/PDF", temp_dir="data/temp_compress", output_dir="data/pdf/json", image_dir="data/pdfToJPG"):
    if not files_to_delete:
        print("Warning: No files specified to delete")
        return
        
    # Standardize search terms
    search_terms = [f.strip() for f in files_to_delete if f.strip()]
    if not search_terms:
        return
        
    # Directories to scan for matching files
    scan_dirs = [input_dir, "data/pdf/Fixbug", temp_dir, output_dir]
    
    # We want to identify the base names of matched files
    matched_base_names = set()
    
    for term in search_terms:
        term_lower = term.lower()
        # Scan files in dirs
        for s_dir in scan_dirs:
            if os.path.exists(s_dir):
                for entry in os.listdir(s_dir):
                    if os.path.isfile(os.path.join(s_dir, entry)):
                        if term_lower in entry.lower():
                            base, _ = os.path.splitext(entry)
                            # Handle potential double extension or dots
                            if base.endswith('.'):
                                matched_base_names.add(base)
                            else:
                                matched_base_names.add(base)
                            
        # Scan image directory
        if os.path.exists(image_dir):
            for entry in os.listdir(image_dir):
                if os.path.isdir(os.path.join(image_dir, entry)):
                    if term_lower in entry.lower():
                        matched_base_names.add(entry)
                        
    if not matched_base_names:
        print(f"No files or directories matching: {', '.join(search_terms)}")
        return
        
    print(f"Found {len(matched_base_names)} unique matching slips/files to delete:")
    for base in matched_base_names:
        print(f"  - {base}")
        
    for base_name in matched_base_names:
        print(f"Processing deletion for: {base_name}")
        
        pdf_filename = f"{base_name}.pdf"
        json_filename = f"{base_name}.json"
        
        # Candidate paths to delete
        paths_to_delete = [
            os.path.join(input_dir, pdf_filename),
            os.path.join("data/pdf/Fixbug", pdf_filename),
            os.path.join(temp_dir, pdf_filename),
            os.path.join(output_dir, json_filename),
        ]
        
        # Image directory candidates
        img_dir_candidates = [
            os.path.join(image_dir, base_name),
            os.path.join(image_dir, base_name.rstrip('.')),
        ]
        
        for path in paths_to_delete:
            if os.path.exists(path):
                try:
                    os.remove(path)
                    print(f"  Deleted file: {path}")
                except Exception as e:
                    print(f"  Error deleting file {path}: {str(e)}", file=sys.stderr)
                    
        for img_dir in img_dir_candidates:
            if os.path.exists(img_dir) and os.path.isdir(img_dir):
                try:
                    shutil.rmtree(img_dir)
                    print(f"  Deleted image directory: {img_dir}")
                except Exception as e:
                    print(f"  Error deleting directory {img_dir}: {str(e)}", file=sys.stderr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimized Batch PDF Pipeline Orchestrator")
    parser.add_argument("--action", choices=["compress_all", "resolve_batch", "update_rules", "delete_slip"], required=True)
    parser.add_argument("--input_dir", default="data/pdf/PDF")
    parser.add_argument("--temp_dir", default="data/temp_compress")
    parser.add_argument("--json_file", help="Path to batch raw JSON file (required for resolve_batch)")
    parser.add_argument("--output_dir", default="data/pdf/json")
    parser.add_argument("--image_dir", default="data/pdfToJPG")
    parser.add_argument("--files", help="Comma-separated list of specific PDF/JSON filenames or base names to delete/process")
    parser.add_argument("--mode", default="all", help="Specific invoice mode (e.g. invoice4) or 'all' for update_rules action")
    
    args = parser.parse_args()
    
    if args.action == "compress_all":
        files_to_compress = None
        if args.files:
            files_to_compress = args.files.split(",")
        run_compress_all(args.input_dir, args.temp_dir, args.image_dir, files_to_compress)
    elif args.action == "resolve_batch":
        if not args.json_file:
            print("Error: --json_file is required for resolve_batch action", file=sys.stderr)
            sys.exit(1)
        run_resolve_batch(args.json_file, args.output_dir, args.temp_dir)
    elif args.action == "update_rules":
        success = update_rules(args.mode)
        sys.exit(0 if success else 1)
    elif args.action == "delete_slip":
        if not args.files:
            print("Error: --files is required for delete_slip action", file=sys.stderr)
            sys.exit(1)
        files_to_delete = args.files.split(",")
        run_delete_slip(files_to_delete, args.input_dir, args.temp_dir, args.output_dir, args.image_dir)
