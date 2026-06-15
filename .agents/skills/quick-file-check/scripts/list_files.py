import os
import sys
import urllib.parse

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    input_dir = "data/pdf/PDF"
    print("Tôi đã mở công cụ **Sunouchi IT**.\n")
    print("Dưới đây là danh sách các tệp PDF đầu vào cần xử lý trong thư mục `data/pdf/PDF/`:")
    
    if not os.path.exists(input_dir):
        print("*(Không có tệp PDF nào)*\n")
        print("Vui lòng phản hồi (\"trích xuất\",...) và cho biết bạn muốn xử lý bao nhiêu file để bắt đầu bước tiếp theo.")
        return
        
    files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    if not files:
        print("*(Không có tệp PDF nào)*\n")
        print("Vui lòng phản hồi (\"trích xuất\",...) và cho biết bạn muốn xử lý bao nhiêu file để bắt đầu bước tiếp theo.")
        return
        
    # Sắp xếp các tệp theo thời gian sửa đổi (mtime) giảm dần để tệp mới nhất đứng đầu
    files_with_time = []
    for f in files:
        path = os.path.join(input_dir, f)
        mtime = os.path.getmtime(path)
        files_with_time.append((f, mtime))
        
    files_with_time.sort(key=lambda x: x[1], reverse=True)
    
    # In danh sách tệp với liên kết mã hóa URL
    for f, _ in files_with_time:
        encoded_name = urllib.parse.quote(f)
        link = f"file:///e:/project/.agents/data/pdf/PDF/{encoded_name}"
        print(f"- [{f}]({link})")
        
    print("\nVui lòng phản hồi (\"trích xuất\",...) và cho biết bạn muốn xử lý bao nhiêu file để bắt đầu bước tiếp theo.")

if __name__ == "__main__":
    main()
