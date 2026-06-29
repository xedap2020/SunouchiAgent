import os
import sys
import json
import subprocess
import re
from pathlib import Path

def _build_clean_env() -> dict:
    env = os.environ.copy()
    env.pop("ANTIGRAVITY_AGENT", None)
    for key in [k for k in env if k.startswith("VSCODE_")]:
        del env[key]
    home_dir = os.path.expanduser("~")
    env["HOME"] = home_dir
    env["USERPROFILE"] = home_dir
    return env

def _get_brain_dirs(brain_dir: Path) -> set[str]:
    if not brain_dir.exists():
        return set()
    return {d.name for d in brain_dir.iterdir() if d.is_dir()}

def _read_transcript(transcript_path: Path) -> str:
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
    except Exception:
        pass
    return reply

def _clean_table_row(row_str: str) -> list[str]:
    # Replace escaped pipe characters first to prevent wrong column splitting
    row_str = row_str.replace(r'\|', ' / ').replace('\\|', ' / ')
    parts = row_str.split('|')
    if parts and parts[0].strip() == '':
        parts = parts[1:]
    if parts and parts[-1].strip() == '':
        parts = parts[:-1]
    return [p.strip() for p in parts]

def _parse_and_format_table(table_lines: list[str]) -> str:
    headers = _clean_table_row(table_lines[0])
    start_row = 1
    if len(table_lines) > 1:
        second_row = _clean_table_row(table_lines[1])
        if all(re.match(r'^[\s\-\:|]+$', cell) for cell in second_row):
            start_row = 2
            
    rows = [
        _clean_table_row(table_lines[i])
        for i in range(start_row, len(table_lines))
        if _clean_table_row(table_lines[i])
    ]
    if not rows:
        return ''
        
    formatted = []
    for row in rows:
        row += [''] * (len(headers) - len(row))
        # Use simple markers, bolding will be stripped later in plain text mode
        line = f'• **{row[0]}**'
        details = [
            f'  - **{headers[i] if i < len(headers) else f"Col {i+1}"}**: {row[i]}'
            for i in range(1, len(row))
            if row[i]
        ]
        if details:
            line += '\n' + '\n'.join(details)
        formatted.append(line)
    return '\n'.join(formatted)

def _format_markdown_tables(text: str) -> str:
    lines = text.split('\n')
    output = []
    table_lines = []
    in_table = False
    for line in lines:
        is_table_row = line.strip().startswith('|') and line.count('|') >= 2
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
    return '\n'.join(output)

def _clean_reply_for_telegram(reply: str) -> str:
    # First, format markdown tables to structured text lists
    reply = _format_markdown_tables(reply)
    
    # 1. Remove instructions/notes lines
    lines = reply.split("\n")
    cleaned_lines = []
    for line in lines:
        if (
            "(* LƯU Ý:" in line
            or "thay thế <đường_dẫn" in line
            or "thay thế E:/SunouchiAgent" in line
        ):
            continue
        cleaned_lines.append(line)
    
    text = "\n".join(cleaned_lines)
    
    # 2. Strip Markdown headers (e.g. ### Heading -> Heading)
    text = re.sub(r'^(?:#{1,6})\s*(.*)', r'\1', text, flags=re.MULTILINE)
    
    # 3. Convert markdown links [text](url) to just text
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    
    # 4. Strip bold and italic characters
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'(?<!\w)__(?!\s)(.+?)(?<!\s)__(?!\w)', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'(?<!\w)_(?!\s)(.+?)(?<!\s)_(?!\w)', r'\1', text)
    
    # 5. Strip inline code (`code` -> code)
    text = re.sub(r'(?<!\`)`([^`\n]+?)`(?!\`)', r'\1', text)
    
    # 6. Normalize lists (* or - to •)
    text = re.sub(r'^(\s*)[*\-]\s+(.*)', r'\1• \2', text, flags=re.MULTILINE)
    
    # Normalize multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # HTML escape for Telegram (parse_mode: HTML compatibility)
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return text.strip()

