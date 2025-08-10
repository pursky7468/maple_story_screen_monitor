#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""測試integration_test修復後是否可以正常導入和初始化"""

import sys
import os

# 設置控制台編碼
if sys.platform == "win32":
    os.system('chcp 65001 > nul')

def test_integration_imports():
    """測試導入是否正常"""
    try:
        from integration_test import IntegrationTester
        from screen_monitor import ScreenMonitor
        from gemini_analyzer import GeminiAnalyzer
        from config import GEMINI_API_KEY, SELLING_ITEMS
        print("OK 所有必要的模組導入成功")
        return True
    except ImportError as e:
        print(f"FAIL 模組導入失敗: {e}")
        return False

def test_analyzer_creation():
    """測試分析器創建"""
    try:
        from gemini_analyzer import GeminiAnalyzer
        from config import GEMINI_API_KEY, SELLING_ITEMS
        
        if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
            print("WARN Gemini API Key未設置，跳過分析器測試")
            return True
        
        analyzer = GeminiAnalyzer(GEMINI_API_KEY, SELLING_ITEMS)
        print("OK GeminiAnalyzer創建成功")
        return True
    except Exception as e:
        print(f"FAIL 分析器創建失敗: {e}")
        return False

def test_screen_monitor_constructor():
    """測試ScreenMonitor建構子"""
    try:
        from screen_monitor import ScreenMonitor
        from gemini_analyzer import GeminiAnalyzer
        from config import GEMINI_API_KEY, SELLING_ITEMS
        
        if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
            print("WARN Gemini API Key未設置，使用模擬分析器")
            # 創建一個簡單的模擬分析器
            class MockAnalyzer:
                def __init__(self):
                    pass
                def analyze(self, image):
                    from text_analyzer import AnalysisResult
                    return AnalysisResult(
                        full_text="模擬文字",
                        is_match=False,
                        analysis_method="MockAnalyzer"
                    ), "模擬回應"
            analyzer = MockAnalyzer()
        else:
            analyzer = GeminiAnalyzer(GEMINI_API_KEY, SELLING_ITEMS)
        
        # 測試ROI座標
        roi_coordinates = {
            "x": 100,
            "y": 100,
            "width": 400,
            "height": 200
        }
        
        # 創建ScreenMonitor實例
        monitor = ScreenMonitor(roi_coordinates, analyzer, save_screenshots=False, show_alerts=False)
        print("OK ScreenMonitor建構子使用正確")
        return True
    except Exception as e:
        print(f"FAIL ScreenMonitor建構子測試失敗: {e}")
        return False

def test_integration_tester():
    """測試IntegrationTester類別"""
    try:
        from integration_test import IntegrationTester
        
        tester = IntegrationTester()
        print("OK IntegrationTester創建成功")
        return True
    except Exception as e:
        print(f"FAIL IntegrationTester創建失敗: {e}")
        return False

def main():
    """主測試程式"""
    print("Integration Test 修復驗證")
    print("=" * 40)
    
    tests = [
        ("模組導入測試", test_integration_imports),
        ("分析器創建測試", test_analyzer_creation),
        ("ScreenMonitor建構子測試", test_screen_monitor_constructor),
        ("IntegrationTester測試", test_integration_tester)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n執行 {test_name}...")
        try:
            if test_func():
                passed += 1
            else:
                print(f"FAIL {test_name} 失敗")
        except Exception as e:
            print(f"ERROR {test_name} 發生例外: {e}")
    
    print(f"\n{'='*40}")
    print(f"測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("SUCCESS 所有測試通過！integration_test.py 修復成功")
    else:
        print("WARNING 部分測試失敗，請檢查相關問題")

if __name__ == "__main__":
    main()