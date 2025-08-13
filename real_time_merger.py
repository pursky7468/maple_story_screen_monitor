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
        """生成快速HTML查看器 - 只顯示有匹配的結果"""
        if not self.merged_results:
            return
        
        # 只取有匹配的結果，並按時間倒序排列
        matched_results = [r for r in self.merged_results if r['has_match']]
        matched_results.reverse()  # 最新的在上面
        
        if not matched_results:
            print("沒有找到匹配結果，不生成HTML報告")
            return
        
        html_file = self.test_folder / "quick_view.html"
        
        # 統計信息
        total_tests = len(self.merged_results)
        matched_count = len(matched_results)
        
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>交易匹配監控結果</title>
    <style>
        body {{ font-family: 'Microsoft JhengHei', Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 15px; margin-bottom: 20px; border-radius: 8px; }}
        .stats {{ display: flex; gap: 15px; margin-bottom: 20px; }}
        .stat {{ background: white; padding: 15px; border-radius: 8px; text-align: center; flex: 1; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .stat-number {{ font-size: 1.5em; font-weight: bold; color: #e74c3c; }}
        .match-list {{ display: flex; flex-direction: column; gap: 15px; }}
        .match-card {{ background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #e74c3c; }}
        .match-header {{ background: #fff3cd; padding: 12px 15px; border-bottom: 1px solid #f39c12; }}
        .match-content {{ padding: 15px; }}
        .field-row {{ margin-bottom: 12px; }}
        .field-label {{ font-weight: bold; color: #2c3e50; min-width: 80px; display: inline-block; }}
        .field-value {{ color: #34495e; }}
        .player-name {{ color: #2980b9; font-weight: bold; }}
        .channel-name {{ color: #27ae60; font-weight: bold; }}
        .items-list {{ color: #e74c3c; font-weight: bold; }}
        .full-text {{ background: #ecf0f1; padding: 10px; border-radius: 4px; font-family: Consolas, monospace; font-size: 12px; line-height: 1.4; }}
        .screenshot {{ max-width: 200px; max-height: 100px; border: 1px solid #ddd; border-radius: 4px; cursor: pointer; float: right; margin-left: 15px; }}
        .timestamp {{ color: #7f8c8d; font-size: 0.9em; float: right; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>🎯 交易匹配監控結果</h2>
        <p>生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 找到 {matched_count} 個匹配交易</p>
    </div>
    
    <div class="stats">
        <div class="stat">
            <div class="stat-number">{total_tests}</div>
            <div>總測試數</div>
        </div>
        <div class="stat">
            <div class="stat-number">{matched_count}</div>
            <div>匹配交易</div>
        </div>
        <div class="stat">
            <div class="stat-number">{(matched_count/total_tests*100):.1f}%</div>
            <div>匹配率</div>
        </div>
    </div>
    
    <div class="match-list">
        {self.generate_match_cards(matched_results)}
    </div>
    
    <script>
        // 點擊圖片放大
        document.querySelectorAll('.screenshot').forEach(img => {{
            img.onclick = function() {{
                const modal = document.createElement('div');
                modal.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);z-index:1000;display:flex;justify-content:center;align-items:center;cursor:pointer;';
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
            print(f"交易匹配報告已生成: {html_file} (共 {matched_count} 個匹配)")
        except Exception as e:
            print(f"生成HTML查看器失敗: {e}")
    
    def generate_match_cards(self, matched_results):
        """生成匹配交易卡片HTML - 新格式"""
        cards = []
        
        for result in matched_results:
            details = result.get('match_details', {})
            analysis = result.get('analysis_result', {})
            
            # 玩家信息
            player_name = details.get('player_name', '未知')
            channel_number = details.get('channel_number', '未知')
            
            # 商品內容
            matched_items = details.get('matched_items', [])
            items_display = []
            if matched_items:
                for item in matched_items:
                    if isinstance(item, dict):
                        item_name = item.get('item_name', '未知物品')
                        keywords = item.get('keywords_found', [])
                        if keywords:
                            items_display.append(f"{item_name} ({', '.join(keywords)})")
                        else:
                            items_display.append(item_name)
                    else:
                        items_display.append(str(item))
            items_text = ' | '.join(items_display) if items_display else '無'
            
            # 完整廣播內容
            full_text = analysis.get('full_text', '無法取得完整內容')
            
            # 時間戳 - 轉換為完整格式
            timestamp = result.get('timestamp', '')
            formatted_time = '未知時間'
            if timestamp:
                try:
                    # 解析時間戳格式 YYYYMMDD_HHMMSS_mmm
                    if '_' in timestamp:
                        date_part, time_part = timestamp.split('_', 1)
                        if len(date_part) == 8 and len(time_part) >= 6:
                            year = date_part[:4]
                            month = date_part[4:6] 
                            day = date_part[6:8]
                            hour = time_part[:2]
                            minute = time_part[2:4]
                            second = time_part[4:6]
                            formatted_time = f"{year}/{month}/{day} {hour}:{minute}:{second}"
                            time_display = f"{hour}:{minute}:{second}"  # 用於標題欄的簡短格式
                        else:
                            formatted_time = timestamp
                            time_display = timestamp
                    else:
                        formatted_time = timestamp
                        time_display = timestamp
                except:
                    formatted_time = timestamp
                    time_display = timestamp
            else:
                time_display = '未知'
            
            card_html = f"""
        <div class="match-card">
            <div class="match-header">
                <strong>交易匹配 #{result['test_id']:03d}</strong>
                <span class="timestamp">{time_display}</span>
            </div>
            <div class="match-content">
                {"<img class='screenshot' src='data:image/png;base64," + result['image_base64'] + "' alt='交易截圖'>" if result['image_base64'] else ""}
                
                <div class="field-row">
                    <span class="field-label">玩家:</span>
                    <span class="field-value player-name">{player_name}</span>
                </div>
                
                <div class="field-row">
                    <span class="field-label">頻道:</span>
                    <span class="field-value channel-name">{channel_number}</span>
                </div>
                
                <div class="field-row">
                    <span class="field-label">商品內容:</span>
                    <span class="field-value items-list">{items_text}</span>
                </div>
                
                <div class="field-row">
                    <span class="field-label">匹配時間:</span>
                    <span class="field-value" style="color: #3498db; font-weight: bold;">{formatted_time}</span>
                </div>
                
                <div class="field-row">
                    <span class="field-label">完整廣播:</span>
                </div>
                <div class="full-text">{full_text}</div>
                
                <div style="clear: both;"></div>
            </div>
        </div>
            """
            
            cards.append(card_html)
        
        return '\n'.join(cards)
    
    def generate_cards(self):
        """生成測試卡片HTML - 保留舊方法以防其他地方使用"""
        # 這個方法現在只作為後備，實際使用新的generate_match_cards
        return self.generate_match_cards([r for r in self.merged_results if r['has_match']])

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