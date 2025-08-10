#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""測試合併功能集成"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# 設置控制台編碼
if sys.platform == "win32":
    os.system('chcp 65001 > nul')

def test_real_time_merger():
    """測試實時合併器"""
    print("測試實時合併器...")
    
    try:
        from real_time_merger import RealTimeMerger
        from text_analyzer import AnalysisResult
        from PIL import Image
        import numpy as np
        
        # 創建臨時測試資料夾
        temp_dir = tempfile.mkdtemp(prefix="test_merger_")
        
        try:
            # 創建合併器
            merger = RealTimeMerger(temp_dir)
            
            # 創建測試圖片
            test_image = Image.new('RGB', (400, 100), 'white')
            from PIL import ImageDraw
            draw = ImageDraw.Draw(test_image)
            draw.text((10, 30), "測試內容：CHO123: 收購披風幸運60%", fill='black')
            
            # 保存測試圖片
            screenshot_path = os.path.join(temp_dir, "test_001_screenshot.png")
            test_image.save(screenshot_path)
            
            # 創建測試分析結果
            result = AnalysisResult(
                full_text="CHO123: 收購披風幸運60%卷軸，價格好議價",
                is_match=True,
                player_name="TestPlayer",
                channel_number="CHO123",
                matched_items=[{
                    "item_name": "披風幸運60%",
                    "keywords_found": ["收購", "披風幸運60%"]
                }],
                matched_keywords=["收購", "披風幸運60%"],
                confidence=0.85,
                analysis_method="TestAnalyzer"
            )
            
            # 添加測試結果
            success = merger.add_test_result(1, screenshot_path, result.to_dict(), None)
            assert success, "添加測試結果應該成功"
            
            # 檢查文件是否創建
            combined_file = Path(temp_dir) / "combined_results.json"
            assert combined_file.exists(), "應該創建combined_results.json"
            
            # 生成HTML查看器
            merger.generate_quick_html()
            html_file = Path(temp_dir) / "quick_view.html"
            assert html_file.exists(), "應該創建quick_view.html"
            
            # 檢查HTML文件內容
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
                assert "測試 #001" in html_content, "HTML應該包含測試信息"
                assert "找到匹配" in html_content, "HTML應該顯示匹配狀態"
                assert "data:image/png;base64," in html_content, "HTML應該包含base64圖片"
            
            print("OK 實時合併器功能正常")
            print(f"  - 合併文件: {combined_file}")
            print(f"  - HTML查看器: {html_file}")
            
            return True
            
        finally:
            # 清理臨時資料夾
            shutil.rmtree(temp_dir)
            
    except Exception as e:
        print(f"FAIL 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_test_merger():
    """測試整合測試中的合併功能"""
    print("測試整合測試合併集成...")
    
    try:
        from integration_test import IntegrationTester
        
        # 檢查是否正確導入了合併功能
        tester = IntegrationTester()
        
        # 檢查屬性是否存在
        assert hasattr(tester, 'real_time_merger'), "應該有real_time_merger屬性"
        
        # 檢查方法是否存在
        assert hasattr(tester, 'setup_test_environment'), "應該有setup_test_environment方法"
        
        print("OK 整合測試合併集成檢查通過")
        return True
        
    except Exception as e:
        print(f"FAIL 測試失敗: {e}")
        return False

def test_merger_tool():
    """測試合併工具"""
    print("測試測試結果合併工具...")
    
    try:
        from test_results_merger import TestResultsMerger
        
        # 檢查類是否可以正常創建
        temp_dir = tempfile.mkdtemp(prefix="test_merger_tool_")
        
        try:
            merger = TestResultsMerger(temp_dir)
            assert hasattr(merger, 'load_test_data'), "應該有load_test_data方法"
            assert hasattr(merger, 'generate_html_report'), "應該有generate_html_report方法"
            assert hasattr(merger, 'generate_json_report'), "應該有generate_json_report方法"
            
            print("OK 合併工具類檢查通過")
            return True
            
        finally:
            shutil.rmtree(temp_dir)
            
    except Exception as e:
        print(f"FAIL 測試失敗: {e}")
        return False

def main():
    """主測試程式"""
    print("測試結果合併功能驗證")
    print("=" * 40)
    
    tests = [
        ("實時合併器測試", test_real_time_merger),
        ("整合測試合併集成", test_integration_test_merger),
        ("合併工具測試", test_merger_tool)
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
        print("SUCCESS 合併功能集成成功！")
        print("\n功能說明：")
        print("1. ✓ 實時合併器：測試過程中自動合併結果")
        print("2. ✓ 快速查看器：生成HTML文件方便調試") 
        print("3. ✓ 合併JSON：包含base64圖片的完整數據")
        print("4. ✓ 後處理工具：處理現有測試結果")
        print("\n使用方式：")
        print("- python integration_test.py  # 自動生成quick_view.html")
        print("- python test_results_merger.py  # 處理現有測試結果")
    else:
        print("WARNING 部分測試失敗")

if __name__ == "__main__":
    main()