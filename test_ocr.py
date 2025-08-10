#!/usr/bin/env python3
"""OCR分析器測試程式"""

import os
import sys
from PIL import Image
from config import SELLING_ITEMS

try:
    from ocr_analyzer import OCRAnalyzer
    OCR_AVAILABLE = True
except ImportError as e:
    print(f"❌ OCR模組導入失敗: {e}")
    print("\n請先安裝OCR依賴：")
    print("方法1 (推薦)：python install_ocr.py")
    print("方法2 (手動)：pip install easyocr")
    print("方法3 (完整)：pip install -r requirements_ocr.txt")
    OCR_AVAILABLE = False
    OCRAnalyzer = None

def test_ocr_basic():
    """基本OCR功能測試"""
    print("=== OCR基本功能測試 ===")
    
    try:
        analyzer = OCRAnalyzer(SELLING_ITEMS)
        print("✓ OCR分析器初始化成功")
        
        # 創建測試圖片
        test_image = Image.new('RGB', (400, 100), 'white')
        from PIL import ImageDraw, ImageFont
        
        draw = ImageDraw.Draw(test_image)
        try:
            # 嘗試使用系統字體
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            # 使用預設字體
            font = ImageFont.load_default()
        
        # 繪製測試文字
        test_text = "CHO123: 收購披風幸運60%卷軸，價格好商量"
        draw.text((10, 30), test_text, fill='black', font=font)
        
        print(f"測試文字: {test_text}")
        
        # 進行OCR分析
        result, raw_response = analyzer.analyze(test_image)
        
        print(f"分析結果:")
        print(f"  - 識別文字: {result.full_text}")
        print(f"  - 是否匹配: {result.is_match}")
        print(f"  - 玩家名稱: {result.player_name}")
        print(f"  - 頻道編號: {result.channel_number}")
        print(f"  - 信心度: {result.confidence:.2f}")
        print(f"  - 匹配商品: {len(result.matched_items)}")
        
        if result.matched_items:
            for item in result.matched_items:
                print(f"    * {item['item_name']}: {item['keywords_found']}")
        
        return True
        
    except ImportError as e:
        print(f"❌ 導入錯誤: {e}")
        print("請安裝OCR依賴: pip install -r requirements_ocr.txt")
        return False
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

def test_ocr_with_screenshot():
    """使用真實截圖測試OCR"""
    print("\n=== 真實截圖OCR測試 ===")
    
    try:
        analyzer = OCRAnalyzer(SELLING_ITEMS)
        
        # 檢查是否有現有的測試截圖
        screenshot_files = [f for f in os.listdir('.') if f.endswith('.png')]
        
        if not screenshot_files:
            print("沒有找到測試截圖檔案")
            
            # 截取一張測試圖片
            import pyautogui
            print("即將截取全螢幕作為測試...")
            input("按Enter繼續...")
            
            screenshot = pyautogui.screenshot()
            test_file = "test_screenshot.png"
            screenshot.save(test_file)
            print(f"已保存測試截圖: {test_file}")
            screenshot_files = [test_file]
        
        # 使用第一張圖片進行測試
        test_file = screenshot_files[0]
        print(f"使用測試檔案: {test_file}")
        
        image = Image.open(test_file)
        result, raw_response = analyzer.analyze(image)
        
        print(f"\nOCR分析結果:")
        print(f"  - 識別的文字長度: {len(result.full_text)} 字符")
        print(f"  - 是否匹配: {result.is_match}")
        print(f"  - 信心度: {result.confidence:.2f}")
        
        if result.full_text:
            print(f"  - 前100字符: {result.full_text[:100]}...")
        
        if result.matched_items:
            print(f"  - 找到 {len(result.matched_items)} 個匹配商品:")
            for item in result.matched_items:
                print(f"    * {item['item_name']}: {item['keywords_found']}")
        
        # 顯示詳細的OCR結果
        if isinstance(raw_response, list):
            print(f"\n詳細OCR結果 ({len(raw_response)} 個文字區域):")
            for i, item in enumerate(raw_response[:5]):  # 只顯示前5個
                print(f"  {i+1}. '{item['text']}' (信心度: {item['confidence']:.2f})")
        
        return True
        
    except Exception as e:
        print(f"❌ 截圖測試失敗: {e}")
        return False

def test_ocr_performance():
    """OCR性能測試"""
    print("\n=== OCR性能測試 ===")
    
    try:
        import time
        analyzer = OCRAnalyzer(SELLING_ITEMS)
        
        # 創建不同尺寸的測試圖片
        sizes = [(200, 50), (400, 100), (800, 200)]
        
        for width, height in sizes:
            test_image = Image.new('RGB', (width, height), 'white')
            from PIL import ImageDraw, ImageFont
            
            draw = ImageDraw.Draw(test_image)
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except:
                font = ImageFont.load_default()
            
            draw.text((10, 10), f"測試圖片 {width}x{height}", fill='black', font=font)
            draw.text((10, 30), "CHO456: 收購母礦 大量收", fill='black', font=font)
            
            # 測量分析時間
            start_time = time.time()
            result, _ = analyzer.analyze(test_image)
            end_time = time.time()
            
            duration = (end_time - start_time) * 1000  # 毫秒
            
            print(f"  {width}x{height}: {duration:.1f}ms (匹配: {result.is_match})")
        
        return True
        
    except Exception as e:
        print(f"❌ 性能測試失敗: {e}")
        return False

def main():
    """主測試程式"""
    print("OCR分析器測試程式")
    print("=" * 50)
    
    # 檢查OCR可用性
    if not OCR_AVAILABLE:
        print("❌ OCR功能不可用，請先安裝依賴")
        print("\n快速安裝：")
        print("python install_ocr.py")
        return
    
    # 檢查OCR依賴
    try:
        import easyocr
        print(f"✅ EasyOCR版本: {easyocr.__version__}")
    except ImportError:
        print("❌ EasyOCR未安裝")
        print("請執行: python install_ocr.py")
        return
    
    try:
        import cv2
        print(f"✅ OpenCV版本: {cv2.__version__}")
    except ImportError:
        print("❌ OpenCV未安裝")
        print("請執行: pip install opencv-python")
        return
    
    # 執行測試
    tests = [
        ("基本功能測試", test_ocr_basic),
        ("真實截圖測試", test_ocr_with_screenshot), 
        ("性能測試", test_ocr_performance)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n執行 {test_name}...")
            success = test_func()
            results.append((test_name, success))
        except KeyboardInterrupt:
            print("\n測試被中斷")
            break
        except Exception as e:
            print(f"❌ {test_name} 失敗: {e}")
            results.append((test_name, False))
    
    # 顯示測試結果摘要
    print(f"\n{'='*50}")
    print("測試結果摘要:")
    for test_name, success in results:
        status = "✓ 通過" if success else "❌ 失敗"
        print(f"  {test_name}: {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\n總計: {passed}/{total} 個測試通過")

if __name__ == "__main__":
    main()