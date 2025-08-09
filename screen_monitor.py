import pyautogui
import time
import tkinter as tk
from tkinter import messagebox
import os
import json
import numpy as np
from datetime import datetime
from config import *
from roi_selector import ROISelector
from text_analyzer import AnalysisResult
from gemini_analyzer import GeminiAnalyzer
from ocr_analyzer import OCRAnalyzer

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
    
    def __init__(self, roi_coordinates, analyzer, save_screenshots=False, show_alerts=True):
        self.roi_coordinates = roi_coordinates
        self.analyzer = analyzer
        self.save_screenshots = save_screenshots
        self.show_alerts = show_alerts
        self.running = False
        
        # 如果需要保存截圖，創建資料夾
        if self.save_screenshots:
            if not os.path.exists(SCREENSHOT_FOLDER):
                os.makedirs(SCREENSHOT_FOLDER)
            print(f"截圖將保存到: {SCREENSHOT_FOLDER}")
        
    def capture_roi(self):
        try:
            # 先截取全螢幕
            full_screenshot = pyautogui.screenshot()
            
            # 如果需要保存全螢幕截圖
            if self.save_screenshots:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                full_path = os.path.join(SCREENSHOT_FOLDER, f"full_{timestamp}.png")
                full_screenshot.save(full_path)
                print(f"已保存全螢幕截圖: {full_path}")
            
            # 截取ROI區域
            roi_screenshot = pyautogui.screenshot(
                region=(
                    self.roi_coordinates["x"],
                    self.roi_coordinates["y"], 
                    self.roi_coordinates["width"],
                    self.roi_coordinates["height"]
                )
            )
            
            # 如果需要保存ROI截圖
            if self.save_screenshots:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                roi_path = os.path.join(SCREENSHOT_FOLDER, f"roi_{timestamp}.png")
                roi_screenshot.save(roi_path)
                print(f"已保存ROI截圖: {roi_path}")
            
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
            
            match_info = f"""✓ 找到匹配！
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
            no_match_info = f"""⋅ 未找到匹配
分析方法: {result.analysis_method}
信心度: {result.confidence:.2f}
頻道編號: {result.channel_number}

完整文字內容:
{result.full_text}"""
            return no_match_info
    
    def save_analysis_result(self, result: AnalysisResult, raw_response: str):
        """保存分析結果"""
        if self.save_screenshots:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 保存結構化結果
            result_path = os.path.join(SCREENSHOT_FOLDER, f"analysis_{timestamp}.json")
            analysis_data = {
                "timestamp": timestamp,
                "analysis_method": result.analysis_method,
                "result": convert_to_json_serializable(result.to_dict()),
                "raw_response": convert_to_json_serializable(raw_response)
            }
            
            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, ensure_ascii=False, indent=2)
            
            print(f"已保存分析結果: {result_path}")
    
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
        
        try:
            while self.running:
                roi_image = self.capture_roi()
                if roi_image:
                    result, raw_response = self.analyze_with_strategy(roi_image)
                    
                    # 保存分析結果
                    self.save_analysis_result(result, raw_response)
                    
                    # 格式化顯示資訊
                    match_details = self.format_match_info(result)
                    
                    if result.is_match:
                        print("✓ 找到匹配！")
                        print(f"詳情: {match_details}")
                        self.show_alert(match_details)
                    else:
                        print("⋅ 未找到完整匹配")
                        print(f"分析方法: {result.analysis_method}, 信心度: {result.confidence:.2f}")
                
                time.sleep(SCAN_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n監控已停止")
            self.running = False
    
    def stop_monitoring(self):
        self.running = False

def get_analyzer_choice():
    """獲取分析器選擇"""
    print("\n請選擇文字分析方法：")
    print("1. Gemini AI (需要API Key，準確度高)")
    print("2. OCR (本地處理，速度快)")
    
    while True:
        choice = input("請輸入選項 (1 或 2): ").strip()
        if choice == "1":
            return "gemini"
        elif choice == "2":
            return "ocr"
        else:
            print("請輸入 1 或 2")

def create_analyzer(analyzer_type: str):
    """創建分析器實例"""
    if analyzer_type == "gemini":
        if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
            print("錯誤：請先在 config.py 中設置您的 Gemini API Key")
            return None
        try:
            return GeminiAnalyzer(GEMINI_API_KEY, SELLING_ITEMS)
        except Exception as e:
            print(f"Gemini分析器初始化失敗: {e}")
            return None
    
    elif analyzer_type == "ocr":
        try:
            return OCRAnalyzer(SELLING_ITEMS)
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
    
    # ROI選擇
    print("\n請選擇監控區域（ROI）...")
    print("即將顯示全螢幕截圖，請用滑鼠拖拉選擇監控區域")
    input("按Enter開始選擇ROI...")
    
    selector = ROISelector()
    roi_coordinates = selector.select_roi()
    
    if roi_coordinates is None:
        print("未選擇ROI區域，程式結束")
        return None, None, None, None
    
    print(f"\n已選擇ROI: {roi_coordinates}")
    print(f"分析方法: {analyzer_type}")
    print(f"截圖保存: {'開啟' if save_screenshots else '關閉'}")
    print(f"提示窗顯示: {'開啟' if show_alerts else '關閉'}")
    
    return roi_coordinates, analyzer_type, save_screenshots, show_alerts

def main():
    """主程式"""
    # 獲取使用者設定
    roi_coordinates, analyzer_type, save_screenshots, show_alerts = get_user_settings()
    if roi_coordinates is None:
        return
    
    # 創建分析器
    analyzer = create_analyzer(analyzer_type)
    if analyzer is None:
        return
    
    # 創建監控器
    monitor = ScreenMonitor(roi_coordinates, analyzer, save_screenshots, show_alerts)
    
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