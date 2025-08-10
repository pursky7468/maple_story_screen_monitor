#!/usr/bin/env python3
"""
測試段落分割法提取玩家名稱和頻道編號
"""

import os
from PIL import Image
from ocr_analyzer import OCRAnalyzer
from config import SELLING_ITEMS

def test_segment_extraction():
    """測試段落分割法功能"""
    print("=== 測試段落分割法提取玩家名稱和頻道編號 ===")
    
    # 測試圖片路徑
    test_image_path = r"C:\Users\User\Desktop\螢幕監控程式\monitoring_session_20250810_085346\monitor_001_20250810_085346_670.png"
    
    if not os.path.exists(test_image_path):
        print("[ERROR] 測試圖片不存在")
        return
    
    # 創建OCR分析器
    try:
        analyzer = OCRAnalyzer(SELLING_ITEMS)
        print("[OK] OCR分析器創建成功")
    except Exception as e:
        print(f"[ERROR] OCR分析器創建失敗: {e}")
        return
    
    # 載入圖片並分析
    image = Image.open(test_image_path)
    print(f"[INFO] 測試圖片: {os.path.basename(test_image_path)}")
    
    # 進行完整分析
    result, raw_response = analyzer.analyze(image)
    
    print(f"\n--- OCR完整分析結果 ---")
    print(f"完整文字: '{result.full_text}'")
    print(f"玩家名稱: '{result.player_name}'")
    print(f"頻道編號: '{result.channel_number}'")
    print(f"是否匹配: {result.is_match}")
    print(f"信心度: {result.confidence:.3f}")
    
    if result.matched_items:
        print(f"匹配物品: {len(result.matched_items)} 個")
        for item in result.matched_items:
            print(f"  - {item['item_name']}: {item['keywords_found']}")
    
    # 測試段落分割的詳細過程
    print(f"\n--- 段落分割詳細分析 ---")
    full_text = result.full_text
    player_name, channel_number = analyzer.extract_player_and_channel_by_segments(full_text)
    
    print(f"原始完整文字: '{full_text}'")
    
    # 顯示分割過程
    import re
    cleaned_text = re.sub(r'\s+', ' ', full_text.strip())
    segments = cleaned_text.split(' ')
    segments = [seg.strip() for seg in segments if seg.strip()]
    
    print(f"清理後文字: '{cleaned_text}'")
    print(f"分割段落數量: {len(segments)}")
    
    for i, segment in enumerate(segments, 1):
        print(f"  段落 {i}: '{segment}'")
        if i == 1:
            print(f"    -> 玩家名稱候選: '{segment}'")
        elif i == 2:
            print(f"    -> 第二段落 (跳過): '{segment}'")
        elif i == 3:
            is_channel = analyzer.is_channel_number(segment)
            cleaned_channel = analyzer.clean_channel_text(segment)
            print(f"    -> 頻道編號候選: '{segment}' -> 清理後: '{cleaned_channel}' -> 是頻道: {is_channel}")
        else:
            print(f"    -> 廣播內容: '{segment}'")
    
    print(f"\n提取結果:")
    print(f"  玩家名稱: '{player_name}'")
    print(f"  頻道編號: '{channel_number}'")
    
    # 對比期望結果
    print(f"\n--- 結果對比 ---")
    expected_player = "乂煞氣a澤神乂"
    expected_channel = "CH2245"
    
    print(f"期望玩家名稱: '{expected_player}'")
    print(f"實際玩家名稱: '{player_name}'")
    print(f"玩家名稱正確: {'✓' if expected_player in player_name or player_name in expected_player else '✗'}")
    
    print(f"期望頻道編號: '{expected_channel}'")
    print(f"實際頻道編號: '{channel_number}'")
    print(f"頻道編號正確: {'✓' if expected_channel in channel_number or channel_number == expected_channel else '✗'}")

def test_various_text_formats():
    """測試各種文字格式的分割效果"""
    print(f"\n=== 測試各種文字格式 ===")
    
    analyzer = OCRAnalyzer(SELLING_ITEMS)
    
    test_cases = [
        "乂煞氣a澤神乂 EHzzls8 收幸運母礦12:1/螺絲釘25:1",
        "PlayerName CHO123 : 收購物品信息",  
        "玩家ABC CH2245 收購內容",
        "TestUser 999 : 賣裝備+10攻",
        "中文玩家 CH001 收購披風",
    ]
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n測試案例 {i}: '{test_text}'")
        player_name, channel_number = analyzer.extract_player_and_channel_by_segments(test_text)
        print(f"  玩家名稱: '{player_name}'")
        print(f"  頻道編號: '{channel_number}'")
        
        # 顯示分割過程
        segments = test_text.split(' ')
        segments = [seg.strip() for seg in segments if seg.strip()]
        print(f"  分割段落: {segments}")

if __name__ == "__main__":
    test_segment_extraction()
    test_various_text_formats()
    
    print(f"\n=== 段落分割法總結 ===")
    print("1. 使用空格分割文字為段落")
    print("2. 第一段落作為玩家名稱")
    print("3. 第二段落跳過（通常是無效OCR結果）")
    print("4. 第三段落檢查是否為頻道編號")
    print("5. 支援OCR錯誤修正（EHzzls8 -> CH2245）")
    print("6. 這種方法更適合OCR識別的文字結構")