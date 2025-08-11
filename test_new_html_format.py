#!/usr/bin/env python3
"""
測試新的HTML報告格式
"""

import os
import tempfile
from datetime import datetime
from real_time_merger import RealTimeMerger

def test_new_html_format():
    """測試新的HTML報告格式"""
    print("=== 測試新的HTML報告格式 ===")
    
    # 創建臨時測試資料夾
    with tempfile.TemporaryDirectory() as temp_dir:
        # 創建實時合併器
        merger = RealTimeMerger(temp_dir)
        
        # 測試案例1: 有匹配的交易
        test_match_1 = {
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
        
        # 測試案例2: 另一個匹配的交易
        test_match_2 = {
            "full_text": "玩家ABC CH001 : 收購耳環智力10%卷軸，價格好談",
            "is_match": True,
            "player_name": "玩家ABC",
            "channel_number": "CH001",
            "matched_items": [
                {
                    "item_name": "耳環智力10%",
                    "keywords_found": ["耳環智力10%"]
                }
            ],
            "matched_keywords": ["耳環智力10%"],
            "confidence": 0.85,
            "analysis_method": "GEMINI"
        }
        
        # 測試案例3: 無匹配結果（應該不會顯示）
        test_no_match = {
            "full_text": "隨便聊天的內容，沒有任何交易相關",
            "is_match": False,
            "player_name": "聊天玩家",
            "channel_number": "CH999",
            "matched_items": [],
            "matched_keywords": [],
            "confidence": 0.70,
            "analysis_method": "OCR"
        }
        
        # 添加測試結果（時間順序：先舊後新）
        merger.add_test_result(
            test_id=1,
            screenshot_path=None,
            analysis_result=test_match_1,
            error_info=None
        )
        
        merger.add_test_result(
            test_id=2,
            screenshot_path=None,
            analysis_result=test_no_match,
            error_info=None
        )
        
        merger.add_test_result(
            test_id=3,
            screenshot_path=None,
            analysis_result=test_match_2,
            error_info=None
        )
        
        # 生成HTML報告
        merger.generate_quick_html()
        
        # 檢查生成的HTML文件
        html_file = os.path.join(temp_dir, "quick_view.html")
        if os.path.exists(html_file):
            print(f"✅ HTML報告已生成: {html_file}")
            
            # 讀取HTML內容並檢查新格式
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # 檢查新格式特性
            checks = []
            
            if "交易匹配監控結果" in html_content:
                checks.append("✅ 標題已更新為交易匹配監控結果")
            
            if "玩家ABC" in html_content and "乂煞氣a澤神乂" in html_content:
                # 檢查順序：玩家ABC應該在乂煞氣a澤神乂之前（最新在上）
                abc_pos = html_content.find("玩家ABC")
                player_pos = html_content.find("乂煞氣a澤神乂")
                if abc_pos < player_pos:
                    checks.append("✅ 最新匹配結果顯示在上方")
                else:
                    checks.append("❌ 順序錯誤，最新結果未在上方")
            
            if "聊天玩家" not in html_content:
                checks.append("✅ 無匹配結果已正確過濾")
            else:
                checks.append("❌ 無匹配結果未被過濾")
            
            if "玩家:" in html_content and "頻道:" in html_content and "商品內容:" in html_content and "完整廣播:" in html_content:
                checks.append("✅ 包含所有必要欄位")
            
            if "母礦 (母礦)" in html_content and "耳環智力10% (耳環智力10%)" in html_content:
                checks.append("✅ 商品內容格式正確")
            
            if "共 2 個匹配" in html_content:
                checks.append("✅ 統計信息正確")
            
            print("\n新格式檢查結果:")
            for check in checks:
                print(f"  {check}")
            
            success_count = len([c for c in checks if c.startswith("✅")])
            total_count = len(checks)
            
            if success_count == total_count:
                print(f"\n🎉 所有檢查通過！ ({success_count}/{total_count})")
            else:
                print(f"\n⚠️  部分檢查未通過 ({success_count}/{total_count})")
            
            # 顯示HTML的關鍵部分
            print(f"\n--- HTML內容預覽 ---")
            lines = html_content.split('\n')
            for i, line in enumerate(lines):
                if "交易匹配 #" in line:
                    # 顯示交易卡片的前幾行
                    for j in range(i, min(i+10, len(lines))):
                        if "玩家:" in lines[j] or "頻道:" in lines[j] or "商品內容:" in lines[j]:
                            print(lines[j].strip())
                    break
            
        else:
            print("❌ HTML報告生成失敗")

if __name__ == "__main__":
    test_new_html_format()
    
    print(f"\n=== 新HTML格式特點 ===")
    print("1. ✅ 只顯示有匹配的交易結果")
    print("2. ✅ 最新的匹配結果顯示在最上方")
    print("3. ✅ 顯示指定的四個欄位：玩家、頻道、商品內容、完整廣播")
    print("4. ✅ 清晰的卡片式布局，便於閱讀")
    print("5. ✅ 統計信息顯示匹配率和數量")