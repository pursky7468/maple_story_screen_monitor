#!/usr/bin/env python3
"""
簡單的OCR測試工具
"""

import os
from PIL import Image
import numpy as np

def test_ocr_basic():
    """基本OCR測試"""
    print("=== OCR基本測試 ===")
    
    try:
        # 測試導入
        import easyocr
        print("[OK] EasyOCR已安裝")
        
        # 初始化讀取器
        reader = easyocr.Reader(['ch_tra', 'en'], verbose=False)
        print("[OK] EasyOCR讀取器初始化成功")
        
        return reader
    except ImportError as e:
        print(f"[ERROR] EasyOCR未安裝: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] EasyOCR初始化失敗: {e}")
        return None

def test_screenshot_ocr(reader, image_path):
    """測試截圖OCR識別"""
    print(f"\n=== 測試截圖: {image_path} ===")
    
    if not os.path.exists(image_path):
        print("[ERROR] 截圖檔案不存在")
        return
    
    try:
        # 載入圖片
        image = Image.open(image_path)
        print(f"[OK] 圖片大小: {image.size}")
        print(f"[OK] 圖片模式: {image.mode}")
        
        # 轉換為numpy array
        img_array = np.array(image)
        
        # 分析圖片基本資訊
        if len(img_array.shape) == 3:
            unique_pixels = len(np.unique(img_array.reshape(-1, img_array.shape[-1]), axis=0))
        else:
            unique_pixels = len(np.unique(img_array))
        
        print(f"[OK] 獨特像素數: {unique_pixels}")
        
        if unique_pixels < 10:
            print("[WARNING] 圖片顏色過於單一")
        
        # OCR識別測試
        if reader:
            # 測試不同信心度閾值
            results = reader.readtext(img_array)
            print(f"[OK] OCR原始結果數量: {len(results)}")
            
            if results:
                print("識別到的文字:")
                for i, (bbox, text, confidence) in enumerate(results):
                    print(f"  {i+1}. '{text}' (信心度: {confidence:.3f})")
                    
                # 測試不同閾值
                for threshold in [0.1, 0.3, 0.5, 0.7]:
                    filtered = [r for r in results if r[2] > threshold]
                    print(f"  閾值 {threshold}: {len(filtered)} 個結果")
            else:
                print("[WARNING] OCR未識別到任何文字")
                
                # 嘗試圖片預處理
                print("嘗試圖片增強...")
                
                # 轉灰階
                if image.mode != 'L':
                    gray_img = image.convert('L')
                    gray_results = reader.readtext(np.array(gray_img))
                    print(f"  灰階處理: {len(gray_results)} 個結果")
                
                # 對比度增強
                from PIL import ImageEnhance
                enhancer = ImageEnhance.Contrast(image.convert('L'))
                enhanced_img = enhancer.enhance(2.0)
                enhanced_results = reader.readtext(np.array(enhanced_img))
                print(f"  對比度增強: {len(enhanced_results)} 個結果")
        else:
            print("[ERROR] OCR讀取器未初始化")
            
    except Exception as e:
        print(f"[ERROR] 測試失敗: {e}")

def test_current_ocr_analyzer():
    """測試目前的OCR分析器"""
    print("\n=== 測試OCR分析器 ===")
    
    try:
        from ocr_analyzer import OCRAnalyzer
        from config import SELLING_ITEMS
        
        analyzer = OCRAnalyzer(SELLING_ITEMS)
        print("[OK] OCR分析器創建成功")
        print(f"[OK] 策略類型: {analyzer.strategy_type}")
        
        # 檢查閾值設定
        print(f"[INFO] 目前OCR信心度閾值: 檢查analyze_image方法中的設定")
        
        return analyzer
        
    except Exception as e:
        print(f"[ERROR] OCR分析器測試失敗: {e}")
        return None

def main():
    """主程序"""
    print("簡單OCR診斷工具")
    print("=" * 40)
    
    # 測試OCR基本功能
    reader = test_ocr_basic()
    
    # 測試OCR分析器
    analyzer = test_current_ocr_analyzer()
    
    if reader:
        # 尋找最新測試截圖
        test_folders = [f for f in os.listdir('.') if f.startswith('integration_test_')]
        if test_folders:
            latest_folder = max(test_folders)
            print(f"\n[INFO] 使用測試資料夾: {latest_folder}")
            
            screenshots = []
            for file in os.listdir(latest_folder):
                if file.endswith('_screenshot.png'):
                    screenshots.append(os.path.join(latest_folder, file))
            
            if screenshots:
                # 測試前2個截圖
                for screenshot in screenshots[:2]:
                    test_screenshot_ocr(reader, screenshot)
            else:
                print("[WARNING] 未找到截圖檔案")
        else:
            print("[WARNING] 未找到測試資料夾")
    
    # 提供建議
    print("\n=== 改進建議 ===")
    print("1. 降低OCR信心度閾值 (從0.5改為0.3或0.1)")
    print("2. 增加圖片預處理步驟")
    print("3. 檢查截圖內容是否包含清楚的中文文字")
    print("4. 確認ROI選擇包含遊戲聊天區域")

if __name__ == "__main__":
    main()