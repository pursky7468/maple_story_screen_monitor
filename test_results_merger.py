#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""測試結果合併工具 - 將測試結果和影像合併為方便調試的格式"""

import os
import json
import base64
from datetime import datetime
from pathlib import Path
import re

class TestResultsMerger:
    """測試結果合併器"""
    
    def __init__(self, test_folder_path):
        self.test_folder = Path(test_folder_path)
        self.results = []
        
    def load_test_data(self):
        """載入測試資料夾中的所有文件"""
        print(f"載入測試資料夾: {self.test_folder}")
        
        if not self.test_folder.exists():
            print(f"錯誤：測試資料夾不存在 - {self.test_folder}")
            return False
        
        # 載入測試摘要
        summary_file = self.test_folder / "test_summary.json"
        if summary_file.exists():
            with open(summary_file, 'r', encoding='utf-8') as f:
                self.summary = json.load(f)
        else:
            self.summary = {"test_start_time": "未知", "total_runs": 0}
        
        # 獲取所有測試文件
        screenshot_files = list(self.test_folder.glob("*_screenshot.png"))
        
        print(f"找到 {len(screenshot_files)} 個截圖文件")
        
        # 為每個截圖找到對應的分析結果
        for screenshot_file in sorted(screenshot_files):
            test_result = self.process_test_file(screenshot_file)
            if test_result:
                self.results.append(test_result)
        
        print(f"成功載入 {len(self.results)} 個測試結果")
        return len(self.results) > 0
    
    def process_test_file(self, screenshot_file):
        """處理單個測試文件"""
        base_name = screenshot_file.stem.replace("_screenshot", "")
        
        # 尋找對應的分析文件
        analysis_file = None
        error_file = None
        debug_file = None
        
        for suffix in ["_analysis.json", "_error.json"]:
            candidate = self.test_folder / f"{base_name}{suffix}"
            if candidate.exists():
                if suffix == "_analysis.json":
                    analysis_file = candidate
                elif suffix == "_error.json":
                    error_file = candidate
        
        # 尋找debug文件
        debug_candidate = self.test_folder / f"{base_name}_debug.txt"
        if debug_candidate.exists():
            debug_file = debug_candidate
        
        # 提取測試ID和時間戳
        match = re.search(r'test_(\d+)_(\d+_\d+_\d+)', base_name)
        if match:
            test_id = int(match.group(1))
            timestamp = match.group(2)
        else:
            test_id = 0
            timestamp = "未知"
        
        # 載入分析結果
        analysis_data = None
        error_data = None
        debug_content = None
        
        if analysis_file:
            with open(analysis_file, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
        
        if error_file:
            with open(error_file, 'r', encoding='utf-8') as f:
                error_data = json.load(f)
        
        if debug_file:
            with open(debug_file, 'r', encoding='utf-8') as f:
                debug_content = f.read()
        
        # 轉換圖片為base64
        image_base64 = self.image_to_base64(screenshot_file)
        
        return {
            "test_id": test_id,
            "timestamp": timestamp,
            "screenshot_file": screenshot_file.name,
            "image_base64": image_base64,
            "analysis_data": analysis_data,
            "error_data": error_data,
            "debug_content": debug_content,
            "has_analysis": analysis_data is not None,
            "has_error": error_data is not None,
            "has_debug": debug_content is not None
        }
    
    def image_to_base64(self, image_path):
        """將圖片轉換為base64編碼"""
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
                return base64.b64encode(image_data).decode('utf-8')
        except Exception as e:
            print(f"警告：無法讀取圖片 {image_path}: {e}")
            return None
    
    def generate_html_report(self, output_file="test_report.html"):
        """生成HTML報告"""
        if not self.results:
            print("沒有測試結果可以生成報告")
            return False
        
        html_content = self.create_html_template()
        
        output_path = self.test_folder / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML報告已生成: {output_path}")
        return True
    
    def create_html_template(self):
        """創建HTML模板"""
        # 統計信息
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r['has_analysis']])
        error_tests = len([r for r in self.results if r['has_error']])
        
        html = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>測試結果報告 - {self.summary.get('test_start_time', '未知')}</title>
    <style>
        body {{
            font-family: 'Microsoft JhengHei', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
        }}
        .stats {{
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
            flex: 1;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #3498db;
        }}
        .controls {{
            margin-bottom: 20px;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .test-item {{
            background: white;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .test-header {{
            background-color: #ecf0f1;
            padding: 15px;
            border-bottom: 1px solid #bdc3c7;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .test-header.success {{
            background-color: #d5f4e6;
            border-left: 5px solid #27ae60;
        }}
        .test-header.error {{
            background-color: #ffeaa7;
            border-left: 5px solid #e17055;
        }}
        .test-content {{
            display: flex;
            padding: 20px;
            gap: 20px;
        }}
        .image-section {{
            flex: 1;
            min-width: 300px;
        }}
        .image-section img {{
            max-width: 100%;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        .analysis-section {{
            flex: 2;
            min-width: 400px;
        }}
        .json-display {{
            background-color: #2d3748;
            color: #e2e8f0;
            padding: 15px;
            border-radius: 4px;
            font-family: 'Consolas', monospace;
            font-size: 12px;
            overflow-x: auto;
            max-height: 400px;
            overflow-y: auto;
        }}
        .error-display {{
            background-color: #fed7d7;
            border: 1px solid #fc8181;
            color: #c53030;
            padding: 15px;
            border-radius: 4px;
            margin-top: 10px;
        }}
        .debug-display {{
            background-color: #f7fafc;
            border: 1px solid #cbd5e0;
            padding: 15px;
            border-radius: 4px;
            font-family: 'Consolas', monospace;
            font-size: 11px;
            margin-top: 10px;
            max-height: 200px;
            overflow-y: auto;
        }}
        .status-badge {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }}
        .status-success {{
            background-color: #27ae60;
            color: white;
        }}
        .status-error {{
            background-color: #e74c3c;
            color: white;
        }}
        .filter-btn {{
            margin-right: 10px;
            padding: 8px 16px;
            border: 1px solid #ddd;
            background: white;
            cursor: pointer;
            border-radius: 4px;
        }}
        .filter-btn.active {{
            background-color: #3498db;
            color: white;
            border-color: #3498db;
        }}
        .hidden {{
            display: none !important;
        }}
        .match-highlight {{
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 4px;
            padding: 10px;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>測試結果報告</h1>
        <p>測試時間: {self.summary.get('test_start_time', '未知')} | 
           分析方法: {self.summary.get('analyzer_class', '未知')} | 
           總測試數: {total_tests}</p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-number">{total_tests}</div>
            <div>總測試數</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{successful_tests}</div>
            <div>成功分析</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{error_tests}</div>
            <div>發生錯誤</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len([r for r in self.results if r['analysis_data'] and r['analysis_data'].get('parsed_result', {}).get('is_match')])}</div>
            <div>找到匹配</div>
        </div>
    </div>
    
    <div class="controls">
        <button class="filter-btn active" onclick="filterResults('all')">全部</button>
        <button class="filter-btn" onclick="filterResults('success')">成功分析</button>
        <button class="filter-btn" onclick="filterResults('error')">發生錯誤</button>
        <button class="filter-btn" onclick="filterResults('match')">找到匹配</button>
    </div>
    
    <div class="results">
        {self.generate_test_items()}
    </div>
    
    <script>
        function filterResults(type) {{
            const buttons = document.querySelectorAll('.filter-btn');
            const items = document.querySelectorAll('.test-item');
            
            // 更新按鈕狀態
            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            // 篩選項目
            items.forEach(item => {{
                item.classList.remove('hidden');
                
                if (type === 'success' && !item.classList.contains('success')) {{
                    item.classList.add('hidden');
                }} else if (type === 'error' && !item.classList.contains('error')) {{
                    item.classList.add('hidden');
                }} else if (type === 'match' && !item.classList.contains('match')) {{
                    item.classList.add('hidden');
                }}
            }});
        }}
        
        function toggleDetails(testId) {{
            const details = document.getElementById('details-' + testId);
            const button = document.getElementById('btn-' + testId);
            
            if (details.style.display === 'none') {{
                details.style.display = 'block';
                button.textContent = '收起詳細';
            }} else {{
                details.style.display = 'none';
                button.textContent = '顯示詳細';
            }}
        }}
    </script>
</body>
</html>
"""
        return html
    
    def generate_test_items(self):
        """生成測試項目的HTML"""
        items_html = []
        
        for result in sorted(self.results, key=lambda x: x['test_id']):
            # 判斷測試狀態
            is_success = result['has_analysis']
            is_error = result['has_error']
            has_match = False
            
            if result['analysis_data'] and result['analysis_data'].get('parsed_result'):
                has_match = result['analysis_data']['parsed_result'].get('is_match', False)
            
            # 設定樣式類
            header_class = "success" if is_success else "error"
            item_classes = ["test-item"]
            if is_success:
                item_classes.append("success")
            if is_error:
                item_classes.append("error")
            if has_match:
                item_classes.append("match")
            
            # 狀態徽章
            if is_success:
                status_badge = '<span class="status-badge status-success">分析成功</span>'
            else:
                status_badge = '<span class="status-badge status-error">分析失敗</span>'
            
            if has_match:
                status_badge += ' <span class="status-badge status-success">找到匹配</span>'
            
            # 生成分析結果顯示
            analysis_html = self.generate_analysis_html(result)
            
            item_html = f"""
        <div class="{' '.join(item_classes)}">
            <div class="test-header {header_class}">
                <div>
                    <strong>測試 #{result['test_id']:03d}</strong>
                    <span style="margin-left: 20px;">時間: {result['timestamp']}</span>
                    <span style="margin-left: 20px;">{status_badge}</span>
                </div>
                <button id="btn-{result['test_id']}" onclick="toggleDetails({result['test_id']})" 
                        class="filter-btn">顯示詳細</button>
            </div>
            <div class="test-content">
                <div class="image-section">
                    <h4>截圖</h4>
                    {"<img src='data:image/png;base64," + result['image_base64'] + "' alt='測試截圖'>" if result['image_base64'] else "<p>圖片載入失敗</p>"}
                    <p style="font-size: 12px; color: #666; margin-top: 10px;">
                        文件: {result['screenshot_file']}
                    </p>
                </div>
                <div class="analysis-section">
                    {analysis_html}
                </div>
            </div>
            <div id="details-{result['test_id']}" style="display: none; padding: 20px; border-top: 1px solid #ddd; background-color: #fafafa;">
                {self.generate_detailed_info(result)}
            </div>
        </div>
"""
            items_html.append(item_html)
        
        return '\n'.join(items_html)
    
    def generate_analysis_html(self, result):
        """生成分析結果HTML"""
        html_parts = []
        
        if result['analysis_data']:
            parsed_result = result['analysis_data'].get('parsed_result', {})
            
            # 基本信息
            html_parts.append("<h4>分析結果</h4>")
            
            if parsed_result.get('is_match'):
                matched_items = parsed_result.get('matched_items', [])
                
                # 生成物品詳細信息
                items_info = ""
                if matched_items:
                    items_list = []
                    for item in matched_items:
                        if isinstance(item, dict):
                            item_name = item.get('item_name', '未知物品')
                            keywords = item.get('keywords_found', [])
                            if keywords:
                                items_list.append(f"<span style='color: #e74c3c; font-weight: bold;'>{item_name}</span> ({', '.join(keywords)})")
                            else:
                                items_list.append(f"<span style='color: #e74c3c; font-weight: bold;'>{item_name}</span>")
                        else:
                            items_list.append(f"<span style='color: #e74c3c; font-weight: bold;'>{str(item)}</span>")
                    items_info = "<br>&nbsp;&nbsp;&nbsp;&nbsp;".join(items_list)
                
                html_parts.append(f"""
                <div class="match-highlight">
                    <strong>🎯 找到匹配交易！</strong><br>
                    <strong>玩家:</strong> <span style='color: #2980b9; font-weight: bold;'>{parsed_result.get('player_name', '未知')}</span><br>
                    <strong>頻道:</strong> <span style='color: #27ae60; font-weight: bold;'>{parsed_result.get('channel_number', '未知')}</span><br>
                    <strong>信心度:</strong> {parsed_result.get('confidence', 0):.2f}<br>
                    <strong>匹配商品 ({len(matched_items)} 個):</strong><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{items_info}
                </div>
                """)
            
            # 顯示部分JSON
            limited_result = {
                "full_text": parsed_result.get('full_text', '')[:200] + "..." if len(parsed_result.get('full_text', '')) > 200 else parsed_result.get('full_text', ''),
                "is_match": parsed_result.get('is_match'),
                "confidence": parsed_result.get('confidence'),
                "analysis_method": parsed_result.get('analysis_method'),
                "matched_items": parsed_result.get('matched_items', [])
            }
            
            html_parts.append(f'<pre class="json-display">{json.dumps(limited_result, ensure_ascii=False, indent=2)}</pre>')
        
        if result['error_data']:
            html_parts.append("<h4>錯誤信息</h4>")
            html_parts.append(f'<div class="error-display">{result["error_data"].get("error", "未知錯誤")}</div>')
        
        return '\n'.join(html_parts)
    
    def generate_detailed_info(self, result):
        """生成詳細信息HTML"""
        html_parts = []
        
        if result['analysis_data']:
            html_parts.append("<h5>完整分析數據</h5>")
            html_parts.append(f'<pre class="json-display">{json.dumps(result["analysis_data"], ensure_ascii=False, indent=2)}</pre>')
        
        if result['debug_content']:
            html_parts.append("<h5>調試信息</h5>")
            html_parts.append(f'<div class="debug-display">{result["debug_content"]}</div>')
        
        return '\n'.join(html_parts)
    
    def generate_json_report(self, output_file="merged_results.json"):
        """生成合併的JSON報告（包含base64圖片）"""
        if not self.results:
            print("沒有測試結果可以生成JSON報告")
            return False
        
        merged_data = {
            "summary": self.summary,
            "generation_time": datetime.now().isoformat(),
            "total_tests": len(self.results),
            "results": self.results
        }
        
        output_path = self.test_folder / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)
        
        print(f"JSON報告已生成: {output_path}")
        return True

def main():
    """主程式"""
    print("測試結果合併工具")
    print("=" * 50)
    
    # 尋找測試資料夾
    current_dir = Path(".")
    test_folders = list(current_dir.glob("integration_test_*"))
    
    if not test_folders:
        print("沒有找到測試資料夾（integration_test_*）")
        print("請確認你在正確的目錄中運行此工具")
        return
    
    # 顯示可用的測試資料夾
    print(f"找到 {len(test_folders)} 個測試資料夾：")
    for i, folder in enumerate(sorted(test_folders, key=lambda x: x.name), 1):
        print(f"{i}. {folder.name}")
    
    # 讓用戶選擇
    while True:
        try:
            choice = input(f"\n請選擇要處理的資料夾 (1-{len(test_folders)}) 或輸入 'all' 處理全部: ").strip()
            
            if choice.lower() == 'all':
                selected_folders = test_folders
                break
            else:
                choice_num = int(choice)
                if 1 <= choice_num <= len(test_folders):
                    selected_folders = [sorted(test_folders, key=lambda x: x.name)[choice_num - 1]]
                    break
                else:
                    print(f"請輸入 1 到 {len(test_folders)} 之間的數字")
        except ValueError:
            print("請輸入有效的數字或 'all'")
    
    # 處理選擇的資料夾
    for folder in selected_folders:
        print(f"\n處理資料夾: {folder.name}")
        
        merger = TestResultsMerger(folder)
        
        if merger.load_test_data():
            print("選擇輸出格式：")
            print("1. HTML報告（推薦，可在瀏覽器中查看）")
            print("2. JSON報告（包含base64圖片）")
            print("3. 兩種格式都生成")
            
            format_choice = input("請選擇 (1-3): ").strip()
            
            if format_choice in ['1', '3']:
                merger.generate_html_report()
            if format_choice in ['2', '3']:
                merger.generate_json_report()
            
            print(f"✓ {folder.name} 處理完成")
        else:
            print(f"✗ {folder.name} 處理失敗")
    
    print("\n所有資料夾處理完成！")

if __name__ == "__main__":
    main()