#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""測試OCR改進效果"""

import os
import sys
from pathlib import Path
from PIL import Image
import json

def test_ocr_improvements():
    """測試OCR改進效果"""
    print("=== OCR改進效果測試 ===")
    print()
    
    try:
        # 導入配置和分析器
        from config import SELLING_ITEMS
        from ocr_analyzer import OCRAnalyzer
        
        # 測試兩種模式：基礎模式和增強模式
        print("正在初始化OCR分析器...")
        
        # 基礎OCR
        basic_ocr = OCRAnalyzer(SELLING_ITEMS, enable_enhancement=False)
        print("✅ 基礎OCR初始化成功")
        
        # 增強OCR
        enhanced_ocr = OCRAnalyzer(SELLING_ITEMS, enable_enhancement=True)
        print("✅ 增強OCR初始化成功")
        
        # 尋找測試圖片（特別是測試107）
        test_folders = [
            "integration_test_20250809_213714",
            "demo_test_results"
        ]
        
        test_image = None
        for folder in test_folders:
            folder_path = Path(folder)
            if folder_path.exists():
                # 優先尋找測試107的截圖
                screenshot_files = list(folder_path.glob("*107*screenshot*.png"))
                if screenshot_files:
                    test_image = screenshot_files[0]
                    print(f"找到測試107截圖: {test_image}")
                    break
                
                # 或者尋找任何截圖
                screenshot_files = list(folder_path.glob("*screenshot*.png"))
                if screenshot_files:
                    test_image = screenshot_files[0]
                    print(f"使用測試圖片: {test_image}")
                    break
        
        if not test_image:
            print("❌ 沒有找到測試圖片")
            print("請先運行 python integration_test.py 創建一些測試數據")
            return
        
        # 載入圖片
        image = Image.open(test_image)
        print(f"圖片尺寸: {image.size}")
        
        # 進行對比測試
        print(f"\n=== 對比測試結果 ===")
        
        # 基礎OCR測試
        print("\n--- 基礎OCR ---")
        basic_result, basic_raw = basic_ocr.analyze(image)
        print(f"玩家名稱: {basic_result.player_name}")
        print(f"頻道編號: {basic_result.channel_number}")
        print(f"是否匹配: {'是' if basic_result.is_match else '否'}")
        print(f"信心度: {basic_result.confidence:.2f}")
        
        # 增強OCR測試
        print("\n--- 增強OCR ---")
        enhanced_result, enhanced_raw = enhanced_ocr.analyze(image)
        print(f"玩家名稱: {enhanced_result.player_name}")
        print(f"頻道編號: {enhanced_result.channel_number}")
        print(f"是否匹配: {'是' if enhanced_result.is_match else '否'}")
        print(f"信心度: {enhanced_result.confidence:.2f}")
        
        # 對比分析
        print(f"\n=== 改進效果分析 ===")
        
        player_improved = enhanced_result.player_name != "未知" and basic_result.player_name == "未知"
        channel_improved = enhanced_result.channel_number != "未知" and basic_result.channel_number == "未知"
        
        if player_improved:
            print("✅ 玩家名稱識別: 顯著改善")
        elif enhanced_result.player_name != "未知":
            print("✅ 玩家名稱識別: 保持良好")
        else:
            print("❌ 玩家名稱識別: 仍需改善")
            
        if channel_improved:
            print("✅ 頻道編號識別: 顯著改善")
        elif enhanced_result.channel_number != "未知":
            print("✅ 頻道編號識別: 保持良好")
        else:
            print("❌ 頻道編號識別: 仍需改善")
        
        # 顯示詳細OCR結果
        if isinstance(enhanced_raw, list) and len(enhanced_raw) > 0:
            print(f"\n=== 詳細OCR識別結果 ===")
            print("增強OCR識別的文字片段：")
            for i, item in enumerate(enhanced_raw[:10]):  # 顯示前10個
                print(f"{i+1}. \"{item['text']}\" (信心度: {item['confidence']:.2f})")
        
        print(f"\n=== 調試建議 ===")
        if enhanced_result.player_name == "未知" or enhanced_result.channel_number == "未知":
            print("如果識別仍不理想，可能的原因：")
            print("• 圖片中的文字格式特殊，不在匹配模式範圍內")
            print("• OCR對特定字體或顏色的識別精度不足") 
            print("• 需要針對具體遊戲視窗進行進一步調整")
            print("\n建議：")
            print("• 檢查截圖是否包含完整的聊天消息")
            print("• 確保截圖清晰，沒有模糊或重疊")
            print("• 可以嘗試不同的截圖時機和角度")
        else:
            print("✅ OCR增強功能工作良好！")
            print("建議在整合測試時啟用增強模式以獲得更好的識別效果")
        
        # 保存測試報告
        report = {
            "test_image": str(test_image),
            "basic_ocr": {
                "player_name": basic_result.player_name,
                "channel_number": basic_result.channel_number,
                "is_match": basic_result.is_match,
                "confidence": basic_result.confidence
            },
            "enhanced_ocr": {
                "player_name": enhanced_result.player_name,
                "channel_number": enhanced_result.channel_number,
                "is_match": enhanced_result.is_match,
                "confidence": enhanced_result.confidence
            },
            "improvements": {
                "player_improved": player_improved,
                "channel_improved": channel_improved
            }
        }
        
        with open("ocr_improvement_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 測試報告已保存: ocr_improvement_report.json")
        
    except ImportError as e:
        print(f"❌ 導入錯誤: {e}")
        print("\n請確保已安裝OCR依賴:")
        print("pip install easyocr pillow numpy")
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ocr_improvements()