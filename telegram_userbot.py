# telegram_userbot.py
import os
import sys
import re
import json
import asyncio
import logging
from PIL import Image

# Reconfigure stdout/stderr to UTF-8 to prevent encoding errors on Windows terminal
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

# Add path to load scripts from .agents/skills/sunouchi-it/scripts/
script_dir = os.path.dirname(os.path.abspath(__file__))
skills_scripts_dir = os.path.join(script_dir, ".agents", "skills", "sunouchi-it", "scripts")
if skills_scripts_dir not in sys.path:
    sys.path.append(skills_scripts_dir)

try:
    import db_helper
    from compress_pdf import compress_pdf
except ImportError:
    print("[-] Không thể import db_helper hoặc compress_pdf. Đang thêm thư mục dự phòng...", flush=True)
    # Fallback to local import path
    sys.path.insert(0, os.path.abspath(os.path.join(".", ".agents", "skills", "sunouchi-it", "scripts")))
    import db_helper
    from compress_pdf import compress_pdf

try:
    from telethon import TelegramClient, events
except ImportError:
    print("[❌] Thư viện Telethon chưa được cài đặt! Vui lòng chạy lệnh: pip install telethon", flush=True)
    sys.exit(1)

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("[❌] Thư viện google-genai chưa được cài đặt! Vui lòng chạy lệnh: pip install google-genai", flush=True)
    sys.exit(1)

try:
    import config
except ImportError:
    print("[❌] Không tìm thấy file config.py trong thư mục gốc!", flush=True)
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("telegram_userbot")

# Verify configurations
is_valid_config = True
if not hasattr(config, 'TELEGRAM_API_ID') or config.TELEGRAM_API_ID == 1234567:
    logger.error("TELEGRAM_API_ID chưa được cấu hình hoặc vẫn là giá trị mặc định.")
    is_valid_config = False
if not hasattr(config, 'TELEGRAM_API_HASH') or config.TELEGRAM_API_HASH == 'your_api_hash':
    logger.error("TELEGRAM_API_HASH chưa được cấu hình hoặc vẫn là giá trị mặc định.")
    is_valid_config = False
if not hasattr(config, 'TELEGRAM_PHONE') or config.TELEGRAM_PHONE == '+84xxxxxxxx':
    logger.error("TELEGRAM_PHONE chưa được cấu hình hoặc vẫn là giá trị mặc định.")
    is_valid_config = False
if not hasattr(config, 'GEMINI_API_KEY') or config.GEMINI_API_KEY == 'your_gemini_api_key':
    logger.error("GEMINI_API_KEY chưa được cấu hình hoặc vẫn là giá trị mặc định.")
    is_valid_config = False

if not is_valid_config:
    print("\n[❌] LỖI: Vui lòng cập nhật đầy đủ thông tin xác thực trong file config.py trước khi chạy!", flush=True)
    sys.exit(1)

# Initialize Gemini Client and Model
ai_client = genai.Client(api_key=config.GEMINI_API_KEY)
gemini_model = getattr(config, 'GEMINI_MODEL', 'gemini-2.5-flash')

