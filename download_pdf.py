import os
import sys
import json
import urllib.request

def download_telegram_file(token: str, file_id: str, save_path: str):
    # 1. Get file path from Telegram
    get_file_url = f"https://api.telegram.org/bot{token}/getFile?file_id={file_id}"
    req = urllib.request.Request(get_file_url)
    with urllib.request.urlopen(req) as response:
        res_data = json.loads(response.read().decode('utf-8'))
        
    if not res_data.get("ok"):
        raise Exception(f"Failed to get file info from Telegram: {res_data}")
        
    file_path_on_tg = res_data["result"]["file_path"]
    
    # 2. Download the file
    download_url = f"https://api.telegram.org/file/bot{token}/{file_path_on_tg}"
    urllib.request.urlretrieve(download_url, save_path)

def main():
    if len(sys.argv) < 3:
        print("Usage: python download_pdf.py <file_id> <file_name>")
        sys.exit(1)
        
    file_id = sys.argv[1]
    file_name = sys.argv[2]
    
    # Bot Token
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "8937260691:AAGfDHtCgTwowkpX43aj5F0r0Ugpi0Gvdkc")
    
    project_dir = os.path.dirname(os.path.abspath(__file__))
    save_dir = os.path.join(project_dir, "data", "pdf", "PDF")
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, file_name)
    
    try:
        download_telegram_file(token, file_id, save_path)
        print(f"Success: Saved to {save_path}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
