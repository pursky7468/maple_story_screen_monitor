#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合併功能演示程式"""

import os
import sys
from pathlib import Path

# 設置控制台編碼
if sys.platform == "win32":
    os.system('chcp 65001 > nul')

def demo_real_time_merger():
    """演示實時合併功能"""
    print("=== 實時合併功能演示 ===")
    print()
    
    try:
        from real_time_merger import RealTimeMerger
        from text_analyzer import AnalysisResult
        from PIL import Image, ImageDraw
        import numpy as np
        import tempfile
        
        # 創建演示資料夾
        demo_folder = "demo_test_results"
        if os.path.exists(demo_folder):
            import shutil
            shutil.rmtree(demo_folder)
        os.makedirs(demo_folder)
        
        # 創建合併器
        merger = RealTimeMerger(demo_folder)
        
        print("1. 創建測試截圖和分析結果...")
        
        # 創建幾個演示測試
        demo_tests = [
            {
                "text": "CHO123: 收購披風幸運60%卷軸，價格好商量",
                "match": True,
                "player": "玩家甲",
                "channel": "CHO123",
                "items": ["披風幸運60%"]
            },
            {
                "text": "CHO456: 賣武器攻擊力30%卷軸，便宜出售",
                "match": False,
                "player": "玩家乙", 
                "channel": "CHO456",
                "items": []
            },
            {
                "text": "CHO789: 收購母礦，大量收購，私聊價格",
                "match": True,
                "player": "玩家丙",
                "channel": "CHO789", 
                "items": ["母礦"]
            }
        ]
        
        for i, test_data in enumerate(demo_tests, 1):
            # 創建測試圖片
            img = Image.new('RGB', (500, 80), 'white')
            draw = ImageDraw.Draw(img)
            
            try:
                # 嘗試使用系統字體
                from PIL import ImageFont
                font = ImageFont.truetype("arial.ttf", 16)
            except:
                # 使用預設字體
                from PIL import ImageFont
                font = ImageFont.load_default()
            
            draw.text((10, 30), test_data["text"], fill='black', font=font)
            
            # 保存截圖
            screenshot_path = os.path.join(demo_folder, f"demo_test_{i:03d}_screenshot.png")
            img.save(screenshot_path)
            
            # 創建分析結果
            result = AnalysisResult(
                full_text=test_data["text"],
                is_match=test_data["match"],
                player_name=test_data["player"],
                channel_number=test_data["channel"],
                matched_items=[{"item_name": item, "keywords_found": ["收購", item]} for item in test_data["items"]],
                matched_keywords=["收購"] + test_data["items"] if test_data["match"] else [],
                confidence=np.random.uniform(0.7, 0.95),
                analysis_method="DemoAnalyzer"
            )
            
            # 添加到合併器
            merger.add_test_result(i, screenshot_path, result.to_dict(), None)
            print(f"   測試 {i}: {'[MATCH] 找到匹配' if test_data['match'] else '[NO MATCH] 未匹配'}")
        
        print("\n2. 生成合併報告...")
        
        # 生成HTML查看器
        merger.generate_quick_html()
        
        html_file = Path(demo_folder) / "quick_view.html"
        json_file = Path(demo_folder) / "combined_results.json"
        
        print(f"\n[OK] 演示完成！生成的文件：")
        print(f"   HTML查看器: {html_file}")
        print(f"   JSON數據: {json_file}")
        print(f"   測試截圖: {len(demo_tests)} 個")
        
        print(f"\n試試看：")
        print(f"   1. 用瀏覽器打開: {html_file}")
        print(f"   2. 點擊圖片可以放大查看")
        print(f"   3. 使用篩選按鈕查看不同類型的結果")
        
        return True
        
    except Exception as e:
        print(f"演示失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def demo_existing_results():
    """演示處理現有結果"""
    print("\n=== 現有結果處理演示 ===")
    print()
    
    current_dir = Path(".")
    test_folders = list(current_dir.glob("integration_test_*"))
    
    if test_folders:
        print(f"找到 {len(test_folders)} 個現有測試資料夾：")
        for folder in sorted(test_folders)[:3]:  # 只顯示前3個
            print(f"   {folder.name}")
        
        print(f"\n你可以運行以下命令來處理現有結果：")
        print(f"   python test_results_merger.py")
        print(f"\n該工具會：")
        print(f"   • 自動掃描所有測試資料夾")
        print(f"   • 讓你選擇要處理的資料夾")
        print(f"   • 生成完整的HTML報告")
        
    else:
        print("沒有找到現有的測試資料夾（integration_test_*）")
        print("運行 python integration_test.py 來創建一些測試結果")

def show_usage_summary():
    """顯示使用總結"""
    print("\n=== 使用總結 ===")
    print()
    print("兩種使用方式：")
    print()
    print("方式1: 自動合併（推薦）")
    print("   - 運行: python integration_test.py")
    print("   - 自動生成: quick_view.html")
    print("   - 實時記錄測試結果和截圖")
    print()
    print("方式2: 處理現有結果")
    print("   - 運行: python test_results_merger.py") 
    print("   - 處理已存在的測試資料夾")
    print("   - 生成完整的HTML報告")
    print()
    print("主要優勢：")
    print("   - 圖片和結果自動對應，無需手動查找")
    print("   - 瀏覽器直接查看，支持圖片放大")
    print("   - 智能篩選功能，快速找到問題")
    print("   - 統計摘要一目了然")
    print()
    print("調試建議：")
    print("   1. 先查看統計摘要了解整體情況")
    print("   2. 使用篩選功能定位問題測試")
    print("   3. 點擊圖片放大查看細節")
    print("   4. 查看詳細信息了解分析結果")

def main():
    """主程式"""
    print("測試結果合併功能演示")
    print("=" * 50)
    
    try:
        # 演示實時合併功能
        demo_success = demo_real_time_merger()
        
        # 演示現有結果處理
        demo_existing_results()
        
        # 顯示使用總結
        show_usage_summary()
        
        if demo_success:
            print(f"\n演示成功完成！")
            print(f"查看 demo_test_results/quick_view.html 來體驗合併功能")
        
    except KeyboardInterrupt:
        print("\n演示被中斷")
    except Exception as e:
        print(f"\n演示過程中發生錯誤: {e}")

if __name__ == "__main__":
    main()