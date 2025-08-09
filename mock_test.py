import os
import time
import json
import random
from datetime import datetime
from integration_test import IntegrationTester
from screen_monitor import ScreenMonitor, convert_to_json_serializable
from roi_selector import ROISelector
from config import *

class MockScreenMonitor(ScreenMonitor):
    """模擬版本的ScreenMonitor，用於測試JSON解析邏輯"""
    
    def __init__(self, roi_coordinates, analyzer=None, save_screenshots=False, show_alerts=False):
        # 不調用父類的__init__以避免API初始化
        self.roi_coordinates = roi_coordinates
        self.analyzer = analyzer  # Mock模式下可以為None
        self.save_screenshots = save_screenshots
        self.show_alerts = show_alerts
        self.running = False
        
        # 模擬的回應模板
        self.mock_responses = [
            # 正確的JSON回應
            '''```json
{
    "full_text": "CHO392: 收購披風幸運60%卷軸，價格好議價",
    "is_match": true,
    "player_name": "TestPlayer1",
    "channel_number": "CHO392",
    "matched_items": [
        {
            "item_name": "披風幸運60%",
            "keywords_found": ["披風幸運60%", "披風幸運60%卷軸"]
        }
    ],
    "matched_keywords": ["收購", "披風幸運60%", "披風幸運60%卷軸"]
}
```''',
            
            # 沒有匹配的JSON回應
            '''```json
{
    "full_text": "CHO123: 賣武器攻擊力30%卷軸，便宜出售",
    "is_match": false,
    "player_name": "TestPlayer2", 
    "channel_number": "CHO123",
    "matched_items": [],
    "matched_keywords": []
}
```''',
            
            # 有語法錯誤的JSON（缺少引號）
            '''```json
{
    "full_text": CHO456: 收購母礦，大量收購,
    "is_match": true,
    "player_name": "TestPlayer3",
    "channel_number": "CHO456",
    "matched_items": [
        {
            "item_name": "母礦",
            "keywords_found": ["母礦"]
        }
    ],
    "matched_keywords": ["收購", "母礦"]
}
```''',
            
            # 括號不平衡的JSON
            '''```json
{
    "full_text": "CHO789: 收購耳環智力10%",
    "is_match": true,
    "player_name": "TestPlayer4",
    "channel_number": "CHO789",
    "matched_items": [
        {
            "item_name": "耳環智力10%",
            "keywords_found": ["耳環智力10%"]
        }
    ],
    "matched_keywords": ["收購", "耳環智力10%"]

```''',
            
            # 沒有JSON標記的回應
            '''{
    "full_text": "普通聊天內容，沒有交易相關",
    "is_match": false,
    "player_name": "ChatPlayer",
    "channel_number": "CHO001",
    "matched_items": [],
    "matched_keywords": []
}''',
            
            # 完全不是JSON的回應
            '''這不是JSON格式的回應，只是普通的文字內容。
玩家在說一些日常對話。
沒有任何結構化的數據。''',
            
            # 空回應
            '',
            
            # 只有JSON標記沒有內容
            '''```json
```''',
        ]
    
    def analyze_with_strategy(self, image):
        """模擬分析功能（兼容新的策略模式）"""
        from text_analyzer import AnalysisResult
        
        # 隨機選擇一個回應
        raw_response = random.choice(self.mock_responses)
        
        # 模擬API延遲
        time.sleep(random.uniform(0.5, 2.0))
        
        # 創建模擬的分析結果
        result = AnalysisResult(
            full_text=f"模擬分析結果 - {datetime.now().strftime('%H:%M:%S')}",
            is_match=random.choice([True, False]),
            analysis_method="MockAnalyzer",
            confidence=random.uniform(0.6, 0.95)
        )
        
        return result, raw_response
    
    def capture_roi(self):
        """模擬截圖功能"""
        # 創建一個簡單的測試圖片
        from PIL import Image
        
        # 創建一個隨機顏色的測試圖片
        width = self.roi_coordinates["width"]
        height = self.roi_coordinates["height"]
        
        # 隨機RGB顏色
        color = (
            random.randint(100, 255),
            random.randint(100, 255), 
            random.randint(100, 255)
        )
        
        image = Image.new('RGB', (width, height), color)
        return image

