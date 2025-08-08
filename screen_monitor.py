import pyautogui
import time
import google.generativeai as genai
from PIL import Image
import tkinter as tk
from tkinter import messagebox
import io
import base64
import os
from datetime import datetime
from config import *
from roi_selector import ROISelector

class ScreenMonitor:
    def __init__(self, roi_coordinates, save_screenshots=False):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.running = False
        self.roi_coordinates = roi_coordinates
        self.save_screenshots = save_screenshots
        
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
    
    def analyze_text_with_gemini(self, image):
        try:
            # 將PIL圖片轉換為bytes
            import io
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            prompt = f"""
            妳是一位楓之谷遊戲的交易商，你需要把你身上的庫存賣出，
            現在你想要把你身上的{GROUP1_KEYWORDS}的卷軸賣個好價錢
            請分析這張圖片中的所有文字內容，並檢查這位玩家是否在收購{GROUP1_KEYWORDS}。
            不需要加入你的推理過程和內容，
            回覆的內容只需要圖片上的完整文字，
            如果有match{GROUP1_KEYWORDS}的話，請強調玩家的名稱和頻道編號
            其中頻道編號一般會在文字的最開頭。
            """
            
            # 使用新的API格式
            response = self.model.generate_content([
                prompt,
                {
                    "mime_type": "image/png",
                    "data": img_byte_arr
                }
            ])
            return response.text.strip()
            
        except Exception as e:
            print(f"Gemini分析錯誤: {e}")
            return "ERROR"
    
    def check_keyword_match(self, analysis_result):
        """檢查分析結果中是否包含目標關鍵字"""
        analysis_upper = analysis_result.upper()
        
        # 檢查是否包含任何目標關鍵字
        found_keywords = []
        for keyword in GROUP1_KEYWORDS:
            if keyword.upper() in analysis_upper:
                found_keywords.append(keyword)
        
        if found_keywords:
            return True, f"找到關鍵字: {', '.join(found_keywords)}\n\nGemini分析結果:\n{analysis_result}"
        else:
            return False, f"未找到目標關鍵字\n\nGemini分析結果:\n{analysis_result}"
    
    def show_alert(self, message):
        root = tk.Tk()
        root.withdraw()  
        messagebox.showinfo("匹配提醒", f"找到符合條件的內容！\n\n{message}")
        root.destroy()
    
    def start_monitoring(self):
        self.running = True
        print("開始監控螢幕...")
        print(f"ROI區域: x={self.roi_coordinates['x']}, y={self.roi_coordinates['y']}, "
              f"寬度={self.roi_coordinates['width']}, 高度={self.roi_coordinates['height']}")
        print(f"截圖保存: {'開啟' if self.save_screenshots else '關閉'}")
        print("按 Ctrl+C 停止監控")
        
        try:
            while self.running:
                roi_image = self.capture_roi()
                if roi_image:
                    analysis = self.analyze_text_with_gemini(roi_image)
                    print("分析結果:", analysis)
                    is_match, details = self.check_keyword_match(analysis)
                    
                    if is_match:
                        print("✓ 找到匹配！")
                        print(f"分析結果: {details}")
                        self.show_alert(details)
                    else:
                        print("⋅ 未找到完整匹配")
                
                time.sleep(SCAN_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n監控已停止")
            self.running = False
    
    def stop_monitoring(self):
        self.running = False

def get_user_settings():
    """獲取使用者設定"""
    print("螢幕監控程式 - 初始設定")
    print("=" * 40)
    
    # 詢問是否保存截圖
    while True:
        save_choice = input("是否保存截圖供debug使用？(y/n): ").lower().strip()
        if save_choice in ['y', 'yes', '是']:
            save_screenshots = True
            break
        elif save_choice in ['n', 'no', '否']:
            save_screenshots = False
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
        return None, None
    
    print(f"\n已選擇ROI: {roi_coordinates}")
    print(f"截圖保存: {'開啟' if save_screenshots else '關閉'}")
    
    return roi_coordinates, save_screenshots

def main():
    if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        print("請先在 config.py 中設置您的 Gemini API Key")
        return
    
    # 獲取使用者設定
    roi_coordinates, save_screenshots = get_user_settings()
    if roi_coordinates is None:
        return
    
    # 創建監控器
    monitor = ScreenMonitor(roi_coordinates, save_screenshots)
    
    print("\n螢幕監控程式")
    print("=" * 30)
    print("目標關鍵字:")
    print(f"搜尋內容: {', '.join(GROUP1_KEYWORDS)}")
    print("=" * 30)
    
    monitor.start_monitoring()

if __name__ == "__main__":
    main()