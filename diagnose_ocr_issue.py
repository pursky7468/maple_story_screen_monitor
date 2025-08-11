#!/usr/bin/env python3
"""
OCR問題診斷工具
分析OCR為何無法識別文字，並提供改進建議
"""

import os
import sys
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

def diagnose_image(image_path):
    """診斷單張圖片的OCR識別問題"""
    print(f"=== 診斷圖片: {image_path} ===")
    
    if not os.path.exists(image_path):
        print(f"[ERROR] 圖片不存在: {image_path}")
        return
    
    try:
        # 讀取圖片
        image = Image.open(image_path)
        print(f"[OK] 圖片大小: {image.size}")
        print(f"[OK] 圖片模式: {image.mode}")
        
        # 轉換為numpy array進行分析
        img_array = np.array(image)
        print(f"[OK] 圖片維度: {img_array.shape}")
        
        # 分析顏色分佈
        if len(img_array.shape) == 3:
            print(f"[OK] RGB數值範圍: R({img_array[:,:,0].min()}-{img_array[:,:,0].max()}) "
                  f"G({img_array[:,:,1].min()}-{img_array[:,:,1].max()}) "
                  f"B({img_array[:,:,2].min()}-{img_array[:,:,2].max()})")
        else:
            print(f"[OK] 灰階數值範圍: {img_array.min()}-{img_array.max()}")
        
        # 分析是否是單一顏色圖片
        unique_colors = len(np.unique(img_array.reshape(-1, img_array.shape[-1]) if len(img_array.shape) == 3 else img_array))
        print(f"[OK] 獨特顏色數量: {unique_colors}")
        
        if unique_colors < 5:
            print("[WARNING] 圖片顏色過於單一，可能沒有文字內容")
        
        # 測試OCR識別
        try:
            # 嘗試導入和測試OCR
            try:
                import easyocr
                reader = easyocr.Reader(['ch_tra', 'en'], verbose=False)
                
                # 直接OCR測試
                ocr_results = reader.readtext(img_array)
                print(f"✅ OCR原始結果數量: {len(ocr_results)}")
                
                if ocr_results:
                    print("📝 OCR識別結果:")
                    for i, (bbox, text, confidence) in enumerate(ocr_results):
                        print(f"   {i+1}. 文字: '{text}' (信心度: {confidence:.3f})")
                        print(f"      位置: {bbox}")
                else:
                    print("❌ OCR未識別到任何文字")
                
                # 測試信心度閾值
                high_conf_results = [(bbox, text, conf) for bbox, text, conf in ocr_results if conf > 0.5]
                med_conf_results = [(bbox, text, conf) for bbox, text, conf in ocr_results if conf > 0.3]
                low_conf_results = [(bbox, text, conf) for bbox, text, conf in ocr_results if conf > 0.1]
                
                print(f"📊 不同信心度閾值的結果:")
                print(f"   > 0.5: {len(high_conf_results)} 個結果")
                print(f"   > 0.3: {len(med_conf_results)} 個結果")
                print(f"   > 0.1: {len(low_conf_results)} 個結果")
                
            except ImportError:
                print("❌ EasyOCR未安裝，無法測試OCR功能")
                
        except Exception as e:
            print(f"❌ OCR測試失敗: {e}")
        
        # 圖片增強測試
        print("\n=== 測試圖片增強效果 ===")
        
        enhanced_results = test_image_enhancements(image, img_array)
        
        return {
            'image_size': image.size,
            'image_mode': image.mode,
            'unique_colors': unique_colors,
            'ocr_results': len(ocr_results) if 'ocr_results' in locals() else 0,
            'enhanced_results': enhanced_results
        }
        
    except Exception as e:
        print(f"❌ 圖片診斷失敗: {e}")
        return None

