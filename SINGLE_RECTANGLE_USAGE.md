# 單白色矩形框檢測和文字分割功能使用說明

## 功能概述

`single_rectangle_detector.py` 提供了專門針對**一個裁剪影像中只有一個白色矩形框**的檢測和文字分割功能。這個模組已經完全隔離，可以獨立使用，不依賴於現有的複雜OCR分析系統。

## 核心功能特點

### 🎯 專門化設計
- **單矩形框專用**: 專門處理一個影像中只有一個白色矩形框的情況
- **隔離實現**: 完全獨立的模組，不與現有系統耦合
- **優化參數**: 針對單矩形框場景調整的檢測參數

### 🔍 核心檢測邏輯
- **白色區域檢測**: 基於像素亮度閾值檢測白色區域
- **形態學處理**: 去除噪點並連接斷裂區域
- **矩形過濾**: 根據面積、長寬比、填充比率篩選候選矩形
- **品質評分**: 為每個候選矩形計算品質分數，選擇最佳結果

### ✂️ 智能文字分割
- **位置基準**: 以矩形框的中心X座標為分割線
- **前後分類**: 文字根據中心位置自動分為矩形框前後兩部分
- **自動排序**: 同一區域內的文字按X座標排序
- **回退機制**: 當未檢測到矩形框時，所有文字歸入前段

## 主要類別

### 1. `SingleRectangleDetector` - 單矩形框檢測器

```python
from single_rectangle_detector import SingleRectangleDetector

# 初始化檢測器
detector = SingleRectangleDetector()

# 或者使用自定義配置
config = {
    "WHITE_THRESHOLD": 200,      # 降低白色閾值
    "MIN_RECTANGLE_AREA": 30,    # 降低最小面積要求
    "FILL_RATIO_THRESHOLD": 0.5  # 降低填充比率要求
}
detector = SingleRectangleDetector(config)

# 檢測矩形框
rectangle_info = detector.detect_single_rectangle(image)
```

### 2. `SingleRectangleTextSplitter` - 文字分割器

```python
from single_rectangle_detector import SingleRectangleTextSplitter

# 初始化文字分割器
splitter = SingleRectangleTextSplitter(['ch_tra', 'en'])

# 分割文字
result = splitter.split_text_by_rectangle(image, rectangle_info)
```

### 3. `SingleRectangleAnalyzer` - 完整分析器

```python
from single_rectangle_detector import SingleRectangleAnalyzer

# 初始化完整分析器
analyzer = SingleRectangleAnalyzer()

# 一次性完成檢測和分割
result = analyzer.analyze_single_rectangle_image(image)
```

## 檢測配置參數

### 默認配置
```python
{
    "WHITE_THRESHOLD": 240,           # 白色閾值 (0-255)
    "MIN_RECTANGLE_AREA": 50,         # 最小矩形面積
    "MAX_RECTANGLE_AREA": 10000,      # 最大矩形面積
    "MIN_ASPECT_RATIO": 0.1,          # 最小長寬比
    "MAX_ASPECT_RATIO": 20,           # 最大長寬比
    "FILL_RATIO_THRESHOLD": 0.6,      # 填充比率閾值
    "MORPHOLOGY_KERNEL_SIZE": 2,      # 形態學核心大小
    "CONTOUR_SIMPLIFICATION": 0.02    # 輪廓簡化係數
}
```

### 配置調整建議
- **檢測不到矩形框**: 降低 `WHITE_THRESHOLD` (240→200→180)
- **誤檢太多小區域**: 提高 `MIN_RECTANGLE_AREA` (50→100→200)
- **矩形框要求太嚴格**: 降低 `FILL_RATIO_THRESHOLD` (0.6→0.4→0.3)
- **長條形矩形檢測不到**: 調整 `MAX_ASPECT_RATIO` (20→50→100)

## 返回結果格式

### 檢測結果 (`rectangle_info`)
```python
{
    'bbox': (x1, y1, x2, y2),        # 矩形框邊界座標
    'center': (x, y),                # 中心點座標
    'area': 600.0,                   # 面積
    'width': 30,                     # 寬度
    'height': 20,                    # 高度
    'aspect_ratio': 1.5,             # 長寬比
    'fill_ratio': 0.85,              # 填充比率
    'score': 1250.0,                 # 品質分數
    'contour': numpy_array           # OpenCV輪廓
}
```

### 文字分割結果 (`split_result`)
```python
{
    'rectangle_found': True,         # 是否找到矩形框
    'rectangle_info': {...},         # 矩形框信息
    'before_rectangle': {
        'texts': [                   # 前段文字列表
            {
                'text': '玩家名稱',
                'confidence': 0.95,
                'bbox': [...],
                'center_x': 80.0
            }
        ],
        'combined': '玩家名稱'        # 組合後的前段文字
    },
    'after_rectangle': {
        'texts': [...],              # 後段文字列表
        'combined': 'CHO123頻道'     # 組合後的後段文字
    },
    'all_texts': [...],              # 所有文字
    'split_success': True,           # 分割是否成功
    'error': None                    # 錯誤信息
}
```