# Filename-based Customer Code Mapping (Sync with gemini_client.py)
CUSTOMER_MAPPING_PROMPT = """
CUSTOMER CODE MAPPING (based on filename):
IMPORTANT: When you see a filename that contains any of the customer names below, you MUST set the customer_code to the corresponding code.

- Nếu tên file chứa "アイテック南関東" hoặc "アイテック南関東支店" → customer_code = "102020"
- Nếu tên file chứa "ｵｰｴﾑｺｰﾎﾟﾚｰｼｮﾝ" hoặc "㈲ｵｰｴﾑｺｰﾎﾟﾚｰｼｮﾝ" → customer_code = "140200"
- Nếu tên file chứa "石崎ボルト" → customer_code = "110500"
- Nếu tên file chứa "石崎ボルト長岡" → customer_code = "110510"
- Nếu tên file chứa "大川スティール" → customer_code = "140500"
- Nếu tên file chứa "大津鉄工" → customer_code = "140600"
- Nếu tên file chứa "小野建沖縄" → customer_code = "140830"
- Nếu tên file chứa "カガヤ" → customer_code = "150200"
- Nếu tên file chứa "川田工業" → customer_code = "151300"
- Nếu tên file chứa "岸" → customer_code = "160100"
- Nếu tên file chứa "駒井ハルテック" → customer_code = "190500"
- Nếu tên file chứa "サンコー丸亀" → customer_code = "203010"
- Nếu tên file chứa "大陽日酸ｶﾞｽ大阪" → customer_code = "250100"
- Nếu tên file chứa "大陽日酸ｶﾞｽ業務" → customer_code = "250110"
- Nếu tên file chứa "砂山商事" → customer_code = "220400"
- Nếu tên file chứa "星和小山" → customer_code = "230110"
- Nếu tên file chứa "ＴＯＫＡＩ" → customer_code = "290300"
- Nếu tên file chứa "日鉄物産" → customer_code = "311000"
- Nếu tên file chứa "フルサト" → customer_code = "371500"
- Nếu tên file chứa "ムラタ北関東" → customer_code = "420110"
- Nếu tên file chứa "室賀ファスナー" → customer_code = "420200"
- Nếu tên file chứa "MMK開発" hoặc "MMK開発課" → customer_code = "135410"
- Nếu tên file chứa "MMK東北" → customer_code = "135810"
- Nếu tên file chứa "MMK中部" → customer_code = "135900"
- Nếu tên file chứa "MMK関西" → customer_code = "136100"
- Nếu tên file chứa "MMK関西兵庫" → customer_code = "136101"
- Nếu tên file chứa "MMK関西第一課" → customer_code = "136102"
- Nếu tên file chứa "MMK関西第一課兵庫" → customer_code = "136103"
- Nếu tên file chứa "MMK四国" → customer_code = "136200"
- Nếu tên file chứa "MMK北陸" → customer_code = "136300"
- Nếu tên file chứa "MMK中国" → customer_code = "136400"
- Nếu tên file chứa "MMK九州" → customer_code = "136620"
- Nếu tên file chứa "MMKH札幌" → customer_code = "133001"
- Nếu tên file chứa "MMHK関東" → customer_code = "133100"
- Nếu tên file chứa "MMKH東京" → customer_code = "133200"
- Nếu tên file chứa "MMKH東北" → customer_code = "133000"
- Nếu tên file chứa "MMK1-2" → customer_code = "135210"
- Nếu tên file chứa "MMKH新潟" → customer_code = "133800"
- Nếu tên file chứa "金太" → customer_code = "160500"
- Nếu tên file chứa "JKW大阪" → customer_code = "210500"
- Nếu tên file chứa "MMK新潟" → customer_code = "133800"
- Nếu tên file chứa "MMK札幌帯広" → customer_code = "133002"
- Nếu tên file chứa "MMK旭川" → customer_code = "133003"
- Nếu tên file chứa "原産業" → customer_code = "350200"
- Nếu tên file chứa "アイン" → customer_code = "100500"
- Nếu tên file chứa "星和" → customer_code = "230100"
- Nếu tên file chứa "日鉄物産東北" → customer_code = "311030"
- Nếu tên file chứa "日鉄物産九州" → customer_code = "311040"

CRITICAL RULES:
1. ALWAYS check the filename against the mapping above FIRST.
2. If filename matches ANY customer name, you MUST use that customer_code in the extracted data.
3. The customer_code field MUST be exactly the 6-digit code from the mapping.
4. Do NOT override the customer_code from filename with any other logic.
"""

# Dictionary to hold the user's active processing context (e.g. {user_id: resolved_json_path})
user_contexts = {}

# Make sure standard directories exist
os.makedirs(os.path.join("data", "pdf", "PDF"), exist_ok=True)
os.makedirs(os.path.join("data", "pdf", "json"), exist_ok=True)
os.makedirs(os.path.join("data", "temp_compress"), exist_ok=True)
os.makedirs(os.path.join("data", "pdfToJPG"), exist_ok=True)

# Create Telethon client
# Session is stored in data/ folder to keep root clean
client = TelegramClient(os.path.join("data", "telegram_userbot"), config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH)

def get_page_images(base_name):
    """Retrieve list of Pillow Images rendered by compress_pdf"""
    img_dir = os.path.join("data", "pdfToJPG", base_name)
    images = []
    if os.path.exists(img_dir):
        for img_file in sorted(os.listdir(img_dir)):
            if img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                images.append(Image.open(os.path.join(img_dir, img_file)))
    return images

