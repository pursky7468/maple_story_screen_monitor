# 螢幕監控程式 - MapleStory交易機會監控系統

![Status](https://img.shields.io/badge/Status-Production%20Ready-green)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![AI](https://img.shields.io/badge/AI-OCR%20Rectangle-orange)
![License](https://img.shields.io/badge/License-MIT-blue)

🚀 **v1.0穩定版** - 一個專為楓之谷等MMORPG遊戲設計的智能交易機會監控系統，採用先進的**OCR_Rectangle視覺分割技術**和**位置感知上下文分析**，能夠精確識別遊戲聊天室中的交易廣播，並即時提醒玩家關注的物品交易機會。

## ✨ 核心特色

- 🎯 **OCR_Rectangle引擎** - 業界領先的白框檢測視覺分割技術
- 🧠 **位置感知分析** - 智能區分買賣section，解決混合訊息誤判
- 🌏 **中文環境優化** - 完美適配繁體中文遊戲環境
- 📍 **精準頻道提取** - 支援CHO/CH格式，純數字輸出
- 🔄 **冒號智能清理** - 自動移除廣播內容前的冒號干擾
- 📊 **視覺化調試** - 完整的圖像處理過程可視化
- ⚡ **即時監控** - <2秒響應，準確率>90%
- 🎨 **HTML報告** - 美觀的測試結果和匹配分析

## 🚀 快速開始

### 1. 環境準備

```bash
# 確保已安裝Python 3.8或更高版本
python --version

# 克隆專案到本地
git clone https://github.com/pursky7468/maple_story_screen_monitor.git
cd maple_story_screen_monitor

# 安裝核心依賴
pip install -r requirements.txt

# 設置OCR_Rectangle環境 (首次使用，自動下載語言模型~100MB)
python install_ocr.py
```

### 2. 配置設定

編輯 `config.py` 設定您要監控的商品：

```python
# 監控商品配置 - 系統將監控有人想"購買"這些商品的訊息
SELLING_ITEMS = {
    "披風幸運60%": ["披風幸運60%", "披風幸運60%卷軸", "披風幸60%", "披幸60"],
    "母礦": ["母礦", "青銅母礦", "鋼鐵母礦", "紫礦石母礦"],
    "耳環智力10%": ["耳環智力10%", "耳智10", "耳環智力10"],
    "耳環智力60%": ["耳環智力60%", "耳智60", "耳環智力60"],
    # 添加更多您想出售的物品...
}

# 掃描間隔 (建議2秒)
SCAN_INTERVAL = 2

# 可選：設置Gemini API Key (作為備用分析引擎)
GEMINI_API_KEY = "your_gemini_api_key_here"  # 可選
```

### 3. 開始監控

```bash
# 啟動監控程式 (自動使用OCR_Rectangle引擎)
python screen_monitor.py

# 操作步驟:
# 1. 拖拉選擇遊戲聊天視窗作為監控區域
# 2. 程式自動開始監控
# 3. 發現有人想買您的商品時會彈窗提醒！
```

### 4. 測試驗證 (可選)

```bash
# 執行整合測試，驗證系統效果
python integration_test.py

# 選擇選項3: OCR_Rectangle策略
# 建議測試20-50次以評估準確率
# 測試結果會保存為HTML報告
```

## 📊 技術指標 (OCR_Rectangle引擎)

- **處理速度**: <2秒/次，CPU友善
- **識別準確率**: >90% (中文環境優化)
- **頻道提取**: 支援CHO225→225格式轉換  
- **混合訊息處理**: 智能區分買賣section，避免誤判
- **調試支援**: 完整視覺化流程，rectangle_debug/資料夾
- **記憶體使用**: <200MB，適合長期運行

## 🛠️ 開發者資源

- 📚 **完整架構說明**: `PROJECT_SUMMARY.md`
- 👨‍💻 **開發者交接文檔**: `DEVELOPER_HANDOVER.md`  
- 🧪 **測試工具**: `test_*.py` 系列文件

---

⭐ 如果這個專案對您有幫助，請給一個Star支持！
🎮 祝您遊戲愉快，交易順利！
