#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""測試JSON序列化修復"""

import sys
import os
import json
import tempfile

# 設置控制台編碼
if sys.platform == "win32":
    os.system('chcp 65001 > nul')

def test_convert_function():
    """測試convert_to_json_serializable函數"""
    print("測試JSON序列化轉換函數...")
    
    try:
        from screen_monitor import convert_to_json_serializable
        import numpy as np
        
        # 測試各種numpy類型
        test_data = {
            "int32": np.int32(42),
            "int64": np.int64(123456789),
            "float32": np.float32(3.14),
            "float64": np.float64(2.718281828),
            "array": np.array([1, 2, 3, 4, 5]),
            "nested_dict": {
                "inner_int": np.int32(999),
                "inner_list": [np.float32(1.1), np.float32(2.2)]
            },
            "normal_string": "這是正常的字符串",
            "normal_int": 42,
            "normal_float": 3.14159
        }
        
        # 轉換數據
        converted_data = convert_to_json_serializable(test_data)
        
        # 嘗試JSON序列化
        json_string = json.dumps(converted_data, ensure_ascii=False, indent=2)
        
        # 確認轉換結果
        assert isinstance(converted_data["int32"], int), "int32應該被轉換為int"
        assert isinstance(converted_data["int64"], int), "int64應該被轉換為int"
        assert isinstance(converted_data["float32"], float), "float32應該被轉換為float"
        assert isinstance(converted_data["float64"], float), "float64應該被轉換為float"
        assert isinstance(converted_data["array"], list), "ndarray應該被轉換為list"
        
        print("OK JSON序列化轉換函數工作正常")
        print(f"轉換後的數據類型正確：")
        for key, value in converted_data.items():
            if key != "nested_dict":
                print(f"  - {key}: {type(value).__name__}")
        
        return True
        
    except Exception as e:
        print(f"FAIL 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_analysis_result_serialization():
    """測試AnalysisResult的JSON序列化"""
    print("測試AnalysisResult序列化...")
    
    try:
        from text_analyzer import AnalysisResult
        from screen_monitor import convert_to_json_serializable
        import numpy as np
        
        # 創建包含numpy類型的分析結果
        result = AnalysisResult(
            full_text="測試文字內容",
            is_match=True,
            confidence=np.float32(0.85),  # 使用numpy類型
            analysis_method="TestAnalyzer"
        )
        
        # 模擬OCR可能返回的數據
        result.matched_items = [{
            "item_name": "測試商品",
            "keywords_found": ["關鍵字1", "關鍵字2"],
            "confidence": np.float64(0.95),  # numpy類型
            "position": np.array([100, 200, 50, 25])  # numpy array
        }]
        
        # 轉換為字典
        result_dict = result.to_dict()
        
        # 使用轉換函數
        converted_dict = convert_to_json_serializable(result_dict)
        
        # 嘗試JSON序列化
        json_string = json.dumps(converted_dict, ensure_ascii=False, indent=2)
        
        # 驗證能夠重新解析
        parsed_data = json.loads(json_string)
        
        print("OK AnalysisResult JSON序列化成功")
        print(f"序列化後的JSON長度: {len(json_string)} 字符")
        
        return True
        
    except Exception as e:
        print(f"FAIL 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_screen_monitor_save():
    """測試ScreenMonitor保存功能"""
    print("測試ScreenMonitor保存功能...")
    
    try:
        from screen_monitor import convert_to_json_serializable
        from text_analyzer import AnalysisResult
        import tempfile
        import numpy as np
        
        # 直接測試序列化功能
        result = AnalysisResult(
            full_text="測試內容",
            is_match=True,
            confidence=np.float32(0.85),
            analysis_method="MockAnalyzer"
        )
        
        # 包含numpy類型的raw_response
        raw_response = {
            "confidence": np.float64(0.95),
            "positions": np.array([[10, 20], [30, 40]]),
            "text_regions": [
                {
                    "text": "測試文字",
                    "confidence": np.float32(0.8),
                    "bbox": np.array([100, 200, 50, 25])
                }
            ]
        }
        
        # 模擬save_analysis_result的操作
        analysis_data = {
            "timestamp": "20250809_210000",
            "analysis_method": result.analysis_method,
            "result": convert_to_json_serializable(result.to_dict()),
            "raw_response": convert_to_json_serializable(raw_response)
        }
        
        # 嘗試JSON序列化
        json_string = json.dumps(analysis_data, ensure_ascii=False, indent=2)
        
        # 驗證能夠重新解析
        parsed_data = json.loads(json_string)
        
        # 檢查關鍵字段
        assert "result" in parsed_data, "應該包含result欄位"
        assert "raw_response" in parsed_data, "應該包含raw_response欄位"
        assert isinstance(parsed_data["raw_response"]["confidence"], float), "confidence應該是float類型"
        assert isinstance(parsed_data["raw_response"]["positions"], list), "positions應該是list類型"
        
        print("OK ScreenMonitor序列化功能正常")
        print(f"序列化的JSON長度: {len(json_string)} 字符")
        
        return True
        
    except Exception as e:
        print(f"FAIL 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主測試程式"""
    print("JSON序列化修復驗證")
    print("=" * 40)
    
    tests = [
        ("JSON轉換函數測試", test_convert_function),
        ("AnalysisResult序列化測試", test_analysis_result_serialization),
        ("ScreenMonitor保存測試", test_screen_monitor_save)
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
        print("SUCCESS JSON序列化修復成功！")
        print("\n修復摘要：")
        print("1. ✓ 新增convert_to_json_serializable轉換函數")
        print("2. ✓ 修復screen_monitor.py的JSON序列化")
        print("3. ✓ 修復integration_test.py的JSON序列化")
        print("4. ✓ 修復mock_test.py的JSON序列化")
        print("\n現在OCR分析器的結果可以正常保存了！")
    else:
        print("WARNING 部分測試失敗，請檢查相關問題")

if __name__ == "__main__":
    main()