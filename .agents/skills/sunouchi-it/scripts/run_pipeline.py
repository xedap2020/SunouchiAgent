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

def clean_directory(dir_path):
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    os.makedirs(dir_path, exist_ok=True)

def run_compress_all(input_dir, temp_dir, image_dir=None):
    if not os.path.exists(input_dir):
        print(f"Error: Input directory {input_dir} does not exist", file=sys.stderr)
        sys.exit(1)
        
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print(f"Warning: No PDF files found in {input_dir}")
        return
        
    print(f"Found {len(pdf_files)} PDF files in {input_dir} to process:")
    for f in pdf_files:
        print(f"  - {f}")
        
    print(f"Cleaning temporary directory: {temp_dir}")
    clean_directory(temp_dir)
    for pdf_file in pdf_files:
        in_path = os.path.join(input_dir, pdf_file)
        out_path = os.path.join(temp_dir, pdf_file)
        print(f"Compressing: {pdf_file}...")
        compress_pdf(in_path, out_path, image_dir=image_dir)
    print("All PDF files compressed successfully!")

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimized Batch PDF Pipeline Orchestrator")
    parser.add_argument("--action", choices=["compress_all", "resolve_batch"], required=True)
    parser.add_argument("--input_dir", default="data/pdf/PDF")
    parser.add_argument("--temp_dir", default="data/temp_compress")
    parser.add_argument("--json_file", help="Path to batch raw JSON file (required for resolve_batch)")
    parser.add_argument("--output_dir", default="data/pdf/json")
    parser.add_argument("--image_dir", default="data/pdfToJPG")
    
    args = parser.parse_args()
    
    if args.action == "compress_all":
        run_compress_all(args.input_dir, args.temp_dir, args.image_dir)
    elif args.action == "resolve_batch":
        if not args.json_file:
            print("Error: --json_file is required for resolve_batch action", file=sys.stderr)
            sys.exit(1)
        run_resolve_batch(args.json_file, args.output_dir, args.temp_dir)
