# tools/prompt_generator/onboard_prep.py
import os
import sys
import re
import glob
import json
import fitz  # PyMuPDF
from PIL import Image
from io import BytesIO

def clean_name(name):
    # Normalize whitespaces
    return re.sub(r'\s+', ' ', name).strip()

def extract_order_code(filename):
    # Extract pattern like J167095 or J164922.25
    match = re.search(r'(J\d{6}(?:\.\d+)?)', filename)
    return match.group(1) if match else None

def convert_pdf_to_images(pdf_path, output_dir):
    """Converts PDF pages into JPG images and saves them in the output directory."""
    print(f"Converting PDF: {os.path.basename(pdf_path)}...")
    doc = fitz.open(pdf_path)
    os.makedirs(output_dir, exist_ok=True)
    page_images = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap(dpi=150)
        img_data = pix.tobytes("jpeg")
        
        output_filename = f"page_{page_num + 1}.jpg"
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, "wb") as f:
            f.write(img_data)
            
        page_images.append(os.path.abspath(output_path).replace("\\", "/"))
        
    return page_images

def find_pdf_erp_pairs(new_form_dir):
    """Scans and pairs PDFs with ERP screenshots using name matching and order codes."""
    pdf_files = glob.glob(os.path.join(new_form_dir, "*.pdf"))
    all_images = glob.glob(os.path.join(new_form_dir, "*.*"))
    img_files = [f for f in all_images if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    pairs = []
    
    for pdf_path in pdf_files:
        pdf_name = os.path.basename(pdf_path)
        pdf_base, _ = os.path.splitext(pdf_name)
        pdf_code = extract_order_code(pdf_name)
        
        matched_screenshots = []
        
        # 1. Look for images with exact same base name
        for img_path in img_files:
            img_name = os.path.basename(img_path)
            img_base, _ = os.path.splitext(img_name)
            
            # Match if exact base name
            if clean_name(pdf_base) == clean_name(img_base):
                matched_screenshots.append(img_path)
                continue
                
            # Match if base name with suffix like _1, _2, -1, -2
            suffix_pattern = re.escape(clean_name(pdf_base)) + r'[-_]\d+'
            if re.match(suffix_pattern, clean_name(img_base)):
                matched_screenshots.append(img_path)
                continue
                
            # Match if backward compatible code-based match (e.g. pdf contains J167095 and img is J167095.png)
            if pdf_code:
                # Match if image name is exactly the code, or starts/ends with the code with suffix
                code_pattern = r'^' + re.escape(pdf_code) + r'([-_].*)?$'
                if re.match(code_pattern, img_base):
                    matched_screenshots.append(img_path)
                    
        # Remove duplicates while preserving order
        unique_screenshots = []
        for path in matched_screenshots:
            abs_path = os.path.abspath(path).replace("\\", "/")
            if abs_path not in unique_screenshots:
                unique_screenshots.append(abs_path)
                
        # Sort screenshots by index/suffix
        unique_screenshots.sort(key=lambda x: [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', x)])
        
        if unique_screenshots:
            pairs.append({
                "pdf_filename": pdf_name,
                "pdf_path": os.path.abspath(pdf_path).replace("\\", "/"),
                "order_code": pdf_code,
                "base_name": pdf_base,
                "erp_screenshots": unique_screenshots
            })
            
    return pairs

def main():
    new_form_dir = "data/pdf/NewForm"
    temp_onboard_dir = "data/temp_onboard"
    
    if not os.path.exists(new_form_dir):
        print(f"Error: Directory {new_form_dir} does not exist.", file=sys.stderr)
        sys.exit(1)
        
    pairs = find_pdf_erp_pairs(new_form_dir)
    
    if not pairs:
        print("No matching PDF-ERP screenshot pairs found in NewForm directory.", file=sys.stderr)
        sys.exit(1)
        
    print(f"Found {len(pairs)} pairs to process. Creating temporary files...")
    
    request_data = []
    
    for pair in pairs:
        # Create folder named after the PDF base name (cleaned)
        folder_name = clean_name(pair["base_name"]).replace(" ", "_")
        pdf_temp_dir = os.path.join(temp_onboard_dir, folder_name)
        
        # Convert PDF pages
        page_images = convert_pdf_to_images(pair["pdf_path"], pdf_temp_dir)
        
        request_data.append({
            "order_code": pair["order_code"],
            "pdf_filename": pair["pdf_filename"],
            "pdf_path": pair["pdf_path"],
            "pdf_page_images": page_images,
            "erp_screenshots": pair["erp_screenshots"]
        })
        
    # Write request JSON file
    os.makedirs(temp_onboard_dir, exist_ok=True)
    request_json_path = os.path.join(temp_onboard_dir, "onboard_request.json")
    
    with open(request_json_path, "w", encoding="utf-8") as f:
        json.dump(request_data, f, ensure_ascii=False, indent=2)
        
    print(f"\nPreprocessing completed successfully!")
    print(f"Request file generated at: {os.path.abspath(request_json_path)}")
    print(f"You can now ask the Agent to onboard the new form using this request file.")

if __name__ == "__main__":
    main()
