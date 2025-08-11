#!/usr/bin/env python3
"""
測試改進後的OCR分析器
"""

import os
from PIL import Image
from ocr_analyzer import OCRAnalyzer
from config import SELLING_ITEMS

def test_improved_ocr():
    """測試改進後的OCR功能"""
    print("=== 測試改進後的OCR分析器 ===")
    
    try:
        # 初始化OCR分析器
        analyzer = OCRAnalyzer(SELLING_ITEMS)
        print("[OK] OCR分析器初始化成功")
        
        # 尋找測試截圖
        test_folders = [f for f in os.listdir('.') if f.startswith('integration_test_')]
        if not test_folders:
            print("[ERROR] 未找到測試資料夾")
            return
        
        latest_folder = max(test_folders)
        screenshots = []
        for file in os.listdir(latest_folder):
            if file.endswith('_screenshot.png'):
                screenshots.append(os.path.join(latest_folder, file))
        
        if not screenshots:
            print("[ERROR] 未找到截圖檔案")
            return
        
        print(f"[INFO] 測試資料夾: {latest_folder}")
        print(f"[INFO] 找到 {len(screenshots)} 個截圖")
        
        # 測試前2個截圖
        for i, screenshot_path in enumerate(screenshots[:2], 1):
            print(f"\n=== 測試截圖 {i}: {os.path.basename(screenshot_path)} ===")
            
            # 讀取圖片
            image = Image.open(screenshot_path)
            print(f"[OK] 圖片大小: {image.size}")
            
            # OCR分析
            result, raw_response = analyzer.analyze(image)
            
            print(f"[結果] 分析方法: {result.analysis_method}")
            print(f"[結果] 完整文字: '{result.full_text}'")
            print(f"[結果] 玩家名稱: '{result.player_name}'")
            print(f"[結果] 頻道編號: '{result.channel_number}'")
            print(f"[結果] 信心度: {result.confidence:.3f}")
            print(f"[結果] 是否匹配: {result.is_match}")
            
            if result.matched_items:
                print(f"[結果] 匹配物品: {result.matched_items}")
            if result.matched_keywords:
                print(f"[結果] 匹配關鍵字: {result.matched_keywords}")
            
            # 顯示原始OCR結果
            if isinstance(raw_response, list) and raw_response:
                print("[原始OCR] 識別結果:")
                for j, item in enumerate(raw_response):
                    if isinstance(item, dict):
                        text = item.get('text', '')
                        conf = item.get('confidence', 0)
                        print(f"  {j+1}. '{text}' (信心度: {conf:.3f})")
            else:
                print(f"[原始OCR] 沒有識別結果")
    
    except Exception as e:
        print(f"[ERROR] 測試失敗: {e}")
        import traceback
        traceback.print_exc()

def test_specific_case():
    """測試特定的識別案例"""
    print("\n=== 測試特定玩家名稱提取 ===")
    
    try:
        analyzer = OCRAnalyzer(SELLING_ITEMS)
        
        # 模擬實際OCR結果
        mock_ocr_result = [
            {
                'text': 'hihi5217',
                'confidence': 0.996,
                'bbox': [[10, 5], [80, 5], [80, 20], [10, 20]]
            },
            {
                'text': 'TH1E收=',
                'confidence': 0.355,
                'bbox': [[85, 5], [140, 5], [140, 20], [85, 20]]
            },
            {
                'text': '披敏收購',
                'confidence': 0.65,
                'bbox': [[145, 5], [200, 5], [200, 20], [145, 20]]
            }
        ]
        
        # 測試玩家名稱提取
        full_text = ' '.join([item['text'] for item in mock_ocr_result])
        player_name = analyzer.extract_player_name_from_ocr(mock_ocr_result, full_text)
        
        print(f"完整文字: '{full_text}'")
        print(f"提取的玩家名稱: '{player_name}'")
        
        # 測試個別方法
        for item in mock_ocr_result:
            text = item['text']
            is_likely = analyzer.is_likely_player_name(text)
            is_valid = analyzer.validate_player_name_strict(text)
            print(f"'{text}' -> 可能是玩家名: {is_likely}, 嚴格驗證: {is_valid}")
        
        # 測試完整解析
        result = analyzer.parse_result(mock_ocr_result)
        print(f"\n完整解析結果:")
        print(f"  玩家名稱: '{result.player_name}'")
        print(f"  是否匹配: {result.is_match}")
        print(f"  匹配的關鍵字: {result.matched_keywords}")
        
    except Exception as e:
        print(f"[ERROR] 特定測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_improved_ocr()
    test_specific_case()
    
    print("\n=== 改進總結 ===")
    print("1. 降低OCR信心度閾值從0.5到0.3")
    print("2. 實現了基於信心度的玩家名稱提取")
    print("3. 增加了無冒號格式的玩家名稱識別")
    print("4. 改進了玩家名稱驗證邏輯")
    print("5. 現在應該能正確識別 'hihi5217' 這樣的玩家名稱")