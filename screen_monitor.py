import pyautogui
import time
import tkinter as tk
from tkinter import messagebox
import os
import json
import numpy as np
from datetime import datetime
from config import *

# 確保買物品配置存在，向後兼容
if 'BUYING_ITEMS' not in globals():
    BUYING_ITEMS = {}
if 'TRADING_KEYWORDS' not in globals():
    TRADING_KEYWORDS = {}
from roi_selector import ROISelector
from text_analyzer import AnalysisResult
from gemini_analyzer import GeminiAnalyzer
from ocr_analyzer import OCRAnalyzer
from ocr_rectangle_analyzer import OCRRectangleAnalyzer
from real_time_merger import RealTimeMerger, log_test_result
from html_template_with_real_config import get_enhanced_html_template, get_current_config
import webbrowser
import threading
from config_api import start_config_api_server

def convert_to_json_serializable(obj):
    """將物件轉換為JSON可序列化的格式"""
    if isinstance(obj, (np.integer, np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_json_serializable(item) for item in obj]
    else:
        return obj

class ScreenMonitor:
    """使用策略模式的螢幕監控器"""
    
    def __init__(self, roi_coordinates, analyzer, save_screenshots=False, show_alerts=True, auto_open_html=True):
        self.roi_coordinates = roi_coordinates
        self.analyzer = analyzer
        self.save_screenshots = save_screenshots
        self.show_alerts = show_alerts
        self.auto_open_html = auto_open_html
        self.running = False
        self.monitoring_counter = 0
        self.real_time_merger = None
        self.monitoring_session_folder = None
        self.html_opened = False
        self.api_server_thread = None
        
        # 始終創建會話資料夾和實時合併器（為了支援HTML報告生成）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.monitoring_session_folder = f"monitoring_session_{timestamp}"
        
        if not os.path.exists(self.monitoring_session_folder):
            os.makedirs(self.monitoring_session_folder)
        
        # 初始化實時合併器
        self.real_time_merger = RealTimeMerger(self.monitoring_session_folder)
        
        print(f"監控會話資料夾: {self.monitoring_session_folder}")
        if self.save_screenshots:
            print(f"檔案保存: 所有截圖和JSON將被保存（完整debug模式）")
        else:
            print(f"檔案保存: 僅在匹配成功時保存截圖和JSON（精簡模式）")
        print(f"HTML合併報告將自動生成{'並開啟' if self.auto_open_html else ''}")
        
        # 啟動配置API服務器
        self.start_config_api_server()
        
        # 創建初始HTML文件
        self.create_initial_html()
        
    def start_config_api_server(self):
        """啟動配置API服務器"""
        try:
            def run_api_server():
                start_config_api_server(port=8899)
            
            self.api_server_thread = threading.Thread(target=run_api_server, daemon=True)
            self.api_server_thread.start()
            print("[OK] 配置API服務器已在背景啟動 (port 8899)")
        except Exception as e:
            print(f"[WARN] 無法啟動配置API服務器: {e}")
    
    def create_initial_html(self):
        """創建初始HTML報告文件 - 使用增強模板"""
        try:
            html_path = os.path.join(self.monitoring_session_folder, "quick_view.html")
            
            # 獲取當前配置
            current_config = get_current_config()
            
            # 使用增強HTML模板
            html_template = get_enhanced_html_template()
            initial_html = html_template.format(
                total_tests=0,
                matched_count=0,
                match_rate=0.0,
                match_cards='<div style="text-align: center; padding: 40px; color: #666;">系統正在監控中，找到匹配交易時會顯示在此處...</div>',
                current_config=json.dumps(current_config, ensure_ascii=False),
                refresh_interval=30
            )
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(initial_html)
                
            print(f"[OK] 增強HTML界面已創建: {html_path}")
            
        except Exception as e:
            print(f"[WARN] 創建HTML界面失敗 - {e}")
    
    def open_html_in_browser(self):
        """在瀏覽器中開啟HTML報告"""
        if not self.auto_open_html or self.html_opened:
            return
            
        try:
            html_path = os.path.join(self.monitoring_session_folder, "quick_view.html")
            if os.path.exists(html_path):
                # 轉換為絕對路徑和file:// URL
                abs_path = os.path.abspath(html_path)
                file_url = f"file:///{abs_path.replace(os.sep, '/')}"
                
                print(f"[INFO] 正在開啟HTML報告...")
                webbrowser.open(file_url)
                self.html_opened = True
                print("[OK] HTML報告已在預設瀏覽器中開啟")
            else:
                print(f"[WARN] 找不到HTML文件: {html_path}")
                
        except Exception as e:
            print(f"[WARN] 開啟瀏覽器失敗 - {e}")
        
    def capture_roi(self):
        try:
            # 截取ROI區域
            roi_screenshot = pyautogui.screenshot(
                region=(
                    self.roi_coordinates["x"],
                    self.roi_coordinates["y"], 
                    self.roi_coordinates["width"],
                    self.roi_coordinates["height"]
                )
            )
            
            return roi_screenshot
        except Exception as e:
            print(f"截圖錯誤: {e}")
            return None
    
    def analyze_with_strategy(self, image):
        """使用策略模式進行分析"""
        try:
            result, raw_response = self.analyzer.analyze(image)
            return result, raw_response
        except Exception as e:
            error_result = AnalysisResult(
                full_text=f"分析錯誤: {str(e)}",
                is_match=False,
                analysis_method=self.analyzer.__class__.__name__
            )
            return error_result, f"ERROR: {str(e)}"
    
    def format_match_info(self, result: AnalysisResult) -> str:
        """格式化匹配資訊"""
        if result.is_match:
            # 格式化匹配商品清單
            items_info = []
            for item in result.matched_items:
                item_name = item.get("item_name", "未知商品")
                keywords_found = item.get("keywords_found", [])
                items_info.append(f"  - {item_name}: {', '.join(keywords_found)}")
            
            items_text = '\n'.join(items_info) if items_info else "  - 無具體商品資訊"
            
            match_info = f"""[MATCH] 找到匹配！
分析方法: {result.analysis_method}
信心度: {result.confidence:.2f}
玩家名稱: {result.player_name}
頻道編號: {result.channel_number}
匹配商品:
{items_text}
所有關鍵字: {', '.join(result.matched_keywords)}

完整文字內容:
{result.full_text}"""
            return match_info
        else:
            no_match_info = f"""[SCAN] 未找到匹配
分析方法: {result.analysis_method}
信心度: {result.confidence:.2f}
頻道編號: {result.channel_number}

完整文字內容:
{result.full_text}"""
            return no_match_info
    
    def save_analysis_result(self, result: AnalysisResult, raw_response: str, screenshot_path: str, screenshot_saved: bool = True):
        """保存分析結果並記錄到合併器"""
        if self.real_time_merger:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # 包含毫秒
            
            # 只在以下情況保存JSON文件：
            # 1. 開啟了完整截圖保存模式（debug/完整記錄模式）
            # 2. 或者匹配成功（重要結果必須保存）
            should_save_json = self.save_screenshots or result.is_match
            
            result_path = None
            if should_save_json:
                # 保存結構化結果
                result_path = os.path.join(self.monitoring_session_folder, f"analysis_{timestamp}.json")
                analysis_data = {
                    "monitoring_id": self.monitoring_counter,
                    "timestamp": timestamp,
                    "analysis_method": result.analysis_method,
                    "result": convert_to_json_serializable(result.to_dict()),
                    "raw_response": convert_to_json_serializable(raw_response),
                    "screenshot_path": screenshot_path
                }
                
                with open(result_path, 'w', encoding='utf-8') as f:
                    json.dump(analysis_data, f, ensure_ascii=False, indent=2)
            
            # 記錄到實時合併器（用於HTML報告生成）
            result_dict = result.to_dict() if hasattr(result, 'to_dict') else result
            error_info = None
            
            if isinstance(raw_response, str) and (raw_response.startswith("ERROR") or "ERROR" in raw_response):
                error_info = {
                    "error": raw_response,
                    "error_type": "ANALYSIS_ERROR",
                    "analysis_method": result.analysis_method
                }
                result_dict = None
            
            log_test_result(self.real_time_merger, self.monitoring_counter, screenshot_path, result_dict, error_info)
            
            # 生成狀態提示
            match_status = "匹配成功" if result.is_match else "未匹配"
            save_status = "已保存截圖" if screenshot_saved else "未保存截圖"
            json_status = "已保存JSON" if should_save_json else "未保存JSON"
            
            if result.is_match:
                print(f"[MATCH] 分析 #{self.monitoring_counter}: {match_status} ({save_status}, {json_status})")
            else:
                print(f"[SCAN] 分析 #{self.monitoring_counter}: {match_status} ({save_status}, {json_status})")
    
    def show_alert(self, message):
        if self.show_alerts:
            root = tk.Tk()
            root.withdraw()  
            messagebox.showinfo("匹配提醒", f"找到符合條件的內容！\n\n{message}")
            root.destroy()
        else:
            print("提示窗已關閉，跳過彈窗顯示")
    
    def start_monitoring(self):
        """開始監控"""
        self.running = True
        print("開始監控螢幕...")
        print(f"分析方法: {self.analyzer.__class__.__name__}")
        print(f"ROI區域: x={self.roi_coordinates['x']}, y={self.roi_coordinates['y']}, "
              f"寬度={self.roi_coordinates['width']}, 高度={self.roi_coordinates['height']}")
        print(f"截圖保存: {'開啟' if self.save_screenshots else '關閉'}")
        print(f"提示窗顯示: {'開啟' if self.show_alerts else '關閉'}")
        print("按 Ctrl+C 停止監控")
        
        # 自動開啟HTML報告
        if self.auto_open_html:
            self.open_html_in_browser()
        
        try:
            while self.running:
                roi_image = self.capture_roi()
                if roi_image:
                    self.monitoring_counter += 1
                    
                    # 保存截圖
                    screenshot_path = None
                    if self.save_screenshots:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                        screenshot_path = os.path.join(self.monitoring_session_folder, f"monitor_{self.monitoring_counter:03d}_{timestamp}.png")
                        roi_image.save(screenshot_path)
                    
                    result, raw_response = self.analyze_with_strategy(roi_image)
                    
                    # 檢查是否匹配成功，如果未保存截圖但匹配成功，強制保存
                    should_save_screenshot = self.save_screenshots or result.is_match
                    
                    # 如果需要保存但還未保存，現在保存
                    if should_save_screenshot and not screenshot_path:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                        screenshot_path = os.path.join(self.monitoring_session_folder, f"monitor_{self.monitoring_counter:03d}_{timestamp}.png")
                        roi_image.save(screenshot_path)
                    
                    # 保存分析結果（始終保存以支援HTML報告）
                    self.save_analysis_result(result, raw_response, screenshot_path, should_save_screenshot)
                    
                    # 格式化顯示資訊
                    match_details = self.format_match_info(result)
                    
                    if result.is_match:
                        print(f"[#{self.monitoring_counter}] [MATCH] 找到匹配！")
                        print(f"玩家: {result.player_name}, 物品: {', '.join([item['item_name'] for item in result.matched_items])}")
                        self.show_alert(match_details)
                    else:
                        print(f"[#{self.monitoring_counter}] [SCAN] 未找到匹配 (方法: {result.analysis_method}, 信心度: {result.confidence:.2f})")
                
                time.sleep(SCAN_INTERVAL)
                
        except KeyboardInterrupt:
            print(f"\n監控已停止 (共執行 {self.monitoring_counter} 次分析)")
            self.finalize_session()
            self.running = False
    
    def finalize_session(self):
        """結束會話並生成報告"""
        if self.real_time_merger:
            print("\n正在生成HTML合併報告...")
            
            # 生成完整的HTML報告（不限制條目數量）
            html_path = self.generate_complete_html_report()
            
            if html_path:
                # 顯示統計信息
                total_results = len(self.real_time_merger.merged_results)
                matches = sum(1 for r in self.real_time_merger.merged_results 
                            if r.get('has_match', False))
                
                print(f"\n{'='*50}")
                print(f"監控會話完成報告")
                print(f"{'='*50}")
                print(f"會話資料夾: {self.monitoring_session_folder}")
                print(f"總分析次數: {total_results}")
                print(f"找到匹配: {matches} 次")
                print(f"匹配率: {matches/total_results*100:.1f}%" if total_results > 0 else "匹配率: 0%")
                print(f"分析方法: {self.analyzer.__class__.__name__}")
                print(f"HTML報告: {html_path}")
                print(f"{'='*50}")
                
                # 自動開啟HTML報告
                try:
                    webbrowser.open(f"file://{os.path.abspath(html_path)}")
                    print("HTML報告已自動開啟")
                except Exception as e:
                    print(f"無法自動開啟HTML報告: {e}")
                    print(f"請手動開啟: {html_path}")
            else:
                print("生成HTML報告失敗")
    
    def generate_complete_html_report(self):
        """生成完整的HTML報告，顯示所有結果"""
        if not self.real_time_merger:
            return None
            
        try:
            # 使用自定義HTML生成，不限制條目數量
            html_content = self.create_unlimited_html_report()
            
            html_path = os.path.join(self.monitoring_session_folder, "complete_monitoring_report.html")
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return html_path
        except Exception as e:
            print(f"生成HTML報告錯誤: {e}")
            return None
    
    def create_unlimited_html_report(self):
        """創建不限制條目數量的HTML報告"""
        import base64
        
        total_results = len(self.real_time_merger.merged_results)
        matches = sum(1 for r in self.real_time_merger.merged_results 
                     if r.get('has_match', False))
        
        # 按test_id排序
        sorted_results = sorted(self.real_time_merger.merged_results, 
                              key=lambda x: x.get('test_id', 0))
        
        html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>螢幕監控完整報告</title>
    <style>
        body {{
            font-family: 'Microsoft JhengHei', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .container {{
            display: grid;
            gap: 20px;
        }}
        .result-card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .result-card.match {{
            border-left: 5px solid #4CAF50;
        }}
        .result-card.no-match {{
            border-left: 5px solid #f44336;
        }}
        .result-card.error {{
            border-left: 5px solid #ff9800;
        }}
        .result-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        .result-id {{
            font-size: 1.2em;
            font-weight: bold;
        }}
        .timestamp {{
            color: #666;
            font-size: 0.9em;
        }}
        .screenshot {{
            text-align: center;
            margin-bottom: 15px;
        }}
        .screenshot img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            cursor: pointer;
            transition: transform 0.3s ease;
        }}
        .screenshot img:hover {{
            transform: scale(1.05);
        }}
        .analysis-info {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 15px;
        }}
        .info-item {{
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }}
        .info-label {{
            font-weight: bold;
            color: #555;
            font-size: 0.9em;
        }}
        .info-value {{
            margin-top: 5px;
        }}
        .match-details {{
            background-color: #e8f5e8;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #4CAF50;
            margin-bottom: 10px;
        }}
        .match-time {{
            background-color: #f0f8ff;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #2196F3;
            margin-bottom: 10px;
            text-align: center;
            font-weight: bold;
        }}
        .error-details {{
            background-color: #fff3e0;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #ff9800;
        }}
        .full-text {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
            word-break: break-all;
        }}
        @media (max-width: 768px) {{
            .analysis-info {{
                grid-template-columns: 1fr;
            }}
        }}
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.9);
        }}
        .modal-content {{
            display: block;
            margin: auto;
            max-width: 90%;
            max-height: 90%;
            margin-top: 5%;
        }}
        .close {{
            position: absolute;
            top: 15px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🖥️ 螢幕監控完整報告</h1>
        <p>完整顯示所有 {total_results} 次分析結果</p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-number">{total_results}</div>
            <div>總分析次數</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{matches}</div>
            <div>找到匹配</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{matches/total_results*100:.1f}%</div>
            <div>匹配率</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{self.analyzer.__class__.__name__}</div>
            <div>分析方法</div>
        </div>
    </div>
    
    <div class="container">
"""
        
        # 生成每個結果的HTML
        for data in sorted_results:
            test_id = data.get('test_id', 0)
            result = data.get('analysis_result', {})
            error_info = data.get('error_info', {})
            screenshot_path = data.get('screenshot_filename', '')
            
            # 確定卡片類型
            if error_info:
                card_class = "error"
                status_icon = "[ERROR]"
                status_text = f"錯誤: {error_info.get('error', '未知錯誤')}"
            elif data.get('has_match', False):
                card_class = "match"
                status_icon = "[OK]"
                status_text = "找到匹配"
            else:
                card_class = "no-match"
                status_icon = "[NO]"
                status_text = "未找到匹配"
            
            # 處理截圖
            screenshot_html = ""
            image_base64 = data.get('image_base64')
            if image_base64:
                screenshot_html = f'<div class="screenshot"><img src="data:image/png;base64,{image_base64}" alt="分析截圖" onclick="openModal(this)"></div>'
            elif screenshot_path:
                full_screenshot_path = os.path.join(self.monitoring_session_folder, screenshot_path)
                if os.path.exists(full_screenshot_path):
                    try:
                        with open(full_screenshot_path, "rb") as img_file:
                            img_data = base64.b64encode(img_file.read()).decode()
                        screenshot_html = f'<div class="screenshot"><img src="data:image/png;base64,{img_data}" alt="分析截圖" onclick="openModal(this)"></div>'
                    except Exception as e:
                        screenshot_html = f'<div class="screenshot"><p>截圖載入失敗: {e}</p></div>'
                else:
                    screenshot_html = f'<div class="screenshot"><p>截圖檔案不存在: {screenshot_path}</p></div>'
            
            # 生成分析詳情
            analysis_html = ""
            if result:
                confidence = result.get('confidence', 0)
                player_name = result.get('player_name', '未知')
                channel_number = result.get('channel_number', '未知')
                full_text = result.get('full_text', '')
                matched_items = result.get('matched_items', [])
                
                # 格式化時間戳為可讀的時間
                timestamp = data.get('timestamp', '')
                formatted_time = '未知時間'
                if timestamp:
                    try:
                        # 嘗試解析時間戳格式 YYYYMMDD_HHMMSS_mmm
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
                        else:
                            formatted_time = timestamp
                    except:
                        formatted_time = timestamp
                
                analysis_html = f"""
                <div class="analysis-info">
                    <div class="info-item">
                        <div class="info-label">玩家名稱</div>
                        <div class="info-value">{player_name}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">頻道編號</div>
                        <div class="info-value">{channel_number}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">信心度</div>
                        <div class="info-value">{confidence:.3f}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">分析方法</div>
                        <div class="info-value">{result.get('analysis_method', '未知')}</div>
                    </div>
                </div>
                """
                
                if matched_items:
                    items_text = ", ".join([item.get('item_name', '未知') for item in matched_items])
                    analysis_html += f'<div class="match-details"><strong>匹配物品:</strong> {items_text}</div>'
                
                # 在商品內容和完整廣播之間添加時間欄位
                if result.get('is_match', False):  # 只在匹配成功時顯示
                    analysis_html += f'<div class="match-time"><strong>匹配時間:</strong> {formatted_time}</div>'
                
                if full_text:
                    analysis_html += f'<div class="full-text"><strong>完整廣播:</strong><br>{full_text}</div>'
            elif error_info:
                analysis_html = f'<div class="error-details"><strong>錯誤詳情:</strong> {error_info.get("error", "未知錯誤")}</div>'
            
            html_content += f"""
        <div class="result-card {card_class}">
            <div class="result-header">
                <div class="result-id">{status_icon} 分析 #{test_id}</div>
                <div class="timestamp">{data.get('timestamp', '未知時間')}</div>
            </div>
            <div style="margin-bottom: 10px;"><strong>{status_text}</strong></div>
            {screenshot_html}
            {analysis_html}
        </div>
            """
        
        html_content += """
    </div>

    <!-- Modal for image viewing -->
    <div id="imageModal" class="modal">
        <span class="close" onclick="closeModal()">&times;</span>
        <img class="modal-content" id="modalImage">
    </div>

    <script>
        function openModal(img) {
            var modal = document.getElementById('imageModal');
            var modalImg = document.getElementById('modalImage');
            modal.style.display = 'block';
            modalImg.src = img.src;
        }

        function closeModal() {
            document.getElementById('imageModal').style.display = 'none';
        }

        // Close modal when clicking outside the image
        window.onclick = function(event) {
            var modal = document.getElementById('imageModal');
            if (event.target == modal) {
                closeModal();
            }
        }
    </script>
</body>
</html>
"""
        
        return html_content

    def stop_monitoring(self):
        """停止監控"""
        self.running = False
        if self.save_screenshots:
            self.finalize_session()

def get_analyzer_choice():
    """自動使用OCR_Rectangle分析器"""
    print("\n使用 OCR_Rectangle 分析引擎 (白框檢測視覺分割)")
    return "ocr_rectangle"

def create_analyzer(analyzer_type: str):
    """創建分析器實例"""
    if analyzer_type == "ocr_rectangle":
        try:
            # 從config.py讀取調試設定
            from config import OCR_DEBUG_CONFIG
            save_debug = OCR_DEBUG_CONFIG.get("ENABLE_RECTANGLE_DEBUG", False)
            debug_dir = OCR_DEBUG_CONFIG.get("DEBUG_OUTPUT_DIR", "rectangle_debug")
            return OCRRectangleAnalyzer(SELLING_ITEMS, BUYING_ITEMS, save_debug_images=save_debug, debug_folder=debug_dir)
        except ImportError as e:
            print(f"❌ OCR_Rectangle依賴缺失: {e}")
            print("\n安裝OCR依賴：")
            print("方法1 (推薦)：pip install -r requirements.txt")
            print("方法2 (手動安裝)：pip install easyocr opencv-python")
            print("\n注意：首次使用OCR會自動下載語言模型，需要網路連線")
            return None
        except Exception as e:
            print(f"❌ OCR_Rectangle初始化失敗: {e}")
            return None
    
    elif analyzer_type == "gemini":
        if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
            print("錯誤：請先在 config.py 中設置您的 Gemini API Key")
            return None
        try:
            return GeminiAnalyzer(GEMINI_API_KEY, SELLING_ITEMS, BUYING_ITEMS)
        except Exception as e:
            print(f"Gemini分析器初始化失敗: {e}")
            return None
    
    elif analyzer_type == "ocr":
        try:
            return OCRAnalyzer(SELLING_ITEMS, BUYING_ITEMS)
        except ImportError as e:
            print(f"❌ OCR依賴缺失: {e}")
            print("\n安裝OCR依賴：")
            print("方法1 (推薦)：pip install -r requirements_ocr.txt")
            print("方法2 (最小安裝)：pip install easyocr")
            print("\n注意：首次使用OCR會自動下載語言模型，需要網路連線")
            return None
        except Exception as e:
            print(f"❌ OCR初始化失敗: {e}")
            return None
    
    return None

def get_user_settings():
    """獲取使用者設定"""
    print("螢幕監控程式 - 初始設定")
    print("=" * 40)
    
    # 選擇分析方法
    analyzer_type = get_analyzer_choice()
    
    # 詢問是否保存截圖
    while True:
        save_choice = input("\n是否保存截圖供debug使用？(y/n): ").lower().strip()
        if save_choice in ['y', 'yes', '是']:
            save_screenshots = True
            break
        elif save_choice in ['n', 'no', '否']:
            save_screenshots = False
            break
        else:
            print("請輸入 y 或 n")
    
    # 詢問是否顯示提示窗
    while True:
        alert_choice = input("是否顯示匹配提示窗？(y/n): ").lower().strip()
        if alert_choice in ['y', 'yes', '是']:
            show_alerts = True
            break
        elif alert_choice in ['n', 'no', '否']:
            show_alerts = False
            break
        else:
            print("請輸入 y 或 n")
    
    # 預設自動開啟HTML報告
    auto_open_html = True
    
    # ROI選擇
    print("\n請選擇監控區域（ROI）...")
    print("即將顯示全螢幕截圖，請用滑鼠拖拉選擇監控區域")
    input("按Enter開始選擇ROI...")
    
    selector = ROISelector()
    roi_coordinates = selector.select_roi()
    
    if roi_coordinates is None:
        print("未選擇ROI區域，程式結束")
        return None, None, None, None, None
    
    print(f"\n已選擇ROI: {roi_coordinates}")
    print(f"分析方法: {analyzer_type}")
    print(f"截圖保存: {'開啟' if save_screenshots else '關閉'}")
    print(f"提示窗顯示: {'開啟' if show_alerts else '關閉'}")
    print("HTML報告: 自動開啟 (預設)")
    
    return roi_coordinates, analyzer_type, save_screenshots, show_alerts, auto_open_html

def main():
    """主程式"""
    # 獲取使用者設定
    roi_coordinates, analyzer_type, save_screenshots, show_alerts, auto_open_html = get_user_settings()
    if roi_coordinates is None:
        return
    
    # 創建分析器
    analyzer = create_analyzer(analyzer_type)
    if analyzer is None:
        return
    
    # 創建監控器
    monitor = ScreenMonitor(roi_coordinates, analyzer, save_screenshots, show_alerts, auto_open_html)
    
    print("\n螢幕監控程式")
    print("=" * 40)
    print("監控商品:")
    for item_name, keywords in SELLING_ITEMS.items():
        print(f"  - {item_name}")
        print(f"    關鍵字: {', '.join(keywords)}")
    print("=" * 40)
    
    monitor.start_monitoring()

if __name__ == "__main__":
    main()