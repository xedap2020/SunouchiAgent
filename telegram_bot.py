"""
Bot Telegram kết nối Antigravity CLI (agy)
------------------------------------------
Luồng hoạt động:
    Telegram message → bot nhận → chạy "agy --print <prompt>" → đọc kết quả → gửi lại Telegram

Cài đặt:
    pip install python-telegram-bot --upgrade

Trước khi chạy:
    1. Cài Antigravity CLI, đăng nhập thủ công 1 lần để lưu credentials.
    2. Điền BOT_TOKEN bên dưới (lấy từ @BotFather).
    3. Chạy: python telegram_antigravity_bot.py
"""

import asyncio
import json
import logging
import os
import re
import subprocess
import sys
from pathlib import Path

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# ===================== LOGGING =====================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ===================== CẤU HÌNH =====================

# Token lấy từ @BotFather
BOT_TOKEN = "8946248688:AAF7BbcUOQ9lC6xoxXSrcBBZwezb_OfWlpw"

# Đường dẫn tới agy CLI (đã có trong PATH nên dùng tên trực tiếp)
AGY_PATH = "agy"

# Thư mục chứa file bot này (dùng làm --add-dir cho agy)
PROJECT_DIR = Path(__file__).parent.resolve()

# File lưu danh sách chat_id để broadcast thông báo bật/tắt
ADMIN_CHATS_FILE = PROJECT_DIR / "data" / "admin_chats.json"

# Lưu conversation_id theo từng user: { telegram_user_id: "uuid-..." }
USER_CONVERSATIONS: dict[int, str | None] = {}


# ===================== MARKDOWN → HTML =====================

# Compile regex một lần duy nhất khi load module (hiệu suất tốt hơn)
_MD_PATTERNS = [
    # Bold: **text** → <b>text</b>  (xử lý trước italic)
    (re.compile(r"\*\*(.*?)\*\*", re.DOTALL), r"<b>\1</b>"),
    # Italic: *text* hoặc _text_ → <i>text</i>
    (re.compile(r"\*(.*?)\*",     re.DOTALL), r"<i>\1</i>"),
    (re.compile(r"_(.*?)_",       re.DOTALL), r"<i>\1</i>"),
    # Heading: # / ## / ### → <b>text</b>
    (re.compile(r"^#{1,6}\s+(.*)", re.MULTILINE), r"<b>\1</b>"),
    # Bullet list: * hoặc - → • (giữ nguyên indent)
    (re.compile(r"^(\s*)[*\-]\s+(.*)", re.MULTILINE), r"\1• \2"),
    # Inline code: `code` → <code>code</code>
    (re.compile(r"`(.+?)`"), r"<code>\1</code>"),
    # Link: [text](url) → <a href="url">text</a>
    (re.compile(r"\[([^\]]+)\]\(([^)]+)\)"), r'<a href="\2">\1</a>'),
]

_SEPARATOR_RE = re.compile(r"^[\s\-\:]+$")


def _clean_table_row(row_str: str) -> list[str]:
    """Tách một dòng bảng Markdown thành danh sách cell đã strip."""
    parts = row_str.split("|")
    if parts and parts[0].strip() == "":
        parts = parts[1:]
    if parts and parts[-1].strip() == "":
        parts = parts[:-1]
    return [p.strip() for p in parts]


def _parse_and_format_table(table_lines: list[str]) -> str:
    """Chuyển bảng Markdown thành danh sách bullet có thể hiển thị trên Telegram."""
    headers = _clean_table_row(table_lines[0])

    # Bỏ qua dòng separator (---) nếu có
    start_row = 1
    if len(table_lines) > 1:
        second_row = _clean_table_row(table_lines[1])
        if all(_SEPARATOR_RE.match(cell) for cell in second_row):
            start_row = 2

    rows = [
        _clean_table_row(table_lines[i])
        for i in range(start_row, len(table_lines))
        if _clean_table_row(table_lines[i])
    ]

    if not rows:
        return ""

    formatted = []
    for row in rows:
        row += [""] * (len(headers) - len(row))  # đảm bảo đủ số cột

        line = f"• **{row[0]}**"
        details = [
            f"**{headers[i] if i < len(headers) else f'Col {i+1}'}**: {row[i]}"
            for i in range(1, len(row))
            if row[i]
        ]
        if details:
            line += "\n  - " + "\n  - ".join(details)
        formatted.append(line)

    return "\n".join(formatted)


def _format_markdown_tables(text: str) -> str:
    """Tìm và thay thế tất cả bảng Markdown trong text bằng dạng bullet list."""
    lines = text.split("\n")
    output: list[str] = []
    table_lines: list[str] = []
    in_table = False

    for line in lines:
        is_table_row = line.strip().startswith("|") and line.count("|") >= 2
        if is_table_row:
            if not in_table:
                in_table = True
                table_lines = []
            table_lines.append(line)
        else:
            if in_table:
                output.append(_parse_and_format_table(table_lines))
                in_table = False
                table_lines = []
            output.append(line)

    if in_table:
        output.append(_parse_and_format_table(table_lines))

    return "\n".join(output)