async def handle_new_message(event):
    user_id = event.sender_id
    message_text = event.message.message.strip().lower() if event.message.message else ""
    
    # 1. Handle user confirmation for ERP Auto-Typer
    if message_text in ['y', 'yes', 'co', 'có']:
        if user_id in user_contexts:
            resolved_path = user_contexts.pop(user_id)
            await event.reply("🚀 **Đang bắt đầu chạy ERP Auto-Typer.**\n\n⚠️ **LƯU Ý QUAN TRỌNG:** Vui lòng **KHÔNG** chạm vào chuột hoặc bàn phím trong quá trình robot làm việc!")
            
            try:
                # Run autoType.py asynchronously to avoid blocking the Telethon event loop
                logger.info(f"Running autoType.py on file: {resolved_path}")
                proc = await asyncio.create_subprocess_exec(
                    sys.executable,
                    os.path.join(skills_scripts_dir, "autoType.py"),
                    "--file", resolved_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await proc.communicate()
                
                if proc.returncode == 0:
                    logger.info("autoType.py completed successfully")
                    await event.reply("🎉 **Hoàn thành nhập liệu ERP thành công!**")
                else:
                    err_msg = stderr.decode('utf-8', errors='ignore')
                    logger.error(f"autoType.py failed: {err_msg}")
                    await event.reply(f"❌ **Gặp lỗi khi chạy ERP Auto-Typer!**\n\nChi tiết:\n```{err_msg[:300]}```")
            except Exception as e:
                logger.error(f"Error executing autoType.py: {e}")
                await event.reply(f"❌ **Lỗi thực thi:** {str(e)}")
        else:
            await event.reply("Hiện tại tôi không có file hóa đơn nào đang chờ bạn xác nhận nhập liệu.")
        return

    # 1.5. Handle product code manual correction from Telegram chat
    p1 = re.search(r'^(?:dòng|dong|line)\s*(\d+)\s*(?::|mã|ma|code|=)?\s*([a-zA-Z0-9]+)$', message_text)
    p2 = re.search(r'^(\d+)\s*(?::|=)\s*([a-zA-Z0-9]{3,})$', message_text)
    match_code = p1 or p2
    
    if match_code:
        if user_id in user_contexts:
            line_num = int(match_code.group(1))
            new_code = match_code.group(2)
            resolved_path = user_contexts[user_id]
            
            try:
                with open(resolved_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                items = data.get("tables", {}).get("items", [])
                if 1 <= line_num <= len(items):
                    items[line_num - 1]["商品コード"] = new_code
                    items[line_num - 1]["found_by_search"] = True
                    
                    with open(resolved_path, 'w', encoding='utf-8') as f_out:
                        json.dump(data, f_out, ensure_ascii=False, indent=2)
                    
                    await event.reply(
                        f"📝 **Đã sửa dòng số {line_num}** thành mã sản phẩm: `{new_code}` thành công!\n\n"
                        f"Bạn có muốn chạy robot **ERP Auto-Typer** ngay bây giờ không?\n"
                        f"👉 Hãy nhắn **`y`** hoặc **`yes`** để bắt đầu."
                    )
                else:
                    await event.reply(f"❌ Dòng số {line_num} không tồn tại trong danh sách sản phẩm (chỉ có {len(items)} dòng).")
            except Exception as e:
                await event.reply(f"❌ Lỗi khi sửa file JSON: {str(e)}")
        else:
            await event.reply("Hiện tại không có file hóa đơn nào đang chờ sửa mã sản phẩm.")
        return

    # 2. Handle PDF file uploads
    if event.message.document:
        filename = None
        for attr in event.message.document.attributes:
            if hasattr(attr, 'file_name'):
                filename = attr.file_name
                break
        
        if filename and filename.lower().endswith('.pdf'):
            logger.info(f"Received PDF file from Saved Messages: {filename}")
            status_msg = await event.reply(f"📥 **Đã nhận file PDF:** `{filename}`\nĐang tải xuống và nén file...")
            
            try:
                # Download file
                input_path = os.path.join("data", "pdf", "PDF", filename)
                await event.download_media(file=input_path)
                
                # Compress PDF & generate images
                base_name = os.path.splitext(filename)[0]
                temp_pdf_path = os.path.join("data", "temp_compress", filename)
                
                # Run compress_pdf synchronously (runs fast, under 1-2s)
                logger.info(f"Compressing PDF: {filename}")
                compress_pdf(input_path, temp_pdf_path, image_dir="data/pdfToJPG")
                
                await status_msg.edit(f"📥 **Nhận file:** `{filename}`\n🔍 Đang phân loại hóa đơn (Classifying)...")
                
                # Retrieve classification prompt from MySQL DB
                classify_prompt = db_helper.get_active_classify_prompt()
                if classify_prompt.startswith("Error"):
                    raise Exception(classify_prompt)
                
                # Get Pillow image objects for Gemini visual input
                images = get_page_images(base_name)
                if not images:
                    raise Exception(f"Không thể xuất ảnh từ file PDF {filename}")
                
                # Build enhanced classification prompt
                enhanced_classify_prompt = f"Filename: {filename}\n\n{CUSTOMER_MAPPING_PROMPT}\n\n{classify_prompt}"
                
                # Call Gemini for layout classification
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: ai_client.models.generate_content(
                        model=gemini_model,
                        contents=images + [enhanced_classify_prompt]
                    )
                )
                
                classify_result = response.text.strip().lower()
                logger.info(f"Classification result: {classify_result}")
                
                match = re.search(r'(invoice\d+)', classify_result)
                if match:
                    invoice_type = match.group(1).lower()
                else:
                    logger.warning(f"Could not parse type from '{classify_result}', defaulting to invoice1")
                    invoice_type = "invoice1"
                
                await status_msg.edit(f"📥 **Nhận file:** `{filename}`\n🏷️ **Loại hóa đơn:** `{invoice_type}`\n🤖 Đang trích xuất dữ liệu (Extracting JSON)...")
                
                # Retrieve schema rules for this invoice type
                schema_info = db_helper.get_active_schema(invoice_type)
                if not schema_info:
                    raise Exception(f"Không tìm thấy cấu trúc (schema) cho '{invoice_type}' trong CSDL.")
                
                shape = schema_info.get("shape")
                rules = schema_info.get("rules")
                
                # Build extraction prompt
                extract_prompt = f"""Filename: {filename}

{CUSTOMER_MAPPING_PROMPT}

You are a professional business assistant specialized in logistics and document processing.
Please analyze the provided commercial document for internal inventory management.

MODE: {invoice_type}

CRITICAL INSTRUCTION:
Based on the filename provided, if it matches any customer in the CUSTOMER CODE MAPPING above, 
you MUST set the customer_code in the header to the corresponding code.

OUTPUT SHAPE (MUST follow exactly):
{shape}

RULES:
{rules}

GUIDELINES:
- Extract accurately.
- Return ONLY valid JSON. Start with {{ and end with }}.
- Use null for missing values.
- IMPORTANT: customer_code MUST be set based on filename mapping if applicable.
"""
                
                # Call Gemini for JSON extraction
                extract_response = await loop.run_in_executor(
                    None,
                    lambda: ai_client.models.generate_content(
                        model=gemini_model,
                        contents=images + [extract_prompt],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json"
                        )
                    )
                )
                
                raw_json_str = extract_response.text.strip()
                logger.info(f"Raw extraction length: {len(raw_json_str)} chars")
                
                # Clean code blocks if returned
                if raw_json_str.startswith("```json"):
                    raw_json_str = raw_json_str[7:]
                elif raw_json_str.startswith("```"):
                    raw_json_str = raw_json_str[3:]
                if raw_json_str.endswith("```"):
                    raw_json_str = raw_json_str[:-3]
                
                raw_json = json.loads(raw_json_str.strip())
                
                # Add extraction mode
                raw_json["_extract_mode"] = invoice_type
                raw_json["_original_filename"] = filename
                
                await status_msg.edit(f"📥 **Nhận file:** `{filename}`\n🏷️ **Loại:** `{invoice_type}`\n⚙️ Đang đối chiếu mã sản phẩm & đối tác với CSDL...")
                
                # Resolve codes using local MySQL database
                resolved_json = await loop.run_in_executor(
                    None,
                    lambda: db_helper.resolve_codes(raw_json)
                )
                
                # Save resolved JSON
                resolved_filename = f"{base_name}.json"
                resolved_path = os.path.join("data", "pdf", "json", resolved_filename)
                with open(resolved_path, 'w', encoding='utf-8') as f_out:
                    json.dump(resolved_json, f_out, ensure_ascii=False, indent=2)
                
                # Store resolved path in user context for confirmation
                user_contexts[user_id] = resolved_path
                
                # Format final message
                warnings = resolved_json.get("mapping_warnings", [])
                warnings_str = ""
                if warnings:
                    warnings_str = "\n\n⚠️ **Cảnh báo đối chiếu DB:**\n" + "\n".join([f"- {w}" for w in warnings])
                
                await status_msg.delete()
                await event.reply(
                    f"✅ **Trích xuất & Đối chiếu CSDL thành công!**\n"
                    f"📄 **File:** `{filename}`\n"
                    f"🏷️ **Loại hóa đơn:** `{invoice_type}`\n"
                    f"💾 **Lưu tại:** `data/pdf/json/{resolved_filename}`{warnings_str}\n\n"
                    f"Bạn có muốn chạy robot **ERP Auto-Typer** để nhập liệu hóa đơn này ngay bây giờ không?\n"
                    f"👉 Hãy nhắn **`y`** hoặc **`yes`** để bắt đầu."
                )
                
            except Exception as e:
                logger.error(f"Error processing document: {e}")
                await event.reply(f"❌ **Lỗi xử lý file {filename}:** {str(e)}")