def _handle_local_commands(prompt: str, project_dir: Path) -> str | None:
    cleaned = prompt.strip().lower()
    
    # 1. Handle listing files
    is_list_pdf = cleaned in ("/list pdf", "list pdf", "/lists pdf", "lists pdf", "/pdfs", "pdfs", "/pdf", "pdf")
    is_list_json = cleaned in ("/list json", "list json", "/lists json", "lists json", "/jsons", "jsons", "/json", "json")
    is_list_all = cleaned in ("/list", "list", "/lists", "lists", "/files", "files")
    
    if is_list_pdf or is_list_json or is_list_all:
        pdf_dir = project_dir / "data" / "pdf" / "PDF"
        json_dir = project_dir / "data" / "pdf" / "json"
        
        pdf_lines = []
        if is_list_pdf or is_list_all:
            if pdf_dir.exists():
                # List PDF files sorted by modification time (newest first)
                pdf_files = []
                for f in pdf_dir.iterdir():
                    if f.is_file() and f.suffix.lower() == ".pdf":
                        pdf_files.append((f.name, f.stat().st_mtime))
                pdf_files.sort(key=lambda x: x[1], reverse=True)
                
                if pdf_files:
                    pdf_lines.append("📁 Danh sách các file PDF hiện có (mới nhất xếp đầu):")
                    for name, _ in pdf_files:
                        pdf_lines.append(f"• {name}")
                else:
                    pdf_lines.append("📁 Không có file PDF nào trong thư mục data/pdf/PDF/.")
            else:
                pdf_lines.append("❌ Thư mục data/pdf/PDF không tồn tại.")
                
        json_lines = []
        if is_list_json or is_list_all:
            if json_dir.exists():
                # List JSON files sorted alphabetically
                json_files = [f.name for f in json_dir.iterdir() if f.is_file() and f.suffix.lower() == ".json"]
                if json_files:
                    json_lines.append("📁 Danh sách các file JSON hiện có:")
                    for name in sorted(json_files):
                        json_lines.append(f"• {name}")
                else:
                    json_lines.append("📁 Không có file JSON nào trong thư mục data/pdf/json/.")
            else:
                json_lines.append("❌ Thư mục data/pdf/json không tồn tại.")
                
        if is_list_pdf:
            return "\n".join(pdf_lines)
        elif is_list_json:
            return "\n".join(json_lines)
        else: # is_list_all
            return "\n\n".join(["\n".join(pdf_lines), "\n".join(json_lines)])

        
    # 2. Handle viewing file content
    is_view = False
    search_query = ""
    
    # Check prefixes
    for prefix in ("/view ", "xem ", "/json ", "show "):
        if prompt.strip().lower().startswith(prefix):
            is_view = True
            search_query = prompt.strip()[len(prefix):].strip()
            break
            
    if is_view:
        if not search_query:
            return "⚠️ Vui lòng nhập từ khóa tìm kiếm. Ví dụ: /view フルサト"
            
        json_dir = project_dir / "data" / "pdf" / "json"
        if not json_dir.exists():
            return "❌ Thư mục data/pdf/json không tồn tại."
            
        # Scan for matching files
        matches = []
        for f in json_dir.iterdir():
            if f.is_file() and f.suffix.lower() == ".json":
                # Check if all words in search_query are in the filename (case-insensitive)
                words = search_query.lower().split()
                filename_lower = f.name.lower()
                if all(word in filename_lower for word in words):
                    matches.append(f)
                    
        if not matches:
            return f"❌ Không tìm thấy file JSON nào khớp với từ khóa: \"{search_query}\""
            
        # Format outputs
        output_parts = []
        for match in sorted(matches, key=lambda x: x.name):
            try:
                with open(match, "r", encoding="utf-8") as file_handle:
                    content = file_handle.read()
                output_parts.append(f"File: {match.name}\n{content.strip()}")
            except Exception as e:
                output_parts.append(f"File: {match.name}\n❌ Lỗi khi đọc file: {e}")
                
        # Return matched files separated by blank line
        return "\n\n".join(output_parts)
        
    return None

