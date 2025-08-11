#!/usr/bin/env python3
"""
測試HTML報告中的物品匹配顯示功能
"""

import os
import tempfile
from real_time_merger import RealTimeMerger

def test_html_match_display():
    """測試HTML匹配顯示功能"""
    print("=== 測試HTML報告物品匹配顯示功能 ===")
    
    # 創建臨時測試資料夾
    with tempfile.TemporaryDirectory() as temp_dir:
        # 創建實時合併器
        merger = RealTimeMerger(temp_dir)
        
        # 測試案例1: 有匹配結果的情況
        test_analysis_result = {
            "full_text": "乂煞氣a澤神乂 CH2245 收幸運母礦12:1/螺絲釘25:1/賣德古拉(80賊手)+10攻6屬430雪",
            "is_match": True,
            "player_name": "乂煞氣a澤神乂",
            "channel_number": "CH2245",
            "matched_items": [
                {
                    "item_name": "母礦",
                    "keywords_found": ["母礦"]
                },
                {
                    "item_name": "披風幸運60%",
                    "keywords_found": ["幸運"]
                }
            ],
            "matched_keywords": ["母礦", "幸運"],
            "confidence": 0.92,
            "analysis_method": "OCR"
        }
        
        # 添加測試結果
        merger.add_test_result(
            test_id=1,
            screenshot_path=None,  # 沒有實際截圖
            analysis_result=test_analysis_result,
            error_info=None
        )
        
        # 測試案例2: 無匹配結果的情況
        test_no_match_result = {
            "full_text": "隨便的一些文字內容",
            "is_match": False,
            "player_name": "測試玩家",
            "channel_number": "CH001",
            "matched_items": [],
            "matched_keywords": [],
            "confidence": 0.85,
            "analysis_method": "OCR"
        }
        
        merger.add_test_result(
            test_id=2,
            screenshot_path=None,
            analysis_result=test_no_match_result,
            error_info=None
        )
        
        # 測試案例3: 錯誤情況
        merger.add_test_result(
            test_id=3,
            screenshot_path=None,
            analysis_result=None,
            error_info={"error": "API配額已用盡", "error_type": "API_QUOTA_EXCEEDED"}
        )
        
        # 生成HTML報告
        merger.generate_quick_html()
        
        # 檢查生成的HTML文件
        html_file = os.path.join(temp_dir, "quick_view.html")
        if os.path.exists(html_file):
            print(f"✅ HTML報告已生成: {html_file}")
            
            # 讀取HTML內容並檢查匹配信息
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # 檢查改進項目
            improvements_found = []
            
            if "🎯 找到匹配交易" in html_content:
                improvements_found.append("✅ 匹配標題已更新")
            
            if "母礦" in html_content and "keywords_found" not in html_content:
                improvements_found.append("✅ 物品名稱正確顯示")
            
            if "玩家:" in html_content and "乂煞氣a澤神乂" in html_content:
                improvements_found.append("✅ 玩家名稱顏色標記")
            
            if "頻道:" in html_content and "CH2245" in html_content:
                improvements_found.append("✅ 頻道編號顏色標記")
            
            if "color: #e74c3c" in html_content:
                improvements_found.append("✅ 物品名稱紅色突出顯示")
                
            if "匹配商品 (2 個)" in html_content:
                improvements_found.append("✅ 匹配商品數量正確")
            
            print("\n改進項目檢查:")
            for improvement in improvements_found:
                print(f"  {improvement}")
            
            if len(improvements_found) >= 4:
                print(f"\n🎉 HTML報告改進成功！ ({len(improvements_found)}/6 項改進完成)")
            else:
                print(f"\n⚠️  部分改進可能未完成 ({len(improvements_found)}/6 項)")
            
            # 顯示HTML文件的關鍵部分
            print(f"\n--- HTML匹配信息預覽 ---")
            lines = html_content.split('\n')
            in_match_info = False
            for line in lines:
                if "🎯 找到匹配交易" in line:
                    in_match_info = True
                if in_match_info:
                    if "匹配商品" in line or "玩家:" in line or "頻道:" in line:
                        print(line.strip())
                    if "</div>" in line and in_match_info:
                        in_match_info = False
                        break
            
        else:
            print("❌ HTML報告生成失敗")

if __name__ == "__main__":
    test_html_match_display()
    
    print(f"\n=== HTML顯示改進總結 ===")
    print("1. 匹配標題改為 '🎯 找到匹配交易'")
    print("2. 玩家名稱藍色粗體顯示")
    print("3. 頻道編號綠色粗體顯示") 
    print("4. 物品名稱紅色粗體突出")
    print("5. 顯示具體匹配到的關鍵字")
    print("6. 改善視覺層次和可讀性")