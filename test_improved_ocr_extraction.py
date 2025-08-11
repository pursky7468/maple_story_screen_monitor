#!/usr/bin/env python3
"""
測試改進後的OCR文字提取功能
"""

import os
from PIL import Image
from ocr_analyzer import OCRAnalyzer
from config import SELLING_ITEMS

def test_specific_image():
    """測試特定的問題圖片"""
    print("=== 測試改進後的OCR文字提取 ===")
    
    # 測試目標圖片
    test_image_path = r"C:\Users\User\Desktop\螢幕監控程式\monitoring_session_20250810_085346\monitor_001_20250810_085346_670.png"
    
    if not os.path.exists(test_image_path):
        print("[ERROR] 測試圖片不存在")
        return
    
    # 載入圖片
    image = Image.open(test_image_path)
    print(f"[INFO] 測試圖片: {os.path.basename(test_image_path)}")
    print(f"[INFO] 圖片尺寸: {image.size}")
    
    # 創建OCR分析器
    try:
        analyzer = OCRAnalyzer(SELLING_ITEMS)
        print("[OK] OCR分析器創建成功")
    except Exception as e:
        print(f"[ERROR] OCR分析器創建失敗: {e}")
        return
    
    # 進行分析
    print("\n--- 進行OCR分析 ---")
    result, raw_response = analyzer.analyze(image)
    
    print(f"[結果] 完整文字: '{result.full_text}'")
    print(f"[結果] 玩家名稱: '{result.player_name}'")
    print(f"[結果] 頻道編號: '{result.channel_number}'")
    print(f"[結果] 信心度: {result.confidence:.3f}")
    print(f"[結果] 是否匹配: {result.is_match}")
    print(f"[結果] 匹配物品: {len(result.matched_items)} 個")
    
    if result.matched_items:
        for item in result.matched_items:
            print(f"  - {item['item_name']}: {item['keywords_found']}")
    
    # 顯示原始OCR結果
    print(f"\n--- 原始OCR結果 ---")
    if isinstance(raw_response, list):
        print(f"識別到 {len(raw_response)} 個文字區域:")
        for i, item in enumerate(raw_response, 1):
            if isinstance(item, dict):
                text = item.get('text', '')
                conf = item.get('confidence', 0)
                bbox = item.get('bbox', [])
                if bbox:
                    left_x = bbox[0][0] if bbox else 0
                    print(f"  {i}. '{text}' (信心度: {conf:.3f}, 左邊距: {left_x:.0f}px)")
                else:
                    print(f"  {i}. '{text}' (信心度: {conf:.3f})")
    
    # 測試玩家名稱提取的各個步驟
    print(f"\n--- 玩家名稱提取詳細分析 ---")
    if isinstance(raw_response, list):
        print("候選玩家名稱:")
        for i, item in enumerate(raw_response, 1):
            text = item.get('text', '').strip()
            conf = item.get('confidence', 0)
            bbox = item.get('bbox', [])
            left_x = bbox[0][0] if bbox else 0
            
            # 測試是否可能是玩家區域
            is_player_area = analyzer.looks_like_player_area(bbox, text)
            
            # 測試清理後的文字
            cleaned_text = analyzer.clean_ocr_text(text)
            
            # 測試是否像玩家名稱
            is_likely_player = analyzer.is_likely_player_name(cleaned_text)
            
            print(f"  {i}. 原文: '{text}' -> 清理後: '{cleaned_text}'")
            print(f"      位置: {left_x:.0f}px, 可能玩家區域: {is_player_area}")
            print(f"      信心度: {conf:.3f}, 像玩家名稱: {is_likely_player}")
            
            if left_x < 250 and is_likely_player:
                print(f"      >>> 這是玩家名稱候選！")
    
    # 期望的結果
    print(f"\n--- 期望結果對比 ---")
    expected_full_text = "乂煞氣a澤神乂 CH2245 : 收幸運母礦12:1/螺絲釘25:1/賣德古拉(80賊手)+10攻6屬430雪"
    expected_player_name = "乂煞氣a澤神乂"
    expected_channel = "CH2245"
    
    print(f"期望完整文字: '{expected_full_text}'")
    print(f"期望玩家名稱: '{expected_player_name}'")
    print(f"期望頻道編號: '{expected_channel}'")
    
    print(f"\n結果比較:")
    print(f"  完整文字匹配: {'✓' if expected_player_name in result.full_text else '✗'}")
    print(f"  玩家名稱正確: {'✓' if result.player_name == expected_player_name else '✗'}")
    print(f"  頻道編號正確: {'✓' if result.channel_number == expected_channel else '✗'}")

def test_multiple_images():
    """測試多張圖片"""
    session_folder = r"C:\Users\User\Desktop\螢幕監控程式\monitoring_session_20250810_085346"
    
    if not os.path.exists(session_folder):
        print("[ERROR] 測試資料夾不存在")
        return
    
    print(f"\n=== 測試多張圖片 ===")
    
    # 尋找前5張截圖進行測試
    screenshots = []
    for i in range(1, 6):
        pattern = f"monitor_{i:03d}_*.png"
        import glob
        matches = glob.glob(os.path.join(session_folder, pattern))
        if matches:
            screenshots.extend(matches[:1])  # 每個編號取一張
    
    if not screenshots:
        print("[WARNING] 沒有找到測試截圖")
        return
    
    analyzer = OCRAnalyzer(SELLING_ITEMS)
    
    print(f"找到 {len(screenshots)} 張測試截圖")
    
    for i, screenshot_path in enumerate(screenshots[:3], 1):  # 只測試前3張
        print(f"\n--- 測試截圖 {i}: {os.path.basename(screenshot_path)} ---")
        
        image = Image.open(screenshot_path)
        result, raw_response = analyzer.analyze(image)
        
        print(f"  玩家名稱: '{result.player_name}'")
        print(f"  頻道編號: '{result.channel_number}'")
        print(f"  完整文字: '{result.full_text[:50]}...'")
        print(f"  是否匹配: {result.is_match}")
        
        # 檢查是否包含中文玩家名稱
        import re
        has_chinese_player = bool(re.search(r'[\u4e00-\u9fff]{2,}', result.player_name))
        print(f"  包含中文玩家名: {has_chinese_player}")

if __name__ == "__main__":
    test_specific_image()
    test_multiple_images()
    
    print(f"\n=== 改進總結 ===")
    print("1. 降低玩家名稱區域的信心度閾值到0.1")
    print("2. 基於位置和內容特徵識別玩家名稱")
    print("3. 清理和修正OCR識別錯誤")
    print("4. 多層次的玩家名稱提取邏輯")
    print("5. 現在應該能正確識別 '乂煞氣a澤神乂' 這樣的玩家名稱")