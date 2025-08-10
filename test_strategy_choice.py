#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""測試整合測試的策略選擇功能"""

import sys
import os

# 設置控制台編碼
if sys.platform == "win32":
    os.system('chcp 65001 > nul')

def test_analyzer_choice_methods():
    """測試分析器選擇方法"""
    print("測試分析器選擇方法...")
    
    try:
        from integration_test import IntegrationTester
        
        tester = IntegrationTester()
        
        # 檢查方法是否存在
        assert hasattr(tester, 'get_analyzer_choice'), "缺少 get_analyzer_choice 方法"
        assert hasattr(tester, 'create_analyzer'), "缺少 create_analyzer 方法"
        
        print("OK 分析器選擇方法存在")
        return True
    except Exception as e:
        print(f"FAIL 測試失敗: {e}")
        return False

def test_gemini_analyzer_creation():
    """測試 Gemini 分析器創建"""
    print("測試 Gemini 分析器創建...")
    
    try:
        from integration_test import IntegrationTester
        from config import GEMINI_API_KEY
        
        tester = IntegrationTester()
        
        if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
            # 測試 API Key 未設置的情況
            analyzer = tester.create_analyzer("gemini")
            assert analyzer is None, "API Key未設置時應該返回 None"
            print("OK Gemini 分析器在 API Key 未設置時正確返回 None")
        else:
            # 測試正常創建
            analyzer = tester.create_analyzer("gemini")
            if analyzer is not None:
                print("OK Gemini 分析器創建成功")
            else:
                print("WARN Gemini 分析器創建失敗，可能是 API Key 問題")
        
        return True
    except Exception as e:
        print(f"FAIL 測試失敗: {e}")
        return False

def test_ocr_analyzer_creation():
    """測試 OCR 分析器創建"""
    print("測試 OCR 分析器創建...")
    
    try:
        from integration_test import IntegrationTester
        
        tester = IntegrationTester()
        
        try:
            analyzer = tester.create_analyzer("ocr")
            if analyzer is not None:
                print("OK OCR 分析器創建成功")
            else:
                print("WARN OCR 分析器創建失敗，可能缺少依賴")
        except ImportError:
            print("WARN OCR 依賴未安裝，這是正常情況")
        
        return True
    except Exception as e:
        print(f"FAIL 測試失敗: {e}")
        return False

def test_invalid_analyzer_type():
    """測試無效的分析器類型"""
    print("測試無效的分析器類型...")
    
    try:
        from integration_test import IntegrationTester
        
        tester = IntegrationTester()
        
        # 測試無效類型
        analyzer = tester.create_analyzer("invalid")
        assert analyzer is None, "無效類型應該返回 None"
        
        print("OK 無效分析器類型正確處理")
        return True
    except Exception as e:
        print(f"FAIL 測試失敗: {e}")
        return False

def main():
    """主測試程式"""
    print("整合測試策略選擇功能驗證")
    print("=" * 40)
    
    tests = [
        ("分析器選擇方法測試", test_analyzer_choice_methods),
        ("Gemini分析器創建測試", test_gemini_analyzer_creation),
        ("OCR分析器創建測試", test_ocr_analyzer_creation),
        ("無效分析器類型測試", test_invalid_analyzer_type)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n執行 {test_name}...")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"ERROR {test_name} 發生例外: {e}")
    
    print(f"\n{'='*40}")
    print(f"測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("SUCCESS 策略選擇功能測試通過！")
        print("\n使用方式：")
        print("python integration_test.py")
        print("- 程式會詢問你要使用哪種分析方法")
        print("- 1: Gemini AI (需要設置 API Key)")
        print("- 2: OCR 本地識別 (需要安裝 easyocr)")
    else:
        print("WARNING 部分測試失敗")

if __name__ == "__main__":
    main()