# 開發者交接文檔

## 快速上手指南

### 1. 環境設置 (5分鐘)
```bash
# 1. 確保Python 3.8+已安装
python --version

# 2. 安装依賴
pip install -r requirements.txt

# 3. 設置OCR (首次使用，需下載約100MB語言模型)
python install_ocr.py

# 4. 配置API Key
# 編輯 config.py，設置您的 Gemini API Key
```

### 2. 基本使用流程 (10分鐘)
```bash
# 1. 啟動主程式
python screen_monitor.py

# 2. 選擇ROI區域 (拖拉選擇遊戲聊天視窗)
# 3. 選擇分析方法 (建議先選Gemini AI)
# 4. 程式開始監控，發現匹配會彈窗提醒

# 進行測試驗證
python integration_test.py
# 選擇測試次數 (建議先測10次)
# 測試完成後開啟 integration_test_*/quick_view.html 查看結果
```

## 核心代碼理解

### 1. 主監控邏輯 (`screen_monitor.py`)
```python
# 關鍵方法理解
class ScreenMonitor:
    def analyze_with_strategy(self, roi_image):
        """策略模式核心 - 委派給具體分析器"""
        return self.analyzer.analyze_and_parse(roi_image)
    
    def format_match_info(self, result):
        """格式化匹配信息用於顯示"""
        # 返回人類可讀的匹配描述
```

### 2. 分析器架構 (`*_analyzer.py`)
```python
# 所有分析器的基類
class TextAnalyzer:
    def analyze_and_parse(self, image):
        """分析圖像並解析結果 - 主要入口"""
    
    def get_error_type(self, error_message):
        """分類錯誤類型 - 用於自動切換"""
        # 回傳: API_QUOTA_EXCEEDED, NETWORK_ERROR, etc.
```

### 3. 自動切換機制 (`integration_test.py`)
```python
# 關鍵邏輯：錯誤檢測與處理
if error_type == "API_QUOTA_EXCEEDED" and fallback_analyzer:
    # 自動切換到OCR分析器
    fallback_result = fallback_analyzer.analyze_image(roi_image)
    # 標記使用了備用分析器
    result["fallback_used"] = True
```

## 重要配置說明

### `config.py` 關鍵設置
```python
# ⚠️ 必須設置
GEMINI_API_KEY = "your_gemini_api_key_here"

# 監控間隔 (秒)
SCAN_INTERVAL = 3

# 關鍵字配置 - 核心業務邏輯
SELLING_ITEMS = {
    "收購關鍵字": ["收", "收購", "買"],
    "目標物品": {
        "披風敏捷60%": ["披敏", "披風敏捷"],
        "母礦": ["母礦"],
        # 💡 新增物品: "物品名稱": ["關鍵字1", "關鍵字2"]
    }
}

# OCR設置
OCR_CONFIDENCE_THRESHOLD = 0.3  # 信心度閾值
```

## 常用操作指令

### 開發測試
```bash
# 單功能測試
python test_improved_ocr.py           # 測試OCR功能
python test_new_html_format.py        # 測試HTML報告格式
python test_player_name_extraction.py # 測試玩家名稱提取

# 整合測試 (推薦)
python integration_test.py
# 選項建議：
# - 測試次數: 20-50 (開發階段)
# - 分析方法: 1 (Gemini AI) 用於高精度測試
# - 分析方法: 2 (OCR) 用於離線測試

# 歷史結果分析
python test_results_merger.py
```

### 調試技巧
```bash
# 1. 查看詳細錯誤 (JSON解析失敗時)
# 檢查: integration_test_*/test_*_debug.txt

# 2. 驗證OCR識別效果
# 開啟: integration_test_*/quick_view.html
# 對照截圖和識別結果

# 3. 檢查API狀態
# Gemini配額: https://aistudio.google.com/
# 錯誤日誌: integration_test_*/test_*_error.json
```

## 擴展開發指南

### 1. 新增分析器
```python
# 1. 繼承基類
class NewAnalyzer(TextAnalyzer):
    def __init__(self, items_config):
        super().__init__(items_config)
        self.strategy_type = "NEW_ANALYZER"
    
    def analyze_image(self, image):
        # 實現具體的圖像分析邏輯
        pass
    
    def get_error_type(self, error_message):
        # 實現錯誤分類邏輯
        pass

# 2. 在 integration_test.py 中添加選項
def get_analyzer_choice(self):
    print("3. 新分析器 (描述)")
    # 添加處理邏輯
```

