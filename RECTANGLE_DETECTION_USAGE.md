# 矩形框檢測功能使用說明

## 功能概述

矩形框檢測結果保存功能已整合到整合測試系統中，當使用矩形框OCR分析器時會自動保存詳細的檢測資料，幫助您分析和調試矩形框檢測算法的性能。

## 自動觸發條件

當滿足以下條件時，系統會自動保存矩形框檢測結果：

1. **主要分析器為矩形框OCR** (`RectangleBasedOCRAnalyzer`)
2. **備用分析器為矩形框OCR** (當主分析器失敗時)

## 保存的檢測資料

### 1. 視覺化圖片 (`detection_visual_[timestamp].png`)
- 原始截圖上標記檢測到的矩形框
- 不同顏色區分不同的矩形框
- 顯示矩形框的面積和長寬比資訊
- 標示OCR檢測到的文字邊界框

### 2. 詳細報告 (`detection_report_[timestamp].json`)

#### 檢測摘要 (`detection_summary`)
```json
{
  "rectangles_detected": 0,      // 檢測到的矩形框數量
  "ocr_texts_found": 1,         // OCR檢測到的文字數量
  "segments_created": 0,         // 創建的文字段落數量
  "has_rectangles": false,       // 是否檢測到矩形框
  "fallback_used": true          // 是否使用回退機制
}
```

#### 檢測參數 (`detection_parameters`)
```json
{
  "white_threshold": 240,         // 白色閾值
  "min_rectangle_area": 100,      // 最小矩形面積
  "max_rectangle_area": 5000,     // 最大矩形面積
  "min_aspect_ratio": 0.2,        // 最小長寬比
  "max_aspect_ratio": 10,         // 最大長寬比
  "fill_ratio_threshold": 0.7     // 填充比率閾值
}
```

#### 矩形框資訊 (`rectangles`)
每個檢測到的矩形框包含：
- `bbox`: 邊界框座標 [x1, y1, x2, y2]
- `center`: 中心點座標 [x, y]
- `area`: 面積
- `aspect_ratio`: 長寬比
- `fill_ratio`: 填充比率
- `position_type`: 位置類型 (left/center/right)

#### OCR結果 (`ocr_results`)
每個OCR檢測到的文字包含：
- `text`: 識別的文字內容
- `confidence`: 信心度 (0-1)
- `bbox`: 文字邊界框座標
- `center_x`: 文字中心X座標
- `assigned_to_rectangle`: 分配到的矩形框ID (-1表示未分配)

#### 段落分析 (`segments`)
每個文字段落包含：
- `segment_id`: 段落ID
- `rectangle_info`: 對應的矩形框資訊
- `combined_text`: 組合後的文字
- `individual_texts`: 個別文字項目的詳細資訊

## 檔案位置

檢測結果保存在測試資料夾的子目錄中：
```
integration_test_[timestamp]/
├── rectangle_detection_details/
│   ├── detection_visual_[timestamp].png
│   └── detection_report_[timestamp].json
├── test_001_[timestamp]_screenshot.png
├── test_001_[timestamp]_analysis.json
└── ...
```

## 使用場景

### 1. 調試矩形框檢測算法
- 檢查檢測參數是否合適
- 分析為什麼某些矩形框未被檢測到
- 調整白色閾值和面積範圍

### 2. 驗證OCR準確性
- 比較OCR識別結果與實際內容
- 檢查信心度是否達到預期
- 分析文字定位準確性

### 3. 分析回退機制
- 了解何時使用回退機制
- 評估回退機制的效果
- 調整檢測策略

### 4. 性能分析
- 追蹤檢測成功率
- 分析不同參數組合的效果
- 持續改進檢測算法

## 範例分析

### 無矩形框檢測情況
當報告顯示 `"rectangles_detected": 0` 和 `"fallback_used": true` 時，說明：
1. 系統未檢測到符合條件的白色矩形框
2. 自動切換到使用所有OCR結果
3. 可能需要調整檢測參數或改進檢測算法

### 檢測參數調整建議
- **矩形框過多**: 提高 `min_rectangle_area` 或降低 `fill_ratio_threshold`
- **矩形框過少**: 降低 `white_threshold` 或 `min_rectangle_area`
- **誤檢測**: 調整 `min_aspect_ratio` 和 `max_aspect_ratio`

## 注意事項

1. **存儲空間**: 每次測試都會生成視覺化圖片和JSON報告，請注意存儲空間
2. **隱私保護**: 報告中包含OCR識別的實際文字內容，請妥善保管
3. **性能影響**: 保存檢測結果會增加少量處理時間，但不會影響分析準確性
4. **自動清理**: 系統不會自動清理舊的檢測報告，請定期手動清理

## 進階用法

### 手動保存檢測結果
```python
from rectangle_detector import RectangleDetectionDebugger
from PIL import Image
import numpy as np

# 載入圖片和檢測結果
image = Image.open("screenshot.png")
rectangles = detector.detect_white_rectangles(image)
ocr_results = reader.readtext(np.array(image))

# 保存檢測報告
vis_path, report_path = RectangleDetectionDebugger.save_detection_report(
    image, rectangles, ocr_results, segments, "output_directory"
)
```

### 批量分析檢測報告
可以編寫腳本批量分析多個檢測報告，統計檢測成功率、常見問題等。

---

此功能幫助您深入了解矩形框檢測的工作原理，為優化檢測算法提供數據支持。