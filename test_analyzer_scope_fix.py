#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""測試修復後的分析器作用域問題"""

import sys
import os

# 設置控制台編碼
if sys.platform == "win32":
    os.system('chcp 65001 > nul')

def test_analyzer_access():
    """測試分析器存取是否正確"""
    print("測試分析器存取修復...")
    
    try:
        from integration_test import IntegrationTester
        from screen_monitor import ScreenMonitor
        from config import GEMINI_API_KEY, SELLING_ITEMS
        
        # 創建測試用的ROI座標
        roi_coordinates = {
            "x": 100,
            "y": 100,
            "width": 400,
            "height": 200
        }
        
        # 創建整合測試器
        tester = IntegrationTester()
        
        # 測試Gemini分析器（如果API Key可用）
        if GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
            print("測試 Gemini 分析器存取...")
            analyzer = tester.create_analyzer("gemini")
            if analyzer is not None:
                monitor = ScreenMonitor(roi_coordinates, analyzer, save_screenshots=False, show_alerts=False)
                
                # 檢查monitor.analyzer是否可以正常存取
                assert hasattr(monitor, 'analyzer'), "ScreenMonitor缺少analyzer屬性"
                assert monitor.analyzer is analyzer, "analyzer引用不正確"
                assert hasattr(monitor.analyzer, 'extract_json_from_response'), "Gemini分析器缺少extract_json_from_response方法"
                
                print("OK Gemini 分析器存取正常")
            else:
                print("SKIP Gemini 分析器創建失敗")
        else:
            print("SKIP Gemini API Key未設置")
        
        # 測試OCR分析器
        print("測試 OCR 分析器存取...")
        try:
            analyzer = tester.create_analyzer("ocr")
            if analyzer is not None:
                monitor = ScreenMonitor(roi_coordinates, analyzer, save_screenshots=False, show_alerts=False)
                
                # 檢查monitor.analyzer是否可以正常存取
                assert hasattr(monitor, 'analyzer'), "ScreenMonitor缺少analyzer屬性"
                assert monitor.analyzer is analyzer, "analyzer引用不正確"
                assert not hasattr(monitor.analyzer, 'extract_json_from_response'), "OCR分析器不應該有extract_json_from_response方法"
                
                print("OK OCR 分析器存取正常")
            else:
                print("SKIP OCR 分析器創建失敗")
        except ImportError:
            print("SKIP OCR 依賴未安裝")
        
        return True
        
    except Exception as e:
        print(f"FAIL 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_run_single_test_method():
    """測試 run_single_test 方法的語法正確性"""
    print("測試 run_single_test 方法語法...")
    
    try:
        from integration_test import IntegrationTester
        import inspect
        
        # 檢查方法是否存在
        tester = IntegrationTester()
        assert hasattr(tester, 'run_single_test'), "缺少run_single_test方法"
        
        # 檢查方法簽名
        method = getattr(tester, 'run_single_test')
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())
        
        assert 'test_id' in params, "run_single_test缺少test_id參數"
        assert 'monitor' in params, "run_single_test缺少monitor參數"
        
        print("OK run_single_test 方法簽名正確")
        
        # 檢查方法代碼中是否還有裸露的analyzer引用
        source = inspect.getsource(method)
        
        # 檢查是否有未修復的analyzer引用（不應該有 "analyzer." 但可以有 "monitor.analyzer."）
        lines = source.split('\n')
        problematic_lines = []
        
        for i, line in enumerate(lines):
            # 檢查是否有直接使用analyzer的情況（排除monitor.analyzer的情況）
            if 'analyzer' in line and 'monitor.analyzer' not in line and 'hasattr(' not in line.replace('monitor.analyzer', ''):
                # 排除註解和字符串中的analyzer
                if not line.strip().startswith('#') and not line.strip().startswith('"""'):
                    problematic_lines.append((i+1, line.strip()))
        
        if problematic_lines:
            print("WARN 發現可能的問題行：")
            for line_num, content in problematic_lines:
                print(f"  第{line_num}行: {content}")
        else:
            print("OK 沒有發現裸露的analyzer引用")
        
        return True
        
    except Exception as e:
        print(f"FAIL 測試失敗: {e}")
        return False

def main():
    """主測試程式"""
    print("分析器作用域修復驗證")
    print("=" * 40)
    
    tests = [
        ("分析器存取測試", test_analyzer_access),
        ("run_single_test方法語法測試", test_run_single_test_method)
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
        print("SUCCESS 分析器作用域修復成功！")
        print("\n現在可以重新執行整合測試：")
        print("python integration_test.py")
    else:
        print("WARNING 部分測試失敗，可能需要進一步檢查")

if __name__ == "__main__":
    main()