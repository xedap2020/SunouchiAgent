"""
Bot Telegram gọi Antigravity CLI (agy)
-----------------------------------------
Cách hoạt động:
  Telegram message -> bot nhận -> chạy "agy -p <prompt> -c --add-dir <workspace>"
  -> lấy stdout -> gửi lại Telegram

Cài thư viện:
    pip install python-telegram-bot --upgrade

Trước khi chạy:
  1. Cài Antigravity CLI và đăng nhập 1 lần thủ công (agy) để lưu credentials.
  2. Sửa các biến cấu hình bên dưới (BOT_TOKEN, ALLOWED_CHAT_IDS, AGY_PATH, WORKSPACE_DIR).
  3. Chạy: python telegram_antigravity_bot.py
"""

import asyncio
import logging
import os
import re
import subprocess
from pathlib import Path

from telegram import Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import Application, ContextTypes, MessageHandler, CommandHandler, filters

# ===================== CẤU HÌNH =====================

# Token lấy từ @BotFather trên Telegram
BOT_TOKEN = "8846703591:AAEBAZzNy1jDvulTVHPUwRX3_MFGe_Y8VNI"

# Danh sách chat_id được phép dùng bot (lấy từ @userinfobot hoặc khi bot báo ID bị từ chối)
# Nhập ID của bạn để tránh người lạ điều khiển máy bạn qua bot
# Ví dụ: {123456789}
ALLOWED_CHAT_IDS = {1800676162}

# Đường dẫn tới agy.exe (Windows). Mặc định nó nằm ở đây sau khi cài:
AGY_PATH = r"C:\Users\admin-KH\AppData\Local\agy\bin\agy.exe"

# Thư mục project SunouchiAgent (chứa .agents/skills/, db_helper.py, autoType.py...)
WORKSPACE_DIR = r"e:\SunouchiAgent"

# Timeout cho mỗi lệnh (giây). Lệnh phức tạp có thể cần lâu hơn.
COMMAND_TIMEOUT = 600

# Có cho phép agent tự động chấp nhận mọi hành động (đọc/sửa file, chạy lệnh) không?
# True = tiện nhưng rủi ro hơn (agent có thể sửa/xóa file mà không hỏi lại bạn)
# False = an toàn hơn nhưng nếu agent cần "Proceed?" mà không ai bấm, lệnh -p sẽ treo/timeout
AUTO_APPROVE = True

# ⚠️ CẢNH BÁO RIÊNG CHO SKILL autoType.py (PyAutoGUI):
# Skill này điều khiển CHUỘT/BÀN PHÍM THẬT trên máy đang chạy bot.
# Nếu AUTO_APPROVE=True, agent có thể tự gõ vào ERP qua Telegram mà không ai
# đứng cạnh màn hình xác nhận đang gõ đúng ô, đúng form. Rủi ro: gõ nhầm vào
# cửa sổ khác đang active, hỏng dữ liệu ERP.
# Khuyến nghị chỉ bật AUTO_APPROVE=True khi đang ở gần máy theo dõi
# màn hình lúc gửi lệnh ERP qua Telegram. Việc đọc PDF / trích xuất / ghi DB
# (không đụng chuột bàn phím) thì an toàn để chạy ngầm bình thường.

# Giới hạn độ dài tin nhắn Telegram (Telegram giới hạn ~4096 ký tự/tin)
TELEGRAM_MAX_LEN = 3500

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ===================== HÀM GỌI AGY =====================