async def resolve_target_chat_id(client, config_val):
    if not config_val or config_val == 'me':
        me = await client.get_me()
        logger.info(f"Lắng nghe tin nhắn tại: Saved Messages (User ID: {me.id})")
        return me.id
        
    # If numeric ID
    if isinstance(config_val, int) or (isinstance(config_val, str) and config_val.strip().lstrip('-').isdigit()):
        val_id = int(config_val)
        logger.info(f"Lắng nghe tin nhắn tại Chat ID: {val_id}")
        return val_id
        
    # Try finding by title or username in user dialogs
    val_str = str(config_val).strip()
    clean_val = val_str.lstrip('@')
    try:
        async for dialog in client.iter_dialogs():
            if dialog.name and dialog.name.lower() == val_str.lower():
                logger.info(f"Tìm thấy Chat/Channel bằng tên hiển thị: '{dialog.name}' (ID: {dialog.id})")
                return dialog.id
            if dialog.entity and hasattr(dialog.entity, 'username') and dialog.entity.username and dialog.entity.username.lower() == clean_val.lower():
                logger.info(f"Tìm thấy Chat/Channel bằng Username: '@{dialog.entity.username}' (ID: {dialog.id})")
                return dialog.id
    except Exception as e:
        logger.warning(f"Lỗi khi quét danh sách chat: {e}")
        
    # Try resolving username directly
    try:
        entity = await client.get_entity(val_str)
        logger.info(f"Đã resolve username '{val_str}' thành ID: {entity.id}")
        return entity.id
    except Exception as e:
        logger.error(f"Không thể tìm thấy Telegram Chat/Channel với thông tin cấu hình '{val_str}': {e}")
        
    # Fallback to me
    me = await client.get_me()
    logger.info(f"Fallback lắng nghe tại: Saved Messages (User ID: {me.id})")
    return me.id

async def main():
    print("=========================================================", flush=True)
    print("🤖 SUNOUCHI IT TELEGRAM USERBOT (Model B) - STARTING...", flush=True)
    print("=========================================================", flush=True)
    print(f"[*] Đang sử dụng tài khoản đăng ký: {config.TELEGRAM_PHONE}", flush=True)
    
    # Start the client. This will prompt for code in console if not authorized
    await client.start(phone=config.TELEGRAM_PHONE)
    print("[+] Đăng nhập Telegram thành công!", flush=True)
    
    # Resolve target chat/channel
    target_channel_config = getattr(config, 'TELEGRAM_CHANNEL', 'me')
    target_chat_id = await resolve_target_chat_id(client, target_channel_config)
    
    # Register dynamic event handler
    client.add_event_handler(
        handle_new_message,
        events.NewMessage(chats=target_chat_id)
    )
    print(f"[+] Đã đăng ký lắng nghe sự kiện trên ID: {target_chat_id}", flush=True)
    print("[*] Đang lắng nghe các tệp tin hóa đơn...", flush=True)
    
    # Keep running until disconnected
    await client.run_until_disconnected()

if __name__ == "__main__":
    # Set event loop policy for Windows if needed
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
