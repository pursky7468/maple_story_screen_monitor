#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
為現有測試結果生成HTML報告
"""

import os
import sys
import json
from pathlib import Path
from real_time_merger import RealTimeMerger

def load_test_results(test_folder):
    """從測試資料夾載入結果"""
    test_folder = Path(test_folder)
    
    if not test_folder.exists():
        print(f"錯誤：測試資料夾不存在 - {test_folder}")
        return None, None
    
    # 找所有截圖和分析文件
    screenshots = list(test_folder.glob("*_screenshot.png"))
    analysis_files = list(test_folder.glob("*_analysis.json"))
    
    print(f"發現 {len(screenshots)} 個截圖文件")
    print(f"發現 {len(analysis_files)} 個分析文件")
    
    # 組織結果
    results = []
    test_ids = set()
    
    # 從截圖文件中提取測試ID
    for screenshot in screenshots:
        parts = screenshot.stem.split('_')
        if len(parts) >= 2 and parts[0] == 'test':
            try:
                test_id = int(parts[1])
                test_ids.add(test_id)
            except ValueError:
                continue
    
    print(f"發現 {len(test_ids)} 個測試ID")
    
    # 為每個測試ID收集數據
    for test_id in sorted(test_ids):
        result_data = {
            'test_id': test_id,
            'screenshot_path': None,
            'analysis_result': None,
            'error_info': None
        }
        
        # 找對應的截圖文件
        screenshot_pattern = f"test_{test_id:03d}_*_screenshot.png"
        matching_screenshots = list(test_folder.glob(screenshot_pattern))
        if matching_screenshots:
            result_data['screenshot_path'] = str(matching_screenshots[0])
        
        # 找對應的分析文件
        analysis_pattern = f"test_{test_id:03d}_*_analysis.json"
        matching_analysis = list(test_folder.glob(analysis_pattern))
        if matching_analysis:
            try:
                with open(matching_analysis[0], 'r', encoding='utf-8') as f:
                    analysis_data = json.load(f)
                    # 提取 parsed_result
                    if 'parsed_result' in analysis_data:
                        result_data['analysis_result'] = analysis_data['parsed_result']
                    elif 'result' in analysis_data:
                        result_data['analysis_result'] = analysis_data['result']
                    
                    # 檢查錯誤
                    if 'error_analysis' in analysis_data:
                        result_data['error_info'] = {
                            'error': analysis_data.get('raw_response', '解析錯誤'),
                            'error_type': 'JSON_PARSE_ERROR'
                        }
            except Exception as e:
                print(f"警告：無法讀取分析文件 {matching_analysis[0]} - {e}")
                result_data['error_info'] = {
                    'error': f'文件讀取錯誤: {str(e)}',
                    'error_type': 'FILE_READ_ERROR'
                }
        
        results.append(result_data)
    
    return results, test_folder

def generate_html_report(test_folder, show_all_results=True):
    """生成HTML報告"""
    results, folder_path = load_test_results(test_folder)
    if not results:
        return False
    
    # 創建合併器
    merger = RealTimeMerger(folder_path, show_all_results)
    
    # 添加所有結果到合併器
    for result in results:
        test_id = result['test_id']
        screenshot_path = result['screenshot_path']
        analysis_result = result['analysis_result']
        error_info = result['error_info']
        
        merger.add_test_result(test_id, screenshot_path, analysis_result, error_info)
    
    # 生成HTML報告
    merger.generate_quick_html()
    
    return True

def main():
    """主函數"""
    if len(sys.argv) < 2:
        print("用法：python generate_test_html.py <測試資料夾路徑> [show_all]")
        print("例如：python generate_test_html.py integration_test_20250811_142022")
        print("      python generate_test_html.py integration_test_20250811_142022 show_all")
        return
    
    test_folder = sys.argv[1]
    show_all_results = len(sys.argv) > 2 and sys.argv[2] == 'show_all'
    
    print(f"為測試資料夾生成HTML報告: {test_folder}")
    print(f"顯示模式: {'所有結果' if show_all_results else '只顯示匹配結果'}")
    print("-" * 50)
    
    if generate_html_report(test_folder, show_all_results):
        print("\n✅ HTML報告生成成功！")
        html_file = Path(test_folder) / "quick_view.html"
        print(f"📁 報告位置: {html_file}")
        print(f"💡 請打開 {html_file} 查看結果")
    else:
        print("\n❌ HTML報告生成失敗")

if __name__ == "__main__":
    main()