def main():
    try:
        if len(sys.argv) < 2:
            print("Usage: python run_agy.py <prompt> [chat_id]")
            sys.exit(1)
            
        prompt = sys.argv[1]
        chat_id = sys.argv[2] if len(sys.argv) >= 3 else "default_telegram_user"
        
        project_dir = Path(__file__).parent.resolve()
        env = _build_clean_env()
        home_dir = Path(env["HOME"])
        brain_dir = home_dir / ".gemini" / "antigravity-cli" / "brain"
        
        # Handle conversation mapping
        conv_mapping_path = project_dir / "data" / "telegram_conversations.json"
        conv_mapping = {}
        if conv_mapping_path.exists():
            try:
                with open(conv_mapping_path, "r", encoding="utf-8") as f:
                    conv_mapping = json.load(f)
            except Exception:
                pass
                
        # Clear conversation if requested
        is_reset = prompt.strip().lower() in ("/reset", "/start", "/clear")
        if is_reset and chat_id:
            conv_mapping.pop(str(chat_id), None)
            try:
                conv_mapping_path.parent.mkdir(parents=True, exist_ok=True)
                with open(conv_mapping_path, "w", encoding="utf-8") as f:
                    json.dump(conv_mapping, f, indent=2)
            except Exception:
                pass
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8")
            print("Đã đặt lại cuộc hội thoại. Bạn có thể bắt đầu yêu cầu mới!")
            return

        # Check if there is an existing conversation for this chat_id
        conversation_id = None
        if chat_id and not is_reset:
            mapped_id = conv_mapping.get(str(chat_id))
            if mapped_id and (brain_dir / mapped_id).exists():
                conversation_id = mapped_id

        existing_dirs = _get_brain_dirs(brain_dir)
        
        cmd = [
            "agy",
            "--dangerously-skip-permissions",
        ]
        if conversation_id:
            cmd.extend(["--conversation", conversation_id])
            
        cmd.extend([
            "--print", prompt,
            "--add-dir", str(project_dir),
        ])
        
        creation_flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        
        reply = ""
        local_reply = _handle_local_commands(prompt, project_dir)
        
        if local_reply:
            reply = local_reply
        else:
            result = subprocess.run(
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
            
            new_conv_id = None
            new_dirs = _get_brain_dirs(brain_dir) - existing_dirs
            if new_dirs:
                new_conv_id = new_dirs.pop()
                
            target_conv_id = conversation_id if conversation_id else new_conv_id
            
            # Save mapping if it is a new conversation
            if chat_id and new_conv_id and not conversation_id:
                conv_mapping[str(chat_id)] = new_conv_id
                try:
                    conv_mapping_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(conv_mapping_path, "w", encoding="utf-8") as f:
                        json.dump(conv_mapping, f, indent=2)
                except Exception:
                    pass
                    
            if target_conv_id:
                transcript_path = (
                    brain_dir / target_conv_id / ".system_generated" / "logs" / "transcript_full.jsonl"
                )
                if transcript_path.exists():
                    reply = _read_transcript(transcript_path)
                    
            if not reply:
                reply = result.stdout.strip()
            if not reply:
                reply = result.stderr.strip()
                
            # Append error tips if CLI process failed
            if result.returncode != 0:
                if not reply:
                    reply = f"Hệ thống gặp sự cố khi xử lý lệnh (Mã lỗi: {result.returncode})."
                reply += "\n\nGợi ý: Vui lòng gửi /reset để khởi động lại cuộc hội thoại nếu Agent bị kẹt."

        # Clean the reply for Telegram
        telegram_reply = _clean_reply_for_telegram(reply)

        # Print the clean reply to stdout in UTF-8
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        print(telegram_reply)
        
    except Exception as e:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        print(f"⚠️ Hệ thống gặp lỗi kỹ thuật:\n{str(e)}\n\nGợi ý: Bạn hãy gửi lệnh /reset để khởi động lại phiên làm việc.")

if __name__ == "__main__":
    main()