class MockIntegrationTester(IntegrationTester):
    """模擬版本的整合測試器"""
    
    def run_integration_test(self, test_runs):
        """執行模擬整合測試"""
        print(f"\n開始模擬整合測試 - 總共 {test_runs} 次")
        print("⚠️  使用模擬模式（不會調用真實API）")
        
        # 設置測試環境
        summary_file = self.setup_test_environment(test_runs)
        
        # 獲取ROI選擇
        roi_coordinates = self.get_roi_selection()
        if roi_coordinates is None:
            return
        
        # 創建模擬監控器
        monitor = MockScreenMonitor(roi_coordinates, analyzer=None, save_screenshots=False, show_alerts=False)
        
        # 更新測試摘要中的ROI資訊
        with open(summary_file, 'r', encoding='utf-8') as f:
            summary = json.load(f)
        summary["roi_coordinates"] = roi_coordinates
        summary["test_mode"] = "MOCK_MODE"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(convert_to_json_serializable(summary), f, ensure_ascii=False, indent=2)
        
        # 執行測試循環（複用父類的邏輯）
        results = []
        match_count = 0
        
        for i in range(1, test_runs + 1):
            try:
                result = self.run_single_test(i, monitor)
                if result:
                    results.append(result)
                    if result.get("success", False) and result.get("is_match", False):
                        match_count += 1
                
                # 每10次測試顯示進度
                if i % 10 == 0:
                    print(f"\n進度: {i}/{test_runs} ({i/test_runs*100:.1f}%)")
                    print(f"成功測試: {len([r for r in results if r.get('success', False)])}")
                    print(f"目前匹配: {match_count}")
                    json_errors = len([r for r in results if not r.get('success', False) and 'JSON' in str(r.get('error', ''))])
                    print(f"JSON解析錯誤: {json_errors}")
                
                # 短暫間隔
                time.sleep(0.1)
                    
            except KeyboardInterrupt:
                print(f"\n測試被中斷在第 {i} 次")
                break
            except Exception as e:
                print(f"測試 {i} 發生錯誤: {e}")
                results.append({
                    "test_id": i,
                    "error": str(e),
                    "error_type": "UNKNOWN_ERROR",
                    "success": False
                })
        
        # 分析測試結果（複用父類邏輯）
        completed_tests = [r for r in results if r.get("success", False)]
        failed_tests = [r for r in results if not r.get("success", False)]
        
        # 統計錯誤類型
        error_stats = {}
        for result in failed_tests:
            error_type = result.get("error", "未知錯誤")
            if "JSON" in error_type:
                error_type = "JSON解析錯誤"
            error_stats[error_type] = error_stats.get(error_type, 0) + 1
        
        # 統計分析時間
        analysis_times = [r.get("analysis_duration_ms", 0) for r in completed_tests]
        avg_analysis_time = sum(analysis_times) / len(analysis_times) if analysis_times else 0
        
        # 更新最終測試摘要
        summary["results"] = results
        summary["test_end_time"] = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary["statistics"] = {
            "total_completed": len(completed_tests),
            "total_failed": len(failed_tests),
            "success_rate": f"{len(completed_tests)/len(results)*100:.1f}%" if results else "0%",
            "total_matches": match_count,
            "match_rate": f"{match_count/len(completed_tests)*100:.1f}%" if completed_tests else "0%",
            "average_analysis_time_ms": round(avg_analysis_time, 2),
            "min_analysis_time_ms": min(analysis_times) if analysis_times else 0,
            "max_analysis_time_ms": max(analysis_times) if analysis_times else 0,
            "error_breakdown": error_stats,
            "json_parsing_success_rate": f"{len(completed_tests)/len(results)*100:.1f}%" if results else "0%"
        }
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(convert_to_json_serializable(summary), f, ensure_ascii=False, indent=2)
        
        # 顯示詳細測試結果
        stats = summary["statistics"]
        print(f"\n{'='*60}")
        print("模擬整合測試完成！")
        print(f"{'='*60}")
        print(f"測試資料夾: {self.test_folder}")
        print(f"執行結果: {len(results)}/{test_runs} 次測試")
        print(f"JSON解析成功率: {stats['json_parsing_success_rate']}")
        print(f"失敗次數: {stats['total_failed']}")
        print(f"匹配次數: {stats['total_matches']}")
        print(f"匹配率: {stats['match_rate']}")
        print(f"平均分析時間: {stats['average_analysis_time_ms']} 毫秒")
        
        if stats['error_breakdown']:
            print(f"\n錯誤統計:")
            for error_type, count in stats['error_breakdown'].items():
                print(f"  - {error_type}: {count} 次")
        
        print(f"\n📁 檔案說明:")
        print(f"  - *_error.json: JSON解析錯誤的詳細分析")
        print(f"  - *_debug.txt: 人類可讀的錯誤分析報告")
        print(f"  - test_summary.json: 完整測試摘要")
        print(f"{'='*60}")
        print(f"💡 提示：使用 'python analyze_errors.py' 分析錯誤詳情")

def main():
    """主程式"""
    print("模擬螢幕監控整合測試程式")
    print("=" * 40)
    print("⚠️  這是模擬測試模式，不會調用真實的Gemini API")
    print("💡 用於測試JSON解析邏輯和錯誤處理機制")
    print("=" * 40)
    
    # 獲取測試次數
    while True:
        try:
            test_runs = int(input("請輸入測試次數 (1-1000): "))
            if 1 <= test_runs <= 1000:
                break
            else:
                print("請輸入1到1000之間的數字")
        except ValueError:
            print("請輸入有效的數字")
    
    # 執行模擬整合測試
    tester = MockIntegrationTester()
    tester.run_integration_test(test_runs)

if __name__ == "__main__":
    main()