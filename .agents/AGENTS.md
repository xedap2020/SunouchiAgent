# Project Rules & Architecture Notes for Sunouchi IT Agent

## 1. n8n Telegram Bot Integration & agy CLI
- **Spawning CLI from n8n:** When launching `agy` CLI from n8n's `Execute Command` node on Windows, you must always run it through the wrapper script [run_agy.py](file:///e:/SunouchiAgent/run_agy.py) instead of calling `agy` directly.
- **Environment Scrubbing:** The `ANTIGRAVITY_AGENT` environment variable must be popped from the environment before running `agy`, otherwise the CLI will hang indefinitely.
- **Output Parsing:** The CLI logs internal debug and tool traces. `run_agy.py` extracts only the clean assistant response from the underlying `transcript.jsonl` log file, formatting tables into readable lists and removing url-encoded local `file:///` paths before sending to Telegram.

## 2. n8n Database Credentials & Version Caching (Crucial)
- **Active Workflow Caching:** n8n caches active workflows and credentials in its memory. Any manual database updates to `workflow_entity` or `credentials_entity` while the n8n process is running will not be immediately visible in active triggers.
- **Workflow Version History:** If n8n has Version History / Git integration enabled, active/published runs load nodes from the `workflow_history` table (using `activeVersionId` link), not from the draft `workflow_entity` table.
- **Reactivating Cache:** To force n8n to sync and load new database or history changes, the user must always toggle the workflow **OFF (Unpublish)** and **ON (Publish)** in the browser UI, and reload the browser page to refresh the frontend state.

## 3. Formatting JSON Output for Users (Strict Format Rule)
- **Raw JSON Display:** When the user asks to display, view, or check the content/result of any JSON file (such as the extracted invoice result files under `data/pdf/json/`), the Agent **MUST** print the filename of the JSON file on the first line in the format: `File: <filename>` (e.g. `File: フルサト J164337 S4 d..json`).
- **No Conversational Filler & No Code Blocks:** Immediately below the filename line, the Agent must output the raw JSON content directly as plain text, **WITHOUT** wrapping it in triple backticks or any markdown code blocks. The Agent must not add any conversational filler, explanations, or introductory/concluding remarks before or after.
- **Multiple Files:** If the user requests to display multiple JSON files, the Agent **MUST** output each file sequentially using the same format (`File: <filename>` followed by the raw JSON text), separating the files with a single blank line.
  ```text
  File: <filename1>
  {
    "raw_json_content_1": ...
  }
  ```

## 4. Onboarding Instructions for New Forms (Strict Wording)
- **Response Format:** When the user asks to onboard, set up, or teach the system a new invoice/order form layout, the Agent **MUST** respond with the following exact text structure and links (preserving the markdown and exact wording):
  ```text
  Để giúp trợ lý AI tự động học cách đọc biểu mẫu (form) hóa đơn/đơn hàng mới, bạn chỉ cần thực hiện 3 bước đơn giản sau:

  1. **Chuẩn bị file mẫu**:
     * Lấy file PDF đơn hàng gốc của đối tác.
     * Chụp ảnh màn hình ERP (phần thông tin đơn hàng này sau khi bạn đã nhập thủ công vào ERP).
     * Đặt cả file PDF và file ảnh này vào thư mục **[NewForm](file:///E:/SunouchiAgent/data/pdf/NewForm/)**.

  2. **Đặt tên file giống nhau**:
     * Hãy đặt tên file PDF và file ảnh ERP **giống hệt nhau** để trợ lý tự động đối chiếu thông tin.
     * *Ví dụ*: `Kagaya_J166817.pdf` đi kèm với `Kagaya_J166817.png` (hoặc `.jpg`).
     *(Mẹo nhỏ: Bạn nên chuẩn bị từ 2-3 đơn hàng mẫu khác nhau để trợ lý học chính xác hơn).*

  3. **Bắt đầu**:
     * Sau khi đã copy các file mẫu vào đúng vị trí, bạn chỉ cần nhắn: **"Chạy script chuẩn bị"** để bắt đầu quy trình học form mới.
  ```

