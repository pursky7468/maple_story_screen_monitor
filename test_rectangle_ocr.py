"""
矩形框OCR分析器測試腳本
"""

import sys
import os
from config import *
from ocr_analyzer import RectangleBasedOCRAnalyzer

def test_rectangle_ocr_creation():
    """測試矩形框OCR分析器創建"""
    print("測試矩形框OCR分析器創建...")
    
    try:
        # 創建分析器
        analyzer = RectangleBasedOCRAnalyzer(
            SELLING_ITEMS, 
            detection_config=RECTANGLE_DETECTION_CONFIG
        )
        
        print("✅ 矩形框OCR分析器創建成功")
        print(f"   - 分析器類型: {analyzer.__class__.__name__}")
        print(f"   - 策略類型: {analyzer.strategy_type}")
        print(f"   - 支援的物品: {len(SELLING_ITEMS)} 項")
        
        # 啟用調試模式測試
        if OCR_DEBUG_CONFIG.get("ENABLE_RECTANGLE_DEBUG", False):
            analyzer.set_debug_mode(
                True, 
                OCR_DEBUG_CONFIG.get("DEBUG_OUTPUT_DIR", "rectangle_debug")
            )
            print("   - 調試模式: 已啟用")
        else:
            print("   - 調試模式: 已關閉")
        
        return True
        
    except Exception as e:
        print(f"❌ 創建失敗: {e}")
        return False

def test_template_pattern():
    """測試Template Pattern實現"""
    print("\n測試Template Pattern實現...")
    
    try:
        from text_analyzer import BaseOCRAnalyzer
        print("✅ BaseOCRAnalyzer 模板基類導入成功")
        
        # 驗證抽象方法
        abstract_methods = BaseOCRAnalyzer.__abstractmethods__
        print(f"   - 抽象方法: {list(abstract_methods)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Template Pattern測試失敗: {e}")
        return False

def test_configuration():
    """測試配置參數"""
    print("\n測試配置參數...")
    
    try:
        print("✅ 矩形框檢測配置:")
        for key, value in RECTANGLE_DETECTION_CONFIG.items():
            print(f"   - {key}: {value}")
        
        print("✅ 調試配置:")
        for key, value in OCR_DEBUG_CONFIG.items():
            print(f"   - {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("=" * 60)
    print("矩形框OCR分析器測試")
    print("=" * 60)
    
    tests = [
        test_rectangle_ocr_creation,
        test_template_pattern,
        test_configuration
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    print("\n" + "=" * 60)
    print("測試結果總結")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    for i, result in enumerate(results, 1):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"測試 {i}: {status}")
    
    print(f"\n總結: {passed}/{total} 測試通過")
    
    if passed == total:
        print("🎉 所有測試通過！矩形框OCR分析器準備就緒。")
        print("\n下一步:")
        print("1. 執行 python integration_test.py")
        print("2. 選擇選項 3 (矩形框OCR)")
        print("3. 如需調試，在 config.py 中設置 ENABLE_RECTANGLE_DEBUG=True")
    else:
        print("⚠️ 部分測試失敗，請檢查錯誤訊息。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)