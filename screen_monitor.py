import pyautogui
import time
import google.generativeai as genai
from PIL import Image
import tkinter as tk
from tkinter import messagebox
import io
import base64
import os
import json
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
            你是一位楓之谷遊戲中的商人，
            你負責把你手中的{GROUP1_KEYWORDS}賣出。
            請分析這張圖片中的所有文字內容，並檢查是否有玩家在收購{GROUP1_KEYWORDS}。
            請以JSON格式回傳分析結果，格式如下：
            {{
                "full_text": "圖片中的完整文字內容",
                "is_match": true/false,
                "player_name": "玩家名稱（如果有匹配的話）",
                "channel_number": "頻道編號（通常在文字開頭）",
                "matched_keywords": ["找到的關鍵字列表"]
            }}
            
            注意事項：
            - full_text 必須包含圖片中所有識別到的文字
            - is_match 判斷是否有人在收購目標物品：{GROUP1_KEYWORDS}
            - player_name 提取說話者的玩家名稱
            - channel_number 提取頻道編號（通常格式如 [頻道1] 或 ch1 等）
            - matched_keywords 列出實際找到的相關關鍵字
            - 你必須嚴格確認百分比的數字內容，例如如果你要賣的東西是披風幸運60%，但玩家是要收購披風幸運10%，這是不成立匹配。
            
            請確保回傳的是有效的JSON格式，不要包含任何其他文字。
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
    
    def extract_json_from_response(self, response_text):
        """從回應中提取JSON內容"""
        # 移除可能的markdown代碼塊標記
        response_text = response_text.strip()
        
        # 檢查是否有```json代碼塊
        if response_text.startswith('```json'):
            # 找到開始和結束位置
            start_marker = '```json'
            end_marker = '```'
            
            start_idx = response_text.find(start_marker) + len(start_marker)
            end_idx = response_text.rfind(end_marker)
            
            if start_idx > len(start_marker) - 1 and end_idx > start_idx:
                json_content = response_text[start_idx:end_idx].strip()
            else:
                # 如果沒找到結束標記，取開始標記之後的所有內容
                json_content = response_text[start_idx:].strip()
        elif response_text.startswith('```'):
            # 處理其他類型的代碼塊
            lines = response_text.split('\n')
            json_lines = []
            in_code_block = False
            
            for line in lines:
                if line.strip().startswith('```') and not in_code_block:
                    in_code_block = True
                elif line.strip() == '```' and in_code_block:
                    break
                elif in_code_block:
                    json_lines.append(line)
            
            json_content = '\n'.join(json_lines).strip()
        else:
            # 沒有代碼塊，直接使用原始內容
            json_content = response_text
        
        # 嘗試找到JSON對象的開始和結束
        json_start = json_content.find('{')
        json_end = json_content.rfind('}')
        
        if json_start >= 0 and json_end > json_start:
            json_content = json_content[json_start:json_end + 1]
        
        return json_content

    def check_keyword_match(self, analysis_result):
        """解析JSON格式的分析結果"""
        try:
            # 先提取JSON內容
            json_content = self.extract_json_from_response(analysis_result)
            print(f"提取的JSON內容: {json_content}")
            
            # 解析JSON
            result_data = json.loads(json_content)
            
            # 直接從JSON中獲取匹配結果
            full_text = result_data.get("full_text", "")
            is_match = result_data.get("is_match", False)
            player_name = result_data.get("player_name", "未知")
            channel_number = result_data.get("channel_number", "未知")
            matched_keywords = result_data.get("matched_keywords", [])
            
            # 格式化顯示資訊
            if is_match:
                match_info = f"""✓ 找到匹配！
玩家名稱: {player_name}
頻道編號: {channel_number}
匹配關鍵字: {', '.join(matched_keywords)}

完整文字內容:
{full_text}"""
                return True, match_info
            else:
                no_match_info = f"""⋅ 未找到匹配
頻道編號: {channel_number}

完整文字內容:
{full_text}"""
                return False, no_match_info
                
        except json.JSONDecodeError as e:
            print(f"JSON解析失敗: {e}")
            print(f"嘗試解析的內容: {json_content if 'json_content' in locals() else analysis_result}")
            return False, f"JSON解析失敗\n\nGemini原始回應:\n{analysis_result}"
        
        except Exception as e:
            print(f"解析結果時發生錯誤: {e}")
            return False, f"解析錯誤: {str(e)}\n\n原始回應:\n{analysis_result}"
    
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
                    print("Gemini原始回應:", analysis)
                    
                    # 如果開啟截圖保存，也保存JSON分析結果
                    if self.save_screenshots:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        json_path = os.path.join(SCREENSHOT_FOLDER, f"analysis_{timestamp}.json")
                        try:
                            # 嘗試解析並格式化JSON
                            json_data = json.loads(analysis)
                            with open(json_path, 'w', encoding='utf-8') as f:
                                json.dump(json_data, f, ensure_ascii=False, indent=2)
                            print(f"已保存分析結果: {json_path}")
                        except json.JSONDecodeError:
                            # 如果不是有效JSON，保存原始文字
                            with open(json_path.replace('.json', '.txt'), 'w', encoding='utf-8') as f:
                                f.write(analysis)
                    
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