def test_image_enhancements(image, img_array):
    """測試不同的圖片增強方法"""
    enhancements = []
    
    try:
        import easyocr
        reader = easyocr.Reader(['ch_tra', 'en'], verbose=False)
        
        # 測試1: 轉換為灰階
        if image.mode != 'L':
            gray_image = image.convert('L')
            gray_array = np.array(gray_image)
            results = reader.readtext(gray_array)
            enhancements.append(('灰階轉換', len(results)))
            print(f"   灰階轉換: {len(results)} 個結果")
        
        # 測試2: 對比度增強
        enhancer = ImageEnhance.Contrast(image.convert('L'))
        contrast_image = enhancer.enhance(2.0)
        contrast_array = np.array(contrast_image)
        results = reader.readtext(contrast_array)
        enhancements.append(('對比度增強(2.0)', len(results)))
        print(f"   對比度增強: {len(results)} 個結果")
        
        # 測試3: 銳利度增強
        sharpness_enhancer = ImageEnhance.Sharpness(image.convert('L'))
        sharp_image = sharpness_enhancer.enhance(2.0)
        sharp_array = np.array(sharp_image)
        results = reader.readtext(sharp_array)
        enhancements.append(('銳利度增強(2.0)', len(results)))
        print(f"   銳利度增強: {len(results)} 個結果")
        
        # 測試4: 組合增強
        combined = image.convert('L')
        combined = ImageEnhance.Contrast(combined).enhance(2.0)
        combined = ImageEnhance.Sharpness(combined).enhance(1.5)
        combined_array = np.array(combined)
        results = reader.readtext(combined_array)
        enhancements.append(('組合增強', len(results)))
        print(f"   組合增強: {len(results)} 個結果")
        
        # 測試5: 不同閾值
        for threshold in [0.1, 0.3, 0.5, 0.7]:
            results = reader.readtext(img_array)
            filtered_results = [r for r in results if r[2] > threshold]
            enhancements.append((f'閾值{threshold}', len(filtered_results)))
            print(f"   信心度閾值{threshold}: {len(filtered_results)} 個結果")
            
        return enhancements
        
    except ImportError:
        print("   ❌ EasyOCR未安裝，無法測試增強效果")
        return []
    except Exception as e:
        print(f"   ❌ 增強測試失敗: {e}")
        return []

def diagnose_ocr_analyzer():
    """診斷OCR分析器的設定問題"""
    print("\n=== 診斷OCR分析器設定 ===")
    
    try:
        from ocr_analyzer import OCRAnalyzer
        from config import SELLING_ITEMS
        
        print("[OK] 成功導入OCR分析器")
        
        # 測試初始化
        analyzer = OCRAnalyzer(SELLING_ITEMS)
        print(f"[OK] OCR分析器初始化成功")
        print(f"[OK] 策略類型: {analyzer.strategy_type}")
        
        # 檢查語言設定
        if hasattr(analyzer, 'reader') and analyzer.reader:
            print(f"[OK] EasyOCR讀取器已初始化")
        else:
            print("[ERROR] EasyOCR讀取器初始化失敗")
            
        return True
        
    except Exception as e:
        print(f"❌ OCR分析器診斷失敗: {e}")
        return False

def main():
    """主診斷程序"""
    print("OCR問題診斷工具")
    print("=" * 50)
    
    # 診斷OCR分析器
    analyzer_ok = diagnose_ocr_analyzer()
    
    if not analyzer_ok:
        print("OCR分析器有問題，請先修復")
        return
    
    # 診斷最新的測試截圖
    test_folder = None
    folders = [f for f in os.listdir('.') if f.startswith('integration_test_')]
    if folders:
        test_folder = max(folders)  # 獲取最新的測試資料夾
        print(f"\n=== 診斷測試資料夾: {test_folder} ===")
        
        # 尋找截圖檔案
        screenshot_files = []
        for file in os.listdir(test_folder):
            if file.endswith('_screenshot.png'):
                screenshot_files.append(os.path.join(test_folder, file))
        
        if screenshot_files:
            print(f"找到 {len(screenshot_files)} 個截圖檔案")
            
            # 診斷前3個截圖
            for i, screenshot in enumerate(screenshot_files[:3]):
                diagnose_image(screenshot)
                print()
                
        else:
            print("❌ 未找到截圖檔案")
    else:
        print("❌ 未找到測試資料夾")
    
    # 提供改進建議
    print("\n=== 改進建議 ===")
    print("1. 檢查截圖是否包含清晰的文字內容")
    print("2. 嘗試調整OCR的信心度閾值（從0.5降低到0.3或0.1）")
    print("3. 使用圖片增強技術提高文字清晰度")
    print("4. 確認截圖的ROI區域包含有效的遊戲聊天內容")
    print("5. 檢查圖片是否過小或解析度過低")

if __name__ == "__main__":
    main()