### 2. 新增監控物品
```python
# 在 config.py 中添加
SELLING_ITEMS = {
    "收購關鍵字": ["收", "收購", "買"],
    "目標物品": {
        # 現有物品...
        "新物品名稱": ["關鍵字1", "關鍵字2", "簡稱"],
        "裝備強化券": ["強化券", "裝備券"],
    }
}
```

### 3. 自定義通知方式
```python
# 在 screen_monitor.py 的 start_monitoring 方法中
if result.is_match:
    # 現有彈窗通知
    self.show_match_popup(formatted_info)
    
    # 💡 新增其他通知方式
    # self.send_line_notify(formatted_info)
    # self.send_discord_webhook(formatted_info)
    # self.play_sound_alert()
```

## 性能優化建議

### 1. OCR性能調優
```python
# 在 ocr_analyzer.py 中調整
OCR_CONFIDENCE_THRESHOLD = 0.3  # 降低→更多結果，升高→更精確
```

### 2. API調用優化
```python
# 在測試時使用較長間隔避免配額用盡
SCAN_INTERVAL = 5  # 生產環境可設為3

# 考慮實現本地快取
def analyze_with_cache(self, image_hash):
    # if image_hash in cache: return cache[image_hash]
    # else: call_api_and_cache()
```

### 3. 記憶體使用優化
```python
# 大量測試時避免記憶體累積
if len(self.merged_results) > 1000:
    self.merged_results = self.merged_results[-500:]  # 只保留最近500筆
```

## 疑難排解清單

### ❌ 常見錯誤及解決方案

**1. `ModuleNotFoundError: No module named 'easyocr'`**
```bash
解決: python install_ocr.py
原因: OCR依賴未安装
```

**2. `API配額已用盡`**
```bash
解決: 
- 等待24小時配額重置
- 升級到付費Gemini API計畫  
- 暫時使用OCR分析器 (選項2)
```

**3. `JSON解析失敗`**
```bash
檢查: integration_test_*/test_*_debug.txt
常見原因: 
- Gemini回應格式變更
- 網路連線不穩定
- API回傳非JSON內容
```

**4. `ROI選擇後沒有反應`**
```bash
檢查:
1. ROI區域是否包含聊天文字
2. 遊戲畫面是否清晰可見
3. 關鍵字配置是否正確
```

**5. `OCR識別率低`**
```bash
優化:
1. 調整遊戲字體大小 (建議12pt以上)
2. 提高遊戲解析度
3. 確保聊天視窗背景對比度足夠
4. 降低OCR_CONFIDENCE_THRESHOLD (在config.py中)
```

## 代碼質量檢查

### 提交前檢查清單
- [ ] 所有測試通過 (`python integration_test.py` 至少10次成功)
- [ ] 代碼有適當中文註釋
- [ ] 配置文件已更新 (如有新增參數)
- [ ] README或文檔已更新 (如有新功能)
- [ ] 錯誤處理完善 (特別是網路請求部分)

### 代碼風格約定
```python
# ✅ 推薦寫法
def analyze_image(self, roi_image):
    """分析ROI圖像並返回結果"""
    try:
        result = self._process_image(roi_image)
        return self._format_result(result)
    except Exception as e:
        return f"ERROR: 圖像分析失敗 - {str(e)}"

# ❌ 避免寫法  
def analyze(img):  # 參數名不清晰
    result = some_complex_logic()  # 缺少註釋
    return result  # 缺少錯誤處理
```

## 聯絡資訊

**技術問題**: 查看 `PROJECT_SUMMARY.md` 了解詳細架構
**測試問題**: 運行 `integration_test.py` 並查看HTML報告
**配置問題**: 檢查 `config.py` 中的設置

---
💡 **提示**: 建議新手開發者先運行測試程式熟悉系統行為，再開始修改代碼。

📚 **學習資源**:
- EasyOCR文檔: https://github.com/JaidedAI/EasyOCR
- Gemini API文檔: https://ai.google.dev/docs
- OpenCV教學: https://opencv-python-tutroals.readthedocs.io/

*最後更新: 2025年8月10日*