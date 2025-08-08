import tkinter as tk
from tkinter import messagebox
import pyautogui
from PIL import Image, ImageTk
import threading

class ROISelector:
    def __init__(self):
        self.roi_coordinates = None
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0
        self.selection_active = False
        
    def select_roi(self):
        """讓使用者在螢幕上拖拉選擇ROI區域"""
        # 先截取全螢幕
        screenshot = pyautogui.screenshot()
        
        # 創建全螢幕視窗
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.configure(cursor='crosshair')
        
        # 將截圖轉換為Tkinter可用的格式
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        screenshot = screenshot.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(screenshot)
        
        # 創建Canvas
        self.canvas = tk.Canvas(
            self.root, 
            width=screen_width, 
            height=screen_height,
            highlightthickness=0
        )
        self.canvas.pack()
        
        # 顯示截圖
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        
        # 綁定滑鼠事件
        self.canvas.bind('<Button-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        
        # 綁定ESC鍵取消
        self.root.bind('<Escape>', self.cancel_selection)
        
        # 顯示說明文字
        self.instruction_text = self.canvas.create_text(
            screen_width // 2, 50,
            text="拖拉滑鼠選擇監控區域，按ESC取消",
            fill="red",
            font=("Arial", 16, "bold")
        )
        
        self.root.mainloop()
        return self.roi_coordinates
    
    def on_mouse_down(self, event):
        """滑鼠按下事件"""
        self.start_x = event.x
        self.start_y = event.y
        self.selection_active = True
        
        # 清除之前的選擇框
        self.canvas.delete("selection_rect")
    
    def on_mouse_drag(self, event):
        """滑鼠拖拉事件"""
        if self.selection_active:
            # 清除之前的選擇框
            self.canvas.delete("selection_rect")
            
            # 畫新的選擇框
            self.canvas.create_rectangle(
                self.start_x, self.start_y,
                event.x, event.y,
                outline="red",
                width=3,
                tags="selection_rect"
            )
            
            # 顯示座標信息
            self.canvas.delete("coord_text")
            coord_text = f"起點: ({self.start_x}, {self.start_y}) 當前: ({event.x}, {event.y})"
            self.canvas.create_text(
                self.start_x, self.start_y - 20,
                text=coord_text,
                fill="red",
                font=("Arial", 12),
                tags="coord_text",
                anchor=tk.W
            )
    
    def on_mouse_up(self, event):
        """滑鼠放開事件"""
        if self.selection_active:
            self.end_x = event.x
            self.end_y = event.y
            self.selection_active = False
            
            # 確保座標是正確的
            x1 = min(self.start_x, self.end_x)
            y1 = min(self.start_y, self.end_y)
            x2 = max(self.start_x, self.end_x)
            y2 = max(self.start_y, self.end_y)
            
            width = x2 - x1
            height = y2 - y1
            
            if width > 10 and height > 10:  # 最小尺寸檢查
                self.roi_coordinates = {
                    "x": x1,
                    "y": y1,
                    "width": width,
                    "height": height
                }
                
                # 顯示確認信息
                confirm_text = f"ROI選擇完成: ({x1}, {y1}) 尺寸: {width}x{height}\\n按任意鍵確認，ESC取消"
                self.canvas.delete("confirm_text")
                self.canvas.create_text(
                    x1 + width // 2, y1 + height // 2,
                    text=confirm_text,
                    fill="yellow",
                    font=("Arial", 14, "bold"),
                    tags="confirm_text"
                )
                
                # 綁定任意鍵確認
                self.root.bind('<Key>', self.confirm_selection)
            else:
                # 選擇區域太小
                self.canvas.create_text(
                    event.x, event.y,
                    text="選擇區域太小，請重新選擇",
                    fill="red",
                    font=("Arial", 12)
                )
    
    def confirm_selection(self, event):
        """確認選擇"""
        if event.keysym != 'Escape':
            self.root.quit()
            self.root.destroy()
    
    def cancel_selection(self, event):
        """取消選擇"""
        self.roi_coordinates = None
        self.root.quit()
        self.root.destroy()


def test_roi_selector():
    """測試ROI選擇器"""
    selector = ROISelector()
    result = selector.select_roi()
    if result:
        print(f"選擇的ROI: {result}")
    else:
        print("已取消選擇")


if __name__ == "__main__":
    test_roi_selector()