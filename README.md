# 螢幕監控程式

這是一個自動監控螢幕特定區域並分析文字內容的Python程式。

## 功能特色

- 每秒自動截取螢幕指定ROI區域
- 使用Google Gemini AI分析圖片中的文字內容  
- 檢查是否同時包含兩組關鍵字：
  - 第一組：收、收購、買
  - 第二組：披敏、披風敏捷
- 當兩組關鍵字都匹配時會彈出提醒視窗

## 安裝步驟

1. 安裝所需套件：
```bash
pip install -r requirements.txt
```

2. 設定Gemini API Key：
   - 編輯 `config.py` 檔案
   - 將 `GEMINI_API_KEY` 替換為您的實際API金鑰

3. 調整ROI座標（可選）：
   - 修改 `config.py` 中的 `ROI_COORDINATES` 來設定監控區域

## 使用方法

```bash
python screen_monitor.py
```

按 Ctrl+C 停止監控

## 檔案說明

- `screen_monitor.py` - 主程式
- `config.py` - 設定檔
- `requirements.txt` - 依賴套件清單

## 注意事項

- 需要有效的Google Gemini API金鑰
- 第一次執行時可能需要允許螢幕擷取權限