def run_agy(prompt: str, continue_session: bool = True) -> str:
    """
    Chạy Antigravity CLI ở chế độ non-interactive (-p) và trả về output.
    Chạy trong subprocess.run đồng bộ được gọi qua asyncio.to_thread để không block bot.
    """
    cmd = [AGY_PATH, "-p", prompt, "--add-dir", WORKSPACE_DIR]

    if continue_session:
        cmd.append("-c")  # tiếp tục hội thoại gần nhất, để agent có ngữ cảnh

    if AUTO_APPROVE:
        cmd.append("--dangerously-skip-permissions")

    logger.info("Chạy lệnh: %s", " ".join(cmd))

    # Chuẩn bị môi trường sạch, loại bỏ các biến ANTIGRAVITY_ để tránh cơ chế chống đệ quy (anti-recursion)
    env = os.environ.copy()
    for k in list(env.keys()):
        if k.startswith("ANTIGRAVITY_"):
            env.pop(k)
    
    # Thiết lập các biến HOME để agy định vị đúng thư mục cấu hình và transcript trên ổ C:
    home_dir = os.path.expanduser("~")
    env["HOME"] = home_dir
    env["HOMEPATH"] = home_dir
    env["HOMEDRIVE"] = "C:"

    try:
        result = subprocess.run(
            cmd,
            cwd=WORKSPACE_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=COMMAND_TIMEOUT,
            env=env,
            stdin=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        return f"❌ Không tìm thấy agy tại: {AGY_PATH}\nKiểm tra lại đường dẫn AGY_PATH."
    except subprocess.TimeoutExpired:
        return f"⏱️ Lệnh chạy quá {COMMAND_TIMEOUT}s và bị hủy. Thử chia nhỏ yêu cầu."

    output = result.stdout.strip()
    err = result.stderr.strip()

    if result.returncode != 0:
        return f"❌ Lỗi (mã {result.returncode}):\n{err or output}"

    # Nếu stdout trống, thử đọc câu trả lời từ file transcript.jsonl mới nhất của agy
    if not output:
        try:
            import json
            brain_dir = Path(home_dir) / ".gemini" / "antigravity-cli" / "brain"
            if brain_dir.exists():
                folders = [d for d in brain_dir.iterdir() if d.is_dir()]
                if folders:
                    latest_folder = max(folders, key=lambda d: d.stat().st_mtime)
                    transcript_path = latest_folder / ".system_generated" / "logs" / "transcript.jsonl"
                    if transcript_path.exists():
                        last_response = None
                        with open(transcript_path, "r", encoding="utf-8") as f:
                            for line in f:
                                data = json.loads(line.strip())
                                if data.get("source") == "MODEL" and "content" in data:
                                    last_response = data["content"]
                        if last_response:
                            logger.info("Lấy phản hồi thành công từ transcript.jsonl")
                            return last_response.strip()
        except Exception as e:
            logger.error(f"Lỗi khi đọc transcript fallback: {e}")

    return output or "(Không có output trả về)"


def split_message(text: str, limit: int = TELEGRAM_MAX_LEN):
    """Chia tin nhắn dài thành nhiều phần để gửi qua Telegram."""
    if len(text) <= limit:
        return [text]
    parts = []
    while text:
        parts.append(text[:limit])
        text = text[limit:]
    return parts


# ===================== HANDLERS TELEGRAM =====================

def is_allowed(update: Update) -> bool:
    chat_id = update.effective_chat.id
    if chat_id not in ALLOWED_CHAT_IDS:
        logger.warning(f"❌ [BẢO MẬT] Từ chối truy cập từ Chat ID: {chat_id}")
        return False
    return True


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not is_allowed(update):
        await update.message.reply_text(
            f"❌ Bạn không có quyền dùng bot này.\n"
            f"Chat ID của bạn là: `{chat_id}`\n"
            f"Hãy copy ID này và thêm vào danh sách ALLOWED_CHAT_IDS trong file code bot để sử dụng."
        )
        return
    await update.message.reply_text(
        "🤖 Bot điều khiển Antigravity CLI đã sẵn sàng.\n\n"
        "Gửi tin nhắn bất kỳ = prompt gửi thẳng cho agent.\n"
        "/new - Bắt đầu hội thoại mới (không tiếp tục session cũ)\n"
        "/status - Kiểm tra agy có hoạt động không"
    )


async def new_session_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        return
    context.chat_data["fresh"] = True
    await update.message.reply_text("🆕 Sẽ bắt đầu hội thoại mới cho lần nhắn tiếp theo.")


async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        return
    if not Path(AGY_PATH).exists():
        await update.message.reply_text(f"❌ Không thấy agy tại {AGY_PATH}")
        return
    await update.message.reply_text("✅ Tìm thấy agy. Workspace: " + WORKSPACE_DIR)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        chat_id = update.effective_chat.id
        await update.message.reply_text(
            f"❌ Bạn không có quyền dùng bot này.\n"
            f"Chat ID của bạn là: `{chat_id}`\n"
            f"Hãy copy ID này và thêm vào danh sách ALLOWED_CHAT_IDS trong file code bot để sử dụng."
        )
        return

    prompt = update.message.text
    if not prompt:
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    status_msg = await update.message.reply_text("⏳ Đang gửi cho Antigravity, chờ chút...")

    continue_session = not context.chat_data.pop("fresh", False)

    # Chạy lệnh blocking trong thread riêng để không treo event loop của bot
    output = await asyncio.to_thread(run_agy, prompt, continue_session)

    # Loại bỏ phần Summary of work ở cuối tin nhắn nếu có
    summary_pattern = re.compile(
        r'(?i)(?:\*\*Summary\s+of\s+work:\*\*|Summary\s+of\s+work:|\*\*Tóm\s+tắt\s+công\s+việc:\*\*|Tóm\s+tắt\s+công\s+việc:).*$',
        re.DOTALL
    )
    output = summary_pattern.sub('', output).strip()
    
    # Thay thế câu hỏi ERP Auto-Typer dài dòng thành câu ngắn gọn
    erp_prompt_pattern = re.compile(
        r'(?i)Bạn\s+có\s+muốn\s+chạy\s+công\s+cụ\s+(?:\*\*)*ERP\s+Auto-Typer(?:\*\*)*\s+để\s+tự\s+động\s+nhập\s+dữ\s+liệu\s+từ\s+các\s+tệp\s+JSON\s+này\s+vào\s+ứng\s+dụng\s+ERP\s+không\??'
    )
    output = erp_prompt_pattern.sub("Bạn có muốn tự động nhập vào APP không?", output)
    
    # Thay thế các link file:// nội bộ không bấm được thành tên file in đậm để hiển thị gọn đẹp
    file_link_pattern = re.compile(r'\[([^\]]+)\]\(file://[^\)]+\)')
    output = file_link_pattern.sub(r'**\1**', output)

    if not output:
        output = "(Xử lý hoàn tất)"

    try:
        await status_msg.delete()
    except Exception:
        pass

    for chunk in split_message(output):
        try:
            await update.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger.warning(f"Không thể gửi tin nhắn dạng Markdown (Lỗi: {e}), đang gửi dưới dạng text thường...")
            await update.message.reply_text(chunk)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        chat_id = update.effective_chat.id
        await update.message.reply_text(
            f"❌ Bạn không có quyền dùng bot này.\n"
            f"Chat ID của bạn là: `{chat_id}`\n"
            f"Hãy copy ID này và thêm vào danh sách ALLOWED_CHAT_IDS trong file code bot để sử dụng."
        )
        return

    document = update.message.document
    if not document:
        return

    file_name = document.file_name
    if not file_name or not file_name.lower().endswith('.pdf'):
        await update.message.reply_text("❌ Vui lòng chỉ gửi tệp tin định dạng PDF.")
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    status_msg = await update.message.reply_text(f"⏳ Đang tải tệp `{file_name}`...")

    try:
        # Đường dẫn lưu file
        target_dir = Path(WORKSPACE_DIR) / "data" / "pdf" / "PDF"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / file_name

        # Tải file từ Telegram server
        tg_file = await context.bot.get_file(document.file_id)
        await tg_file.download_to_drive(custom_path=target_path)

        await status_msg.edit_text(
            f"✅ Đã tải và lưu thành công file **{file_name}** vào thư mục xử lý.\n\n"
            f"Bạn có muốn tôi tiến hành phân loại và trích xuất dữ liệu của file này không?",
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Lỗi khi tải file: {e}")
        try:
            await status_msg.edit_text(f"❌ Có lỗi xảy ra khi lưu file: {e}")
        except Exception:
            await update.message.reply_text(f"❌ Có lỗi xảy ra khi lưu file: {e}")


# ===================== MAIN =====================

def main():
    if "DÁN_BOT_TOKEN" in BOT_TOKEN or not BOT_TOKEN:
        raise SystemExit("⚠️ Bạn chưa điền BOT_TOKEN. Mở file và sửa biến BOT_TOKEN trước.")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("new", new_session_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    logger.info("Bot đang chạy...")
    app.run_polling()


if __name__ == "__main__":
    main()