## 使用範例

### 基本使用
```python
from PIL import Image
from single_rectangle_detector import SingleRectangleAnalyzer

# 載入圖片
image = Image.open("your_image.png")

# 執行分析
analyzer = SingleRectangleAnalyzer()
result = analyzer.analyze_single_rectangle_image(image)

# 取得結果
if result['detection_success']:
    before_text = result['text_split_result']['before_rectangle']['combined']
    after_text = result['text_split_result']['after_rectangle']['combined']
    
    print(f"玩家名稱: {before_text}")
    print(f"頻道信息: {after_text}")
else:
    all_text = result['text_split_result']['before_rectangle']['combined']
    print(f"未檢測到矩形框，全部文字: {all_text}")
```

### 自定義配置使用
```python
# 針對特定場景調整參數
detection_config = {
    "WHITE_THRESHOLD": 200,          # 降低白色要求
    "MIN_RECTANGLE_AREA": 20,        # 允許更小的矩形
    "FILL_RATIO_THRESHOLD": 0.4      # 降低填充要求
}

ocr_languages = ['ch_tra', 'en']     # 支援繁體中文和英文

analyzer = SingleRectangleAnalyzer(detection_config, ocr_languages)
result = analyzer.analyze_single_rectangle_image(image)
```

### 只檢測矩形框
```python
from single_rectangle_detector import SingleRectangleDetector

detector = SingleRectangleDetector()
rectangle_info = detector.detect_single_rectangle(image)

if rectangle_info:
    print(f"找到矩形框: 位置 {rectangle_info['bbox']}")
    print(f"面積: {rectangle_info['area']}")
    print(f"中心點: {rectangle_info['center']}")
else:
    print("未找到矩形框")
```

### 只進行文字分割
```python
from single_rectangle_detector import SingleRectangleTextSplitter

splitter = SingleRectangleTextSplitter()

# 可以傳入已知的矩形框信息
result = splitter.split_text_by_rectangle(image, rectangle_info)

# 或者讓系統自動檢測
result = splitter.split_text_by_rectangle(image, None)

before_texts = result['before_rectangle']['texts']
after_texts = result['after_rectangle']['texts']
```

## 整合到現有系統

### 替換現有的矩形框檢測邏輯
```python
# 在你的OCR分析器中
from single_rectangle_detector import SingleRectangleAnalyzer

class YourOCRAnalyzer:
    def __init__(self):
        self.rectangle_analyzer = SingleRectangleAnalyzer()
    
    def analyze_image(self, image):
        # 使用單矩形框分析器
        result = self.rectangle_analyzer.analyze_single_rectangle_image(image)
        
        # 根據結果進行後續處理
        if result['detection_success']:
            player_name = result['text_split_result']['before_rectangle']['combined']
            channel_info = result['text_split_result']['after_rectangle']['combined']
            return self.process_split_text(player_name, channel_info)
        else:
            # 回退處理
            all_text = result['text_split_result']['before_rectangle']['combined']
            return self.process_fallback_text(all_text)
```

## 性能和準確性

### 優勢
- ✅ **專門優化**: 針對單矩形框場景特別優化
- ✅ **獨立運行**: 不依賴複雜的現有系統
- ✅ **參數可調**: 靈活的配置系統適應不同場景
- ✅ **回退機制**: 檢測失敗時自動回退到傳統方法

### 限制
- ⚠️ **單矩形限制**: 只適用於一個矩形框的情況
- ⚠️ **白色矩形**: 只檢測白色或接近白色的矩形
- ⚠️ **依賴EasyOCR**: 需要安裝EasyOCR和相關語言模型

## 故障排除

### 常見問題

1. **檢測不到矩形框**
   - 檢查 `WHITE_THRESHOLD` 設置是否太高
   - 降低 `MIN_RECTANGLE_AREA` 和 `FILL_RATIO_THRESHOLD`
   - 確認矩形框是否足夠白(亮度 > 閾值)

2. **誤檢測太多**
   - 提高 `MIN_RECTANGLE_AREA` 過濾小區域
   - 調整 `MIN_ASPECT_RATIO` 和 `MAX_ASPECT_RATIO`
   - 提高 `FILL_RATIO_THRESHOLD` 要求更規整的矩形

3. **文字分割不準確**
   - 檢查OCR是否正確識別文字
   - 確認矩形框位置是否正確
   - 調整OCR語言設置

4. **性能問題**
   - 裁剪圖片到必要區域
   - 降低圖片解析度
   - 調整 `MORPHOLOGY_KERNEL_SIZE` 減少處理複雜度

---

此功能提供了一個簡潔、專用的解決方案，專門處理單個白色矩形框的檢測和基於位置的文字分割任務。