# .agents/skills/sunouchi-it/scripts/compress_pdf.py
import os
import sys
import argparse
import fitz

def compress_pdf(input_path, output_path, dpi=120, quality=70, image_dir="data/pdfToJPG"):
    """
    Nén file PDF bằng cách render từng trang thành ảnh JPEG chất lượng trung bình,
    sau đó ghép lại thành file PDF mới nhẹ hơn nhiều giúp Agent xử lý nhanh hơn.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} does not exist", file=sys.stderr)
        sys.exit(1)
        
    try:
        doc = fitz.open(input_path)
        new_doc = fitz.open() # Tạo PDF trống mới
        
        for i, page in enumerate(doc):
            # Render trang thành pixmap với DPI thấp (mặc định 120 DPI đủ đọc rõ chữ)
            pix = page.get_pixmap(dpi=dpi)
            
            # Chuyển đổi sang JPEG bytes với độ nén thích hợp
            img_data = pix.tobytes("jpeg", quality)
            
            # Lưu ảnh tương ứng vào thư mục image_dir nếu được chỉ định
            if image_dir:
                base_name = os.path.splitext(os.path.basename(input_path))[0]
                pdf_image_dir = os.path.join(image_dir, base_name)
                os.makedirs(pdf_image_dir, exist_ok=True)
                image_name = f"page_{i + 1}.jpg"
                image_path = os.path.join(pdf_image_dir, image_name)
                with open(image_path, "wb") as f_img:
                    f_img.write(img_data)
                print(f"Saved page image to {image_path}")
            
            # Tạo trang mới trong new_doc có kích thước giống trang gốc
            new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
            
            # Chèn ảnh vào trang mới
            new_page.insert_image(new_page.rect, stream=img_data)
            
        # Lưu file PDF đã nén
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        new_doc.save(output_path, garbage=3, deflate=True)
        new_doc.close()
        doc.close()
        print(f"Success: Compressed PDF saved to {output_path}")
        
    except Exception as e:
        print(f"Error compressing PDF: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compress PDF for faster Agent processing")
    parser.add_argument("--input", required=True, help="Path to input PDF file")
    parser.add_argument("--output", required=True, help="Path to save compressed PDF file")
    parser.add_argument("--dpi", type=int, default=120, help="DPI for page rendering (default: 120)")
    parser.add_argument("--quality", type=int, default=70, help="JPEG compression quality 1-100 (default: 70)")
    parser.add_argument("--image_dir", default="data/pdfToJPG", help="Path to save page images")
    
    args = parser.parse_args()
    compress_pdf(args.input, args.output, args.dpi, args.quality, args.image_dir)