def md_to_html(text: str) -> str:
    """
    Chuyển đổi Markdown sang HTML tương thích với Telegram (parse_mode='HTML').

    Thứ tự xử lý:
        1. Bảng Markdown  → bullet list có cấu trúc
        2. Escape HTML    → tránh inject tag lạ
        3. Bold / Italic / Heading / List / Code / Link
        4. Dọn tag bold bị lồng nhau
    """
    text = _format_markdown_tables(text)

    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    for pattern, replacement in _MD_PATTERNS:
        text = pattern.sub(replacement, text)

    # Dọn <b><b> phát sinh khi heading + bold cùng xuất hiện
    text = text.replace("<b><b>", "<b>").replace("</b></b>", "</b>")

    return text


# ===================== QUẢN LÝ CHAT ID =====================

def _load_chat_ids() -> list[int]:
    if not ADMIN_CHATS_FILE.exists():
        return []
    with open(ADMIN_CHATS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_chat_ids(chats: list[int]) -> None:
    ADMIN_CHATS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(ADMIN_CHATS_FILE, "w", encoding="utf-8") as f:
        json.dump(chats, f, indent=4)


def register_chat_id(chat_id: int) -> None:
    """Lưu chat_id vào file nếu chưa có, để dùng cho broadcast."""
    try:
        chats = _load_chat_ids()
        if chat_id not in chats:
            chats.append(chat_id)
            _save_chat_ids(chats)
    except Exception as e:
        logger.error("Lỗi khi lưu chat_id %s: %s", chat_id, e)


async def send_broadcast(application, text: str) -> None:
    """Gửi tin nhắn đến tất cả chat_id đã đăng ký."""
    try:
        chats = _load_chat_ids()
    except Exception as e:
        logger.error("Lỗi khi đọc danh sách chat: %s", e)
        return

    for chat_id in chats:
        try:
            await application.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
        except Exception as e:
            logger.error("Lỗi gửi tin đến %s: %s", chat_id, e)


# ===================== LIFECYCLE HOOKS =====================

async def post_init(application) -> None:
    logger.info("Bot khởi động.")
    await send_broadcast(application, "🟢 <b>Bot Antigravity đã BẬT và đang hoạt động!</b>")


async def post_stop(application) -> None:
    logger.info("Bot dừng.")
    await send_broadcast(application, "🔴 <b>Bot Antigravity đã DỪNG hoạt động!</b>")


# ===================== HELPERS AGY =====================

def _build_clean_env() -> dict:
    """Trả về môi trường sạch, loại bỏ các biến có thể gây xung đột với agy."""
    env = os.environ.copy()
    env.pop("ANTIGRAVITY_AGENT", None)
    for key in [k for k in env if k.startswith("VSCODE_")]:
        del env[key]

    home_dir = os.path.expanduser("~")
    env["HOME"] = home_dir
    env["USERPROFILE"] = home_dir
    return env


def _get_brain_dirs(brain_dir: Path) -> set[str]:
    """Lấy tập hợp tên thư mục trong brain_dir (để phát hiện conversation mới)."""
    if not brain_dir.exists():
        return set()
    return {d.name for d in brain_dir.iterdir() if d.is_dir()}


def _read_transcript(transcript_path: Path) -> str:
    """
    Đọc transcript.jsonl và trả về câu trả lời cuối cùng của MODEL.
    Ưu tiên type PLANNER_RESPONSE hoặc MODIFIED_RESPONSE, bỏ qua tool_calls.
    """
    reply = ""
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                if (
                    data.get("source") == "MODEL"
                    and data.get("type") in ("PLANNER_RESPONSE", "MODIFIED_RESPONSE")
                    and "content" in data
                    and not data.get("tool_calls")
                ):
                    content = data["content"].strip()
                    if content:
                        reply = content
    except Exception as e:
        logger.error("Lỗi đọc transcript: %s", e)
    return reply


async def _run_agy(
    user_message: str,
    conv_id: str | None,
    env: dict,
) -> tuple[str, str | None]:
    """
    Gọi agy CLI và trả về (reply_text, new_conv_id).
    new_conv_id là None nếu không phát hiện conversation mới.
    """
    home_dir = Path(env["HOME"])
    brain_dir = home_dir / ".gemini" / "antigravity-cli" / "brain"

    existing_dirs = _get_brain_dirs(brain_dir)

    cmd = [
        AGY_PATH,
        "--dangerously-skip-permissions",
        "--print", user_message,
        "--add-dir", str(PROJECT_DIR),
    ]
    if conv_id:
        cmd += ["--conversation", conv_id]

    creation_flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0

    result = await asyncio.to_thread(
        subprocess.run,
        cmd,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
        env=env,
        cwd=str(home_dir),
        creationflags=creation_flags,
    )

    # Phát hiện conversation ID mới nếu agy tạo session mới
    new_conv_id = conv_id
    new_dirs = _get_brain_dirs(brain_dir) - existing_dirs
    if new_dirs:
        new_conv_id = new_dirs.pop()
        logger.info("Phát hiện conversation mới từ agy: %s", new_conv_id)

    # Đọc kết quả: transcript (ưu tiên) → stdout → stderr
    reply = ""
    if new_conv_id:
        transcript_path = (
            brain_dir / new_conv_id / ".system_generated" / "logs" / "transcript.jsonl"
        )
        if transcript_path.exists():
            reply = _read_transcript(transcript_path)

    if not reply:
        reply = result.stdout.strip()
    if not reply:
        stderr = result.stderr.strip()
        reply = f"❌ Lỗi từ CLI:\n{stderr}" if stderr else "⚠️ Antigravity CLI không phản hồi."

    return reply, new_conv_id


# ===================== HANDLERS TELEGRAM =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lệnh /start — chào mừng và tạo session mới."""
    user_id = update.effective_user.id
    register_chat_id(update.effective_chat.id)
    USER_CONVERSATIONS[user_id] = None

    await update.message.reply_text(
        "👋 Chào mừng bạn đến với Antigravity AI Bot!\n\n"
        "Tôi đã khởi tạo một cuộc trò chuyện mới cho bạn.\n"
        "Hãy gửi tin nhắn bất kỳ để bắt đầu!"
    )


async def new_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lệnh /new — reset session, bắt đầu hội thoại mới."""
    user_id = update.effective_user.id
    register_chat_id(update.effective_chat.id)
    USER_CONVERSATIONS[user_id] = None
    await update.message.reply_text("🔄 Đã làm mới cuộc trò chuyện. Hãy gửi tin nhắn tiếp theo!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Xử lý tin nhắn thường — gọi agy và gửi kết quả về Telegram."""
    user_id = update.effective_user.id
    register_chat_id(update.effective_chat.id)
    user_message = update.message.text
    if not user_message:
        return

    # Gửi placeholder ngay để user biết bot đang xử lý
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    status_message = await update.message.reply_text(
        "⚡ <i>Antigravity đang suy nghĩ...</i>", parse_mode="HTML"
    )

    # Giữ hiệu ứng "đang gõ..." mỗi 4 giây (Telegram tự tắt sau 5 giây)
    async def typing_loop(chat_id: int) -> None:
        try:
            while True:
                await asyncio.sleep(4)
                await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error("Lỗi typing loop: %s", e)

    typing_task = asyncio.create_task(typing_loop(update.effective_chat.id))

    conv_id = USER_CONVERSATIONS.get(user_id)
    logger.info("User %s gửi tin (conversation: %s)", user_id, conv_id)

    try:
        reply, new_conv_id = await _run_agy(user_message, conv_id, _build_clean_env())

        if new_conv_id != conv_id:
            USER_CONVERSATIONS[user_id] = new_conv_id

        html_reply = md_to_html(reply)

        try:
            await status_message.edit_text(html_reply, parse_mode="HTML")
        except Exception as e:
            logger.warning("Không parse được HTML (%s), dùng plain text.", e)
            try:
                await status_message.edit_text(reply)
            except Exception:
                await update.message.reply_text(reply)

    except Exception as e:
        logger.error("Lỗi khi chạy agy: %s", e)
        error_text = f"❌ Không thể thực thi lệnh CLI: {e}"
        try:
            await status_message.edit_text(error_text)
        except Exception:
            await update.message.reply_text(error_text)

    finally:
        typing_task.cancel()


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Nhận file PDF từ Telegram và lưu vào thư mục xử lý."""
    register_chat_id(update.effective_chat.id)

    document = update.message.document
    if not document or not document.file_name.lower().endswith(".pdf"):
        await update.message.reply_text("❌ Chỉ hỗ trợ file PDF.")
        return

    file_name = document.file_name
    status_message = await update.message.reply_text(
        f"⏳ <i>Đang tải <b>{file_name}</b>...</i>", parse_mode="HTML"
    )

    try:
        save_dir = PROJECT_DIR / "data" / "pdf"
        save_dir.mkdir(parents=True, exist_ok=True)
        save_path = save_dir / file_name

        tg_file = await context.bot.get_file(document.file_id)
        await tg_file.download_to_drive(custom_path=save_path)

        await status_message.edit_text(
            f"✅ Đã lưu <b>{file_name}</b> vào thư mục xử lý.",
            parse_mode="HTML"
        )
        logger.info("Đã lưu PDF: %s", save_path)

    except Exception as e:
        logger.error("Lỗi khi lưu PDF: %s", e)
        await status_message.edit_text(f"❌ Lỗi khi lưu file: {e}")


# ===================== MAIN =====================

def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if not BOT_TOKEN or BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        sys.exit("[!] Vui lòng điền BOT_TOKEN trước khi chạy.")

    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .post_stop(post_stop)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("new", new_chat))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_document))

    print("🤖 Telegram Bot đang chạy. Nhấn Ctrl+C để dừng.")
    app.run_polling()


if __name__ == "__main__":
    main()