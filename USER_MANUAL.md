# 🎮 MapleStory 交易機會監控系統 - 用戶使用手冊

![Status](https://img.shields.io/badge/Status-Production%20Ready-green)
![Version](https://img.shields.io/badge/Version-v1.0-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)

## 📋 目錄
- [快速開始](#快速開始)
- [系統需求](#系統需求)
- [安裝指南](#安裝指南)
- [使用教學](#使用教學)
- [配置設定](#配置設定)
- [常見問題](#常見問題)
- [技術支持](#技術支持)

## 🚀 快速開始

### 1. 一鍵安裝
```
雙擊執行 → install.bat
等待安裝完成（約5-10分鐘）
```

### 2. 設置監控物品
```
編輯 config_user.py
添加您要出售的物品和關鍵字
```

### 3. 開始監控
```
雙擊執行 → 啟動監控.bat
選擇遊戲聊天視窗區域
自動監控交易機會！
```

## 💻 系統需求

### 必要需求
- **作業系統**: Windows 10/11, macOS 10.14+, Ubuntu 18.04+
- **Python**: 3.8 或更高版本
- **記憶體**: 最少 4GB RAM
- **硬碟空間**: 最少 500MB 可用空間
- **網路**: 穩定的網際網路連接（安裝時需要）

### 建議配置
- **CPU**: Intel Core i5 或同等級以上
- **記憶體**: 8GB RAM 或更多
- **螢幕解析度**: 1920x1080 或更高

## 📦 安裝指南

### 自動安裝（推薦）

1. **下載安裝包**
   - 解壓縮到任意資料夾
   - 確保資料夾路徑不包含中文字符

2. **執行安裝**
   ```
   右鍵以系統管理員身分執行 → install.bat
   ```

3. **等待安裝完成**
   - 系統會自動下載並安裝所有依賴
   - 首次安裝需要下載 OCR 語言模型（約100MB）

### 手動安裝

如果自動安裝失敗，請按以下步驟手動安裝：

```bash
# 1. 安裝 Python 依賴
pip install -r requirements.txt

# 2. 設置 OCR 環境
python install_ocr.py

# 3. 執行程式
python screen_monitor.py
```

## 📖 使用教學

### 第一次使用

1. **編輯配置文件**
   ```python
   # 打開 config_user.py
   SELLING_ITEMS = {
       "披風幸運60%": ["披風幸運60%", "披風幸60%", "披幸60"],
       "母礦": ["母礦", "青銅母礦", "鋼鐵母礦"],
       # 添加更多您想出售的物品...
   }
   ```

2. **啟動程式**
   - 雙擊「啟動監控.bat」
   - 程式會自動使用 OCR_Rectangle 視覺分割引擎

3. **選擇監控區域**
   - 程式啟動後會要求選擇 ROI（監控區域）
   - 用滑鼠拖拉框選遊戲的聊天視窗
   - 確保框選範圍包含完整的交易廣播訊息

4. **開始監控**
   - 選擇是否保存截圖（建議選擇「否」以節省空間）
   - 選擇是否顯示匹配提示窗（建議選擇「是」）
   - 系統開始自動監控

### 監控過程

- **即時顯示**: 控制台會顯示每次分析的結果
- **匹配提醒**: 找到交易機會時會彈出提示窗
- **自動記錄**: 所有匹配結果會自動保存為 HTML 報告

### 查看結果

監控結束後（按 Ctrl+C），系統會：
- 自動生成 HTML 報告
- 開啟瀏覽器顯示匹配結果
- 報告包含：玩家名稱、頻道編號、匹配時間、完整廣播內容

## ⚙️ 配置設定

### 基本設定

```python
# config_user.py

# 監控商品設置
SELLING_ITEMS = {
    "物品名稱": ["關鍵字1", "關鍵字2", "縮寫"],
    # 範例:
    "披風幸運60%": ["披風幸運60%", "披風幸60%", "披幸60"],
    "母礦": ["母礦", "青銅母礦", "鋼鐵母礦"],
}

# 掃描間隔（秒）
SCAN_INTERVAL = 2

# 截圖保存設定
SAVE_SCREENSHOTS = False  # True=保存所有截圖, False=僅保存匹配截圖
```

### 高級設定

```python
# OCR 調試設定
OCR_DEBUG_CONFIG = {
    "ENABLE_RECTANGLE_DEBUG": False,     # 啟用視覺調試
    "DEBUG_OUTPUT_DIR": "rectangle_debug", # 調試輸出目錄
}

# 矩形檢測參數
RECTANGLE_DETECTION_CONFIG = {
    "WHITE_THRESHOLD": 245,              # 白色檢測閾值
    "MIN_RECTANGLE_AREA": 100,           # 最小矩形面積
    "MAX_RECTANGLE_AREA": 5000,          # 最大矩形面積
}
```

### 物品關鍵字設置技巧

1. **包含完整名稱**
   ```python
   "披風幸運60%": ["披風幸運60%", "披風幸運60%卷軸"]
   ```

2. **添加常見縮寫**
   ```python
   "披風幸運60%": ["披風幸60%", "披幸60", "披60"]
   ```

3. **考慮變體寫法**
   ```python
   "耳環智力10%": ["耳環智力10%", "耳智10", "耳環智力10"]
   ```

## ❓ 常見問題

### 安裝問題

**Q: 安裝時提示 "未找到 Python"**
A: 請確保已安裝 Python 3.8+ 並添加到系統 PATH。從 [python.org](https://www.python.org/downloads/) 下載安裝。

**Q: 安裝時網路錯誤**
A: 請檢查網路連接，或嘗試使用手動安裝方式。

**Q: OCR 模型下載失敗**
A: 這是正常現象，系統可以使用 Gemini AI 作為備用分析引擎。

### 使用問題

**Q: 無法偵測到交易廣播**
A: 請檢查：
- ROI 區域是否正確框選聊天視窗
- config_user.py 中的關鍵字是否正確
- 遊戲聊天字體是否清晰

**Q: 誤判率太高**
A: 請：
- 調整關鍵字，使其更精確
- 確保 ROI 區域不包含其他干擾文字
- 檢查遊戲聊天背景是否為純色

**Q: 程式運行緩慢**
A: 請：
- 關閉其他耗資源的程式
- 調整 SCAN_INTERVAL 為較大值（如3-5秒）
- 確保 ROI 區域不要太大

### 功能問題

**Q: 如何添加新的監控物品？**
A: 編輯 config_user.py，在 SELLING_ITEMS 中添加新項目：
```python
"新物品名稱": ["關鍵字1", "關鍵字2"]
```

**Q: 可以同時監控多個遊戲視窗嗎？**
A: 目前版本只支援單一視窗監控。

**Q: 如何查看歷史監控記錄？**
A: 查看 monitoring_session_* 資料夾中的 quick_view.html 報告。

## 🛠️ 技術支持

### 日誌文件位置
- **監控記錄**: `monitoring_session_YYYYMMDD_HHMMSS/`
- **錯誤日誌**: `*.log` 文件
- **調試圖像**: `rectangle_debug/` 資料夾（如啟用）

### 效能調優

1. **優化 ROI 區域**
   - 盡量精確框選聊天區域
   - 避免包含滾動條和其他 UI 元素

2. **調整掃描間隔**
   - 預設 2 秒適合大部分情況
   - 頻繁交易時可調整為 1 秒
   - 效能較低的電腦可調整為 3-5 秒

3. **記憶體管理**
   - 定期清理舊的監控記錄
   - 關閉不必要的截圖保存

### 故障排除

1. **重設配置**
   ```bash
   # 刪除 config_user.py 重新運行 setup.py
   python setup.py
   ```

2. **重新安裝依賴**
   ```bash
   pip uninstall -r requirements.txt -y
   pip install -r requirements.txt
   ```

3. **清除快取**
   ```bash
   # 刪除所有 monitoring_session_* 資料夾
   # 刪除 rectangle_debug 資料夾
   ```

## 📞 聯絡我們

- **GitHub Issues**: [專案 Issues 頁面](https://github.com/pursky7468/maple_story_screen_monitor/issues)
- **使用說明**: 本文件或 CLAUDE.md
- **技術文檔**: DEVELOPER_HANDOVER.md

---

🎮 **享受自動化的交易機會監控體驗！**

*MapleStory 交易機會監控系統 v1.0 - 讓您不再錯過任何賺錢機會！*