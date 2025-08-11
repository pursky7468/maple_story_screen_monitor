#!/usr/bin/env python3
"""
調試OCR過濾邏輯
"""

import os
import numpy as np
from PIL import Image

def direct_ocr_test():
    """直接測試EasyOCR，不經過我們的分析器"""
    print("=== 直接EasyOCR測試 ===")
    
    test_image_path = r"C:\Users\User\Desktop\螢幕監控程式\monitoring_session_20250810_085346\monitor_001_20250810_085346_670.png"
    
    if not os.path.exists(test_image_path):
        print("[ERROR] 測試圖片不存在")
        return
    
    try:
        import easyocr
        reader = easyocr.Reader(['ch_tra', 'en'], verbose=False)
        
        image = Image.open(test_image_path)
        image_array = np.array(image)
        
        print(f"[INFO] 圖片尺寸: {image.size}")
        
        # 直接OCR
        results = reader.readtext(image_array)
        print(f"[OCR] 原始識別結果數量: {len(results)}")
        
        for i, (bbox, text, confidence) in enumerate(results, 1):
            left_x = bbox[0][0]
            print(f"  {i}. '{text}'")
            print(f"     信心度: {confidence:.3f}")
            print(f"     位置: 左邊{left_x:.0f}px")
            print(f"     長度: {len(text)} 字符")
            
            # 測試過濾條件
            print(f"     > 信心度 > 0.3: {'是' if confidence > 0.3 else '否'}")
            print(f"     > 信心度 > 0.1: {'是' if confidence > 0.1 else '否'}")
            print(f"     > 在左側250px內: {'是' if left_x < 250 else '否'}")
            print()
        
        return results
        
    except Exception as e:
        print(f"[ERROR] 直接OCR測試失敗: {e}")
        return None

def test_analyzer_filtering():
    """測試分析器的過濾邏輯"""
    print("=== 測試OCR分析器過濾 ===")
    
    from ocr_analyzer import OCRAnalyzer
    from config import SELLING_ITEMS
    
    test_image_path = r"C:\Users\User\Desktop\螢幕監控程式\monitoring_session_20250810_085346\monitor_001_20250810_085346_670.png"
    
    try:
        analyzer = OCRAnalyzer(SELLING_ITEMS)
        image = Image.open(test_image_path)
        
        # 調用analyze_image方法，獲得原始OCR結果
        raw_ocr_result = analyzer.analyze_image(image)
        
        print(f"[分析器] 返回結果類型: {type(raw_ocr_result)}")
        print(f"[分析器] 返回結果: {raw_ocr_result}")
        
        if isinstance(raw_ocr_result, list):
            print(f"[分析器] 過濾後結果數量: {len(raw_ocr_result)}")
            
            for i, item in enumerate(raw_ocr_result, 1):
                if isinstance(item, dict):
                    text = item.get('text', '')
                    conf = item.get('confidence', 0)
                    bbox = item.get('bbox', [])
                    left_x = bbox[0][0] if bbox else 0
                    
                    print(f"  {i}. '{text}' (信心度: {conf:.3f}, 左邊: {left_x:.0f}px)")
        
        return raw_ocr_result
        
    except Exception as e:
        print(f"[ERROR] 分析器測試失敗: {e}")
        return None

def compare_results():
    """比較直接OCR和分析器的結果"""
    print("\n=== 結果比較 ===")
    
    direct_results = direct_ocr_test()
    analyzer_results = test_analyzer_filtering()
    
    if direct_results and analyzer_results:
        print(f"直接OCR識別: {len(direct_results)} 個區域")
        print(f"分析器返回: {len(analyzer_results)} 個區域")
        
        # 檢查是否有被過濾的結果
        if len(direct_results) > len(analyzer_results):
            print("\n[發現] 有結果被過濾了！")
            
            # 找出被過濾的結果
            analyzer_texts = {item.get('text', '') for item in analyzer_results if isinstance(item, dict)}
            
            for bbox, text, confidence in direct_results:
                if text not in analyzer_texts:
                    left_x = bbox[0][0]
                    print(f"  被過濾: '{text}' (信心度: {confidence:.3f}, 位置: {left_x:.0f}px)")
                    
                    # 分析為什麼被過濾
                    if confidence <= 0.1:
                        print(f"    原因: 信心度太低 ({confidence:.3f} <= 0.1)")
                    elif confidence <= 0.3:
                        print(f"    原因: 中等信心度但不在玩家區域")
                    else:
                        print(f"    原因: 未知")
        else:
            print("\n[結果] 沒有結果被過濾")
    
    # 建議修正方案
    print(f"\n=== 修正建議 ===")
    print("1. 檢查looks_like_player_area方法是否正確判斷")
    print("2. 可能需要進一步降低信心度閾值")
    print("3. 考慮保留所有OCR結果，在後處理階段再篩選")

if __name__ == "__main__":
    compare_results()