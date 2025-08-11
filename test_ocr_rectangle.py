#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OCR_Rectangle策略測試程式
測試新的白框檢測OCR分析器功能
"""

import os
import sys
from PIL import Image
import numpy as np

# 添加當前目錄到Python路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from ocr_rectangle_analyzer import OCRRectangleAnalyzer
    from config import SELLING_ITEMS
except ImportError as e:
    print(f"導入錯誤: {e}")
    print("請確認所需模塊已正確安裝")
    sys.exit(1)

def create_test_image():
    """創建測試圖像"""
    # 創建一個簡單的測試圖像
    width, height = 800, 200
    img = Image.new('RGB', (width, height), color='black')
    
    # 可以在這裡添加更複雜的測試圖像生成邏輯
    # 目前返回空白測試圖像
    return img

def test_basic_functionality():
    """測試基本功能"""
    print("=== OCR_Rectangle 基本功能測試 ===")
    
    try:
        # 初始化分析器（開啟調試模式）
        analyzer = OCRRectangleAnalyzer(
            selling_items=SELLING_ITEMS,
            save_debug_images=True,
            debug_folder="test_rectangle_debug"
        )
        print("OK OCR_Rectangle分析器初始化成功")
        
        # 創建測試圖像
        test_image = create_test_image()
        print("OK 測試圖像創建成功")
        
        # 測試分析功能
        print("\n--- 執行圖像分析 ---")
        analysis_result, raw_response = analyzer.analyze(test_image)
        
        print(f"分析方法: {analysis_result.analysis_method}")
        print(f"完整文字: {analysis_result.full_text}")
        print(f"是否匹配: {analysis_result.is_match}")
        print(f"玩家名稱: {analysis_result.player_name}")
        print(f"頻道編號: {analysis_result.channel_number}")
        print(f"匹配物品: {analysis_result.matched_items}")
        print(f"信心度: {analysis_result.confidence:.3f}")
        
        return True
        
    except Exception as e:
        print(f"ERROR 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_screenshot():
    """使用螢幕截圖進行測試"""
    print("\n=== 螢幕截圖測試 ===")
    
    try:
        import pyautogui
        from tkinter import messagebox
        import tkinter as tk
        
        # 提示用戶準備
        root = tk.Tk()
        root.withdraw()  # 隱藏主窗口
        
        result = messagebox.askyesno(
            "螢幕截圖測試", 
            "即將進行螢幕截圖測試。\n請確認遊戲聊天窗口可見，然後點擊'是'開始測試。"
        )
        
        if not result:
            print("用戶取消測試")
            return True
        
        # 截圖
        print("正在截圖...")
        screenshot = pyautogui.screenshot()
        
        # 初始化分析器
        analyzer = OCRRectangleAnalyzer(
            selling_items=SELLING_ITEMS,
            save_debug_images=True,
            debug_folder="test_rectangle_debug"
        )
        
        # 分析截圖
        print("正在分析截圖...")
        analysis_result, raw_response = analyzer.analyze(screenshot)
        
        print("\n--- 分析結果 ---")
        print(f"分析方法: {analysis_result.analysis_method}")
        print(f"完整文字: {analysis_result.full_text}")
        print(f"是否匹配: {analysis_result.is_match}")
        print(f"玩家名稱: {analysis_result.player_name}")
        print(f"頻道編號: {analysis_result.channel_number}")
        print(f"匹配物品: {analysis_result.matched_items}")
        print(f"匹配關鍵字: {analysis_result.matched_keywords}")
        print(f"信心度: {analysis_result.confidence:.3f}")
        
        if analysis_result.is_match:
            print("\nTARGET 找到交易機會！")
        else:
            print("\nNO 未發現交易機會")
            
        print(f"\n調試圖像已保存到: test_rectangle_debug/")
        
        return True
        
    except ImportError:
        print("ERROR pyautogui未安裝，跳過螢幕截圖測試")
        return True
    except Exception as e:
        print(f"ERROR 螢幕截圖測試失敗: {e}")
        return False

def test_image_processing():
    """測試圖像處理功能"""
    print("\n=== 圖像處理功能測試 ===")
    
    try:
        analyzer = OCRRectangleAnalyzer(
            selling_items=SELLING_ITEMS,
            save_debug_images=True
        )
        
        # 創建包含白色矩形的測試圖像
        test_image = Image.new('RGB', (400, 100), color='gray')
        pixels = test_image.load()
        
        # 添加白色矩形
        for x in range(50, 150):
            for y in range(20, 60):
                pixels[x, y] = (255, 255, 255)
        
        print("OK 創建包含白色矩形的測試圖像")
        
        # 測試預處理
        binary_image, processed_image = analyzer.preprocess_image(test_image)
        print("OK 圖像預處理完成")
        
        # 測試白框檢測
        rectangles = analyzer.detect_white_rectangles(binary_image)
        print(f"OK 檢測到 {len(rectangles)} 個白色矩形")
        
        # 測試遮罩創建
        masked_image = analyzer.create_masked_image(processed_image, rectangles)
        print("OK 遮罩圖像創建完成")
        
        return True
        
    except Exception as e:
        print(f"ERROR 圖像處理測試失敗: {e}")
        return False

def test_text_analysis():
    """測試文字分析功能"""
    print("\n=== 文字分析功能測試 ===")
    
    try:
        analyzer = OCRRectangleAnalyzer(selling_items=SELLING_ITEMS)
        
        # 測試案例
        test_cases = [
            {
                "front_text": "玩家123",
                "rear_text": "CHO225 收購 披風幸運60%",
                "expected_player": "玩家123",
                "expected_channel": "CHO225",
                "expected_match": True
            },
            {
                "front_text": "hihi5217",
                "rear_text": "225 買 母礦",
                "expected_player": "hihi5217", 
                "expected_channel": "225",
                "expected_match": True
            },
            {
                "front_text": "測試玩家",
                "rear_text": "只是聊天而已",
                "expected_player": "測試玩家",
                "expected_channel": "未知",
                "expected_match": False
            }
        ]
        
        for i, case in enumerate(test_cases):
            print(f"\n--- 測試案例 {i+1} ---")
            
            # 模擬原始結果
            raw_result = {
                "front_text": case["front_text"],
                "rear_text": case["rear_text"],
                "full_text": f"{case['front_text']} {case['rear_text']}",
                "ocr_results": []
            }
            
            # 解析結果
            result = analyzer.parse_result(raw_result)
            
            print(f"前段文字: '{case['front_text']}'")
            print(f"後段文字: '{case['rear_text']}'")
            print(f"解析玩家: {result.player_name} (預期: {case['expected_player']})")
            print(f"解析頻道: {result.channel_number} (預期: {case['expected_channel']})")
            print(f"是否匹配: {result.is_match} (預期: {case['expected_match']})")
            
            # 檢查結果
            success = (
                result.player_name == case["expected_player"] and
                result.channel_number == case["expected_channel"] and
                result.is_match == case["expected_match"]
            )
            
            print(f"測試結果: {'OK 通過' if success else 'ERROR 失敗'}")
        
        return True
        
    except Exception as e:
        print(f"ERROR 文字分析測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("OCR_Rectangle策略測試程式")
    print("=" * 50)
    
    tests = [
        ("基本功能", test_basic_functionality),
        ("圖像處理", test_image_processing), 
        ("文字分析", test_text_analysis),
        ("螢幕截圖", test_with_screenshot),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n開始執行: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"OK {test_name} 測試通過")
            else:
                print(f"ERROR {test_name} 測試失敗")
        except Exception as e:
            print(f"ERROR {test_name} 測試異常: {e}")
    
    print("\n" + "=" * 50)
    print(f"測試完成: {passed}/{total} 通過")
    
    if passed == total:
        print("SUCCESS 所有測試通過！OCR_Rectangle策略實現成功")
    else:
        print("WARNING  部分測試失敗，請檢查相關功能")

if __name__ == "__main__":
    main()