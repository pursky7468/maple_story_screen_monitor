#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""實時測試結果合併器 - 在測試過程中自動合併結果和影像"""

import os
import json
import base64
from datetime import datetime
from pathlib import Path

class RealTimeMerger:
    """實時測試結果合併器"""
    
    def __init__(self, test_folder):
        self.test_folder = Path(test_folder)
        self.merged_results = []
        self.output_file = self.test_folder / "combined_results.json"
        
    def add_test_result(self, test_id, screenshot_path, analysis_result=None, error_info=None):
        """添加單個測試結果"""
        try:
            # 轉換截圖為base64
            image_base64 = None
            if screenshot_path and os.path.exists(screenshot_path):
                with open(screenshot_path, 'rb') as f:
                    image_data = f.read()
                    image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # 創建合併記錄
            combined_record = {
                "test_id": test_id,
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3],
                "screenshot_filename": os.path.basename(screenshot_path) if screenshot_path else None,
                "image_base64": image_base64,
                "analysis_result": analysis_result,
                "error_info": error_info,
                "has_match": False,
                "match_details": None
            }
            
            # 檢查是否有匹配
            if analysis_result and isinstance(analysis_result, dict):
                if analysis_result.get('is_match'):
                    combined_record["has_match"] = True
                    combined_record["match_details"] = {
                        "player_name": analysis_result.get('player_name'),
                        "channel_number": analysis_result.get('channel_number'),
                        "matched_items": analysis_result.get('matched_items', []),
                        "confidence": analysis_result.get('confidence', 0)
                    }
            
            self.merged_results.append(combined_record)
            self.save_combined_results()
            
            return True
            
        except Exception as e:
            print(f"警告：添加測試結果失敗 - {e}")
            return False
    
    def save_combined_results(self):
        """保存合併結果到文件"""
        try:
            combined_data = {
                "generation_info": {
                    "created_at": datetime.now().isoformat(),
                    "total_tests": len(self.merged_results),
                    "successful_tests": len([r for r in self.merged_results if r['analysis_result']]),
                    "error_tests": len([r for r in self.merged_results if r['error_info']]),
                    "matched_tests": len([r for r in self.merged_results if r['has_match']])
                },
                "results": self.merged_results
            }
            
            # 使用現有的JSON序列化函數
            from screen_monitor import convert_to_json_serializable
            safe_data = convert_to_json_serializable(combined_data)
            
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(safe_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"警告：保存合併結果失敗 - {e}")
    
    def generate_quick_html(self):
        """生成快速HTML查看器"""
        if not self.merged_results:
            return
        
        html_file = self.test_folder / "quick_view.html"
        
        # 統計信息
        total = len(self.merged_results)
        successful = len([r for r in self.merged_results if r['analysis_result']])
        matched = len([r for r in self.merged_results if r['has_match']])
        
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>快速測試查看器</title>
    <style>
        body {{ font-family: 'Microsoft JhengHei', Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 15px; margin-bottom: 20px; border-radius: 8px; }}
        .stats {{ display: flex; gap: 15px; margin-bottom: 20px; }}
        .stat {{ background: white; padding: 15px; border-radius: 8px; text-align: center; flex: 1; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .stat-number {{ font-size: 1.5em; font-weight: bold; color: #3498db; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; }}
        .card {{ background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .card-header {{ padding: 15px; background: #ecf0f1; border-bottom: 1px solid #bdc3c7; }}
        .card-header.success {{ background: #d5f4e6; border-left: 4px solid #27ae60; }}
        .card-header.match {{ background: #fff3cd; border-left: 4px solid #f39c12; }}
        .card-header.error {{ background: #ffeaa7; border-left: 4px solid #e74c3c; }}
        .card-content {{ padding: 15px; }}
        .screenshot {{ max-width: 100%; border: 1px solid #ddd; border-radius: 4px; }}
        .result-text {{ background: #2d3748; color: #e2e8f0; padding: 10px; border-radius: 4px; font-family: Consolas, monospace; font-size: 11px; max-height: 150px; overflow-y: auto; }}
        .match-info {{ background: #fff3cd; border: 1px solid #f39c12; padding: 10px; border-radius: 4px; margin-top: 10px; }}
        .badge {{ padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold; }}
        .badge-success {{ background: #27ae60; color: white; }}
        .badge-error {{ background: #e74c3c; color: white; }}
        .badge-match {{ background: #f39c12; color: white; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>快速測試查看器</h2>
        <p>生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="stats">
        <div class="stat">
            <div class="stat-number">{total}</div>
            <div>總測試</div>
        </div>
        <div class="stat">
            <div class="stat-number">{successful}</div>
            <div>成功分析</div>
        </div>
        <div class="stat">
            <div class="stat-number">{matched}</div>
            <div>找到匹配</div>
        </div>
    </div>
    
    <div class="grid">
        {self.generate_cards()}
    </div>
    
    <script>
        // 點擊圖片放大
        document.querySelectorAll('.screenshot').forEach(img => {{
            img.style.cursor = 'pointer';
            img.onclick = function() {{
                const modal = document.createElement('div');
                modal.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);z-index:1000;display:flex;justify-content:center;align-items:center;';
                const bigImg = document.createElement('img');
                bigImg.src = this.src;
                bigImg.style.cssText = 'max-width:90%;max-height:90%;';
                modal.appendChild(bigImg);
                modal.onclick = () => document.body.removeChild(modal);
                document.body.appendChild(modal);
            }};
        }});
    </script>
</body>
</html>
"""
        
        try:
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"快速查看器已生成: {html_file}")
        except Exception as e:
            print(f"生成HTML查看器失敗: {e}")
    
    def generate_cards(self):
        """生成測試卡片HTML"""
        cards = []
        
        for result in self.merged_results[-20:]:  # 只顯示最近20個
            # 確定卡片樣式
            header_class = "card-header"
            badges = []
            
            if result['analysis_result']:
                header_class += " success"
                badges.append('<span class="badge badge-success">分析成功</span>')
            
            if result['has_match']:
                header_class += " match"
                badges.append('<span class="badge badge-match">找到匹配</span>')
            
            if result['error_info']:
                header_class += " error"
                badges.append('<span class="badge badge-error">發生錯誤</span>')
            
            # 生成結果摘要
            result_summary = ""
            if result['analysis_result']:
                analysis = result['analysis_result']
                summary_text = analysis.get('full_text', '')
                if len(summary_text) > 100:
                    summary_text = summary_text[:100] + "..."
                
                result_summary = f"""
                <div class="result-text">
                文字內容: {summary_text}
                分析方法: {analysis.get('analysis_method', '未知')}
                信心度: {analysis.get('confidence', 0):.2f}
                </div>
                """
            
            # 匹配信息
            match_info = ""
            if result['has_match'] and result['match_details']:
                details = result['match_details']
                match_info = f"""
                <div class="match-info">
                    <strong>🎯 找到匹配</strong><br>
                    玩家: {details.get('player_name', '未知')}<br>
                    頻道: {details.get('channel_number', '未知')}<br>
                    匹配商品: {len(details.get('matched_items', []))} 個
                </div>
                """
            
            card_html = f"""
        <div class="card">
            <div class="{header_class}">
                <strong>測試 #{result['test_id']:03d}</strong>
                <div style="margin-top: 5px;">{' '.join(badges)}</div>
            </div>
            <div class="card-content">
                {"<img class='screenshot' src='data:image/png;base64," + result['image_base64'] + "' alt='測試截圖'>" if result['image_base64'] else "<p>圖片載入失敗</p>"}
                {result_summary}
                {match_info}
            </div>
        </div>
            """
            
            cards.append(card_html)
        
        return '\n'.join(cards)

# 集成到現有系統的輔助函數
def setup_real_time_merger(test_folder):
    """為測試資料夾設置實時合併器"""
    return RealTimeMerger(test_folder)

def log_test_result(merger, test_id, screenshot_path, result=None, error=None):
    """記錄測試結果到合併器"""
    if merger:
        merger.add_test_result(test_id, screenshot_path, result, error)
        
        # 每10個測試生成一次快速查看器
        if len(merger.merged_results) % 10 == 0:
            merger.generate_quick_html()