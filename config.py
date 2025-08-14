GEMINI_API_KEY = "AIzaSyBv_hIyvmyLb9vXIh2nzlKkVtm9AyvnRLU"

# ROI座標將在程式啟動時由使用者選擇
ROI_COORDINATES = None

# 多商品字典格式：主商品名稱 -> 相關關鍵字列表
SELLING_ITEMS = {
    "母礦": ["母礦", "青銅母礦", "鋼鐵母礦", "紫礦石母礦", "鋰礦石母礦"],
    "盾牌防禦力60%": ["盾牌防禦力60", "盾牌防禦60", "盾牌防60", "盾防60", "盾60"],
    "雙手棍攻擊力60%": ["雙手棍攻擊力60", "雙手棍攻擊60", "雙手棍攻60", "雙棍攻擊力60", "雙棍攻擊60", "雙棍攻60"],
    "弓攻擊力60%": ["弓攻擊力60", "弓攻擊60", "弓攻60", "弓60"],
    "催化劑": ["催化劑"],
}

# 暫停監控的物品 - 保留對照表但不進行監控
INACTIVE_ITEMS = {
    "披風": ["披風", "乾淨披風"],
}

SCAN_INTERVAL = 2

# 截圖保存設定
SAVE_SCREENSHOTS = False  # 是否保存截圖
SCREENSHOT_FOLDER = "screenshots"  # 截圖保存資料夾

# Rectangle detection parameters for OCR_Rectangle analyzer
RECTANGLE_DETECTION_CONFIG = {
    "WHITE_THRESHOLD": 245,              # White detection threshold (adjusted from 250)
    "MIN_RECTANGLE_AREA": 100,           # Minimum rectangle area
    "MAX_RECTANGLE_AREA": 5000,          # Maximum rectangle area
    "MIN_ASPECT_RATIO": 0.2,             # Minimum aspect ratio
    "MAX_ASPECT_RATIO": 10,              # Maximum aspect ratio
    "FILL_RATIO_THRESHOLD": 0.7,         # Rectangle fill ratio threshold
    "TEXT_ASSIGNMENT_TOLERANCE": 5,      # Text assignment tolerance in pixels
}

# OCR Debug settings for OCR_Rectangle analyzer
OCR_DEBUG_CONFIG = {
    "ENABLE_RECTANGLE_DEBUG": False,     # Enable rectangle detection debugging
    "DEBUG_OUTPUT_DIR": "rectangle_debug", # Debug output directory
}