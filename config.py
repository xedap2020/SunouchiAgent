DB_CONFIG = {
    'host': 'localhost',
    'database': 'test_sunouchiit2',
    'user': 'root',
    'password': 'NewRoot@123!',
    'port': 3306
}

# Telegram Configuration (Model B)
# Lấy api_id và api_hash từ https://my.telegram.org/
TELEGRAM_API_ID = 1234567          # Thay bằng api_id của bạn (kiểu số nguyên)
TELEGRAM_API_HASH = 'your_api_hash' # Thay bằng api_hash của bạn (kiểu chuỗi)
TELEGRAM_PHONE = '+84xxxxxxxx'     # Số điện thoại đăng ký Telegram của bạn

# Gemini API Key (Google AI Studio)
GEMINI_API_KEY = 'your_gemini_api_key' # Thay bằng Gemini API Key của bạn

# Gemini Model to use
# Mặc định là 'gemini-2.5-flash' (nhanh và rẻ). 
# Bạn có thể đổi sang 'gemini-2.5-pro' nếu cần độ chính xác cao hơn.
GEMINI_MODEL = 'gemini-2.5-flash'

# Telegram Channel/Group/Chat to listen to
# Mặc định là 'me' (Saved Messages - Tin nhắn đã lưu).
# Bạn có thể đổi thành Tên hiển thị của Nhóm/Kênh (ví dụ: 'Hoá đơn Sunouchi')
# hoặc Username của Kênh (ví dụ: '@hoadon_sunouchi')
TELEGRAM_CHANNEL = 'me'
