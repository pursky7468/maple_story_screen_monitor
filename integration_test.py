import os
import time
import json
from datetime import datetime
from screen_monitor import ScreenMonitor
from roi_selector import ROISelector
from gemini_analyzer import GeminiAnalyzer
from config import *

class IntegrationTester:
    def __init__(self):
        self.test_folder = None
        self.roi_coordinates = None
        
    def setup_test_environment(self, test_runs):
        """設置測試環境"""
        # 創建測試資料夾，使用時間命名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.test_folder = f"integration_test_{timestamp}"
        
        if not os.path.exists(self.test_folder):
            os.makedirs(self.test_folder)
            
        print(f"測試資料夾已創建: {self.test_folder}")
        
        # 創建測試摘要檔案
        summary_file = os.path.join(self.test_folder, "test_summary.json")
        test_info = {
            "test_start_time": timestamp,
            "total_runs": test_runs,
            "roi_coordinates": None,
            "selling_items": SELLING_ITEMS,
            "results": []
        }
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(test_info, f, ensure_ascii=False, indent=2)
            
        return summary_file
    
    def get_roi_selection(self):
        """獲取ROI選擇"""
        print("\n請選擇測試用的ROI區域...")
        print("即將顯示全螢幕截圖，請用滑鼠拖拉選擇監控區域")
        input("按Enter開始選擇ROI...")
        
        selector = ROISelector()
        roi_coordinates = selector.select_roi()
        
        if roi_coordinates is None:
            print("未選擇ROI區域，測試結束")
            return None
            
        print(f"已選擇ROI: {roi_coordinates}")
        self.roi_coordinates = roi_coordinates
        return roi_coordinates
    
    def run_single_test(self, test_id, monitor):
        """執行單次測試"""
        print(f"\n--- 執行測試 {test_id} ---")
        
        # 使用統一的時間戳記
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # 包含毫秒
        
        # 截取ROI圖像
        roi_image = monitor.capture_roi()
        if roi_image is None:
            print(f"測試 {test_id}: 截圖失敗")
            return None
            
        # 保存截圖
        screenshot_path = os.path.join(self.test_folder, f"test_{test_id:03d}_{timestamp}_screenshot.png")
        roi_image.save(screenshot_path)
        
        # 進行分析
        analysis_start_time = datetime.now()
        result, analysis_result = monitor.analyze_with_strategy(roi_image)
        analysis_end_time = datetime.now()
        
        # 檢查是否是API配額錯誤
        if analysis_result == "ERROR" or "429" in str(analysis_result) or "quota" in str(analysis_result).lower():
            if "429" in str(analysis_result) or "quota" in str(analysis_result).lower():
                print(f"⚠️  測試 {test_id}: API配額已用盡")
                return {
                    "test_id": test_id,
                    "timestamp": timestamp,
                    "screenshot_path": screenshot_path,
                    "error": "API配額已用盡",
                    "error_type": "API_QUOTA_EXCEEDED",
                    "analysis_duration_ms": (analysis_end_time - analysis_start_time).total_seconds() * 1000,
                    "success": False
                }
            else:
                print(f"❌ 測試 {test_id}: LLM分析失敗")
                return {
                    "test_id": test_id,
                    "timestamp": timestamp,
                    "screenshot_path": screenshot_path,
                    "error": "LLM分析失敗",
                    "error_type": "API_ERROR",
                    "analysis_duration_ms": (analysis_end_time - analysis_start_time).total_seconds() * 1000,
                    "success": False
                }
        
        # 保存分析結果
        analysis_path = os.path.join(self.test_folder, f"test_{test_id:03d}_{timestamp}_analysis.json")
        
        try:
            # 嘗試解析JSON並格式化保存 (僅適用於Gemini)
            if hasattr(analyzer, 'extract_json_from_response'):
                json_content = analyzer.extract_json_from_response(analysis_result)
                parsed_result = json.loads(json_content)
            else:
                # OCR分析器直接返回結構化結果
                parsed_result = result.to_dict()
            
            # 添加測試元數據
            test_result = {
                "test_id": test_id,
                "timestamp": timestamp,
                "screenshot_path": screenshot_path,
                "analysis_start_time": analysis_start_time.isoformat(),
                "analysis_end_time": analysis_end_time.isoformat(),
                "analysis_duration_ms": (analysis_end_time - analysis_start_time).total_seconds() * 1000,
                "raw_response": analysis_result,
                "parsed_result": parsed_result
            }
            
            with open(analysis_path, 'w', encoding='utf-8') as f:
                json.dump(test_result, f, ensure_ascii=False, indent=2)
                
        except json.JSONDecodeError as e:
            # 詳細的JSON解析錯誤分析
            if hasattr(analyzer, 'extract_json_from_response'):
                extracted_json = analyzer.extract_json_from_response(analysis_result)
            else:
                extracted_json = str(analysis_result)
            
            error_analysis = {
                "error_type": "JSON解析錯誤",
                "error_message": str(e),
                "error_line": getattr(e, 'lineno', None),
                "error_column": getattr(e, 'colno', None),
                "error_position": getattr(e, 'pos', None),
                "raw_response_length": len(analysis_result),
                "extracted_json_length": len(extracted_json),
                "has_json_markers": "```json" in analysis_result,
                "has_closing_markers": "```" in analysis_result and analysis_result.count("```") >= 2,
                "starts_with_brace": extracted_json.strip().startswith('{'),
                "ends_with_brace": extracted_json.strip().endswith('}'),
                "brace_balance": extracted_json.count('{') - extracted_json.count('}'),
                "quote_balance": extracted_json.count('"') % 2 == 0,
                "common_issues": []
            }
            
            # 檢查常見問題
            if not extracted_json.strip():
                error_analysis["common_issues"].append("提取的JSON內容為空")
            if "```json" in analysis_result and not extracted_json.strip().startswith('{'):
                error_analysis["common_issues"].append("找到json標記但內容不是JSON格式")
            if extracted_json.count('{') != extracted_json.count('}'):
                error_analysis["common_issues"].append(f"大括號不平衡: {{ {extracted_json.count('{')} 個, }} {extracted_json.count('}')} 個")
            if extracted_json.count('"') % 2 != 0:
                error_analysis["common_issues"].append("引號不平衡")
            if '\\n' in extracted_json and not extracted_json.replace('\\n', '\n').strip():
                error_analysis["common_issues"].append("可能包含換行符問題")
                
            test_result = {
                "test_id": test_id,
                "timestamp": timestamp,
                "screenshot_path": screenshot_path,
                "analysis_start_time": analysis_start_time.isoformat(),
                "analysis_end_time": analysis_end_time.isoformat(),
                "analysis_duration_ms": (analysis_end_time - analysis_start_time).total_seconds() * 1000,
                "raw_response": analysis_result,
                "extracted_json": extracted_json,
                "error_analysis": error_analysis,
                "parsed_result": None
            }
            
            # 保存詳細錯誤報告
            with open(analysis_path.replace('.json', '_error.json'), 'w', encoding='utf-8') as f:
                json.dump(test_result, f, ensure_ascii=False, indent=2)
                
            # 也保存純文字版本方便查看
            with open(analysis_path.replace('.json', '_debug.txt'), 'w', encoding='utf-8') as f:
                f.write(f"=== 測試 {test_id} JSON解析錯誤詳細報告 ===\n\n")
                f.write(f"時間戳: {timestamp}\n")
                f.write(f"錯誤類型: {error_analysis['error_type']}\n")
                f.write(f"錯誤訊息: {error_analysis['error_message']}\n")
                if error_analysis['error_line']:
                    f.write(f"錯誤行號: {error_analysis['error_line']}\n")
                if error_analysis['error_column']:
                    f.write(f"錯誤列號: {error_analysis['error_column']}\n")
                f.write(f"\n=== 內容分析 ===\n")
                f.write(f"原始回應長度: {error_analysis['raw_response_length']} 字符\n")
                f.write(f"提取JSON長度: {error_analysis['extracted_json_length']} 字符\n")
                f.write(f"包含```json標記: {error_analysis['has_json_markers']}\n")
                f.write(f"包含結束標記: {error_analysis['has_closing_markers']}\n")
                f.write(f"以{{開始: {error_analysis['starts_with_brace']}\n")
                f.write(f"以}}結束: {error_analysis['ends_with_brace']}\n")
                f.write(f"大括號平衡: {error_analysis['brace_balance']} (0為平衡)\n")
                f.write(f"引號平衡: {error_analysis['quote_balance']}\n")
                
                if error_analysis['common_issues']:
                    f.write(f"\n=== 發現的問題 ===\n")
                    for issue in error_analysis['common_issues']:
                        f.write(f"- {issue}\n")
                
                f.write(f"\n=== 原始回應 ===\n")
                f.write(analysis_result)
                f.write(f"\n\n=== 提取的JSON ===\n")
                f.write(extracted_json)
                
                # 如果JSON很短，嘗試逐字符分析
                if len(extracted_json.strip()) < 500:
                    f.write(f"\n\n=== 字符分析 ===\n")
                    for i, char in enumerate(extracted_json):
                        f.write(f"{i:3d}: '{char}' (ASCII: {ord(char)})\n")
        
        # 進行匹配檢查（不觸發提示窗）
        is_match = result.is_match
        match_details = monitor.format_match_info(result)
        
        print(f"測試 {test_id} 完成:")
        print(f"  截圖: {screenshot_path}")
        print(f"  分析: {analysis_path}")
        print(f"  匹配: {'是' if is_match else '否'}")
        if is_match:
            print(f"  詳情: {match_details[:100]}...")
            
        return {
            "test_id": test_id,
            "timestamp": timestamp,
            "screenshot_path": screenshot_path,
            "analysis_path": analysis_path,
            "is_match": is_match,
            "analysis_duration_ms": (analysis_end_time - analysis_start_time).total_seconds() * 1000,
            "success": True
        }
    
    def run_integration_test(self, test_runs):
        """執行整合測試"""
        print(f"\n開始整合測試 - 總共 {test_runs} 次")
        
        # 設置測試環境
        summary_file = self.setup_test_environment(test_runs)
        
        # 獲取ROI選擇
        roi_coordinates = self.get_roi_selection()
        if roi_coordinates is None:
            return
        
        # 創建監控器（關閉提示窗功能）
        analyzer = GeminiAnalyzer(GEMINI_API_KEY, SELLING_ITEMS)
        monitor = ScreenMonitor(roi_coordinates, analyzer, save_screenshots=False, show_alerts=False)
        
        # 更新測試摘要中的ROI資訊
        with open(summary_file, 'r', encoding='utf-8') as f:
            summary = json.load(f)
        summary["roi_coordinates"] = roi_coordinates
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        # 執行測試循環
        results = []
        match_count = 0
        quota_exceeded_count = 0
        
        for i in range(1, test_runs + 1):
            try:
                result = self.run_single_test(i, monitor)
                if result:
                    results.append(result)
                    
                    # 檢查匹配結果
                    if result.get("success", False) and result.get("is_match", False):
                        match_count += 1
                    
                    # 檢查配額錯誤
                    if result.get("error_type") == "API_QUOTA_EXCEEDED":
                        quota_exceeded_count += 1
                        
                        # 如果連續3次配額錯誤，詢問是否繼續
                        if quota_exceeded_count >= 3:
                            print(f"\n⚠️  連續遇到API配額錯誤")
                            print("建議：")
                            print("1. 等待24小時配額重置")
                            print("2. 升級到付費計畫")
                            print("3. 使用不同的API Key")
                            
                            choice = input("是否繼續測試？(y/n): ").lower().strip()
                            if choice not in ['y', 'yes', '是']:
                                print(f"測試在第 {i} 次後停止（配額限制）")
                                break
                            else:
                                quota_exceeded_count = 0  # 重置計數器
                    else:
                        quota_exceeded_count = 0  # 重置配額錯誤計數器
                
                # 每10次測試顯示進度
                if i % 10 == 0:
                    print(f"\n進度: {i}/{test_runs} ({i/test_runs*100:.1f}%)")
                    print(f"成功測試: {len([r for r in results if r.get('success', False)])}")
                    print(f"目前匹配: {match_count}")
                
                # 測試間隔（避免API限制）
                if i < test_runs:
                    time.sleep(SCAN_INTERVAL)
                    
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
        
        # 分析測試結果
        completed_tests = [r for r in results if r.get("success", False)]
        failed_tests = [r for r in results if not r.get("success", False)]
        
        # 統計錯誤類型
        error_stats = {}
        for result in failed_tests:
            error_type = result.get("error", "未知錯誤")
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
            "error_breakdown": error_stats
        }
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        # 顯示詳細測試結果
        stats = summary["statistics"]
        print(f"\n{'='*60}")
        print("整合測試完成！")
        print(f"{'='*60}")
        print(f"測試資料夾: {self.test_folder}")
        print(f"執行結果: {len(results)}/{test_runs} 次測試")
        print(f"成功率: {stats['success_rate']}")
        print(f"失敗次數: {stats['total_failed']}")
        print(f"匹配次數: {stats['total_matches']}")
        print(f"匹配率: {stats['match_rate']}")
        print(f"平均分析時間: {stats['average_analysis_time_ms']} 毫秒")
        print(f"分析時間範圍: {stats['min_analysis_time_ms']}-{stats['max_analysis_time_ms']} 毫秒")
        
        if stats['error_breakdown']:
            print(f"\n錯誤統計:")
            for error_type, count in stats['error_breakdown'].items():
                print(f"  - {error_type}: {count} 次")
        
        print(f"\n檔案說明:")
        print(f"  - test_summary.json: 完整測試摘要")
        print(f"  - *_screenshot.png: 測試截圖")
        print(f"  - *_analysis.json: 成功解析的結果")
        print(f"  - *_error.json: JSON解析錯誤的詳細分析")
        print(f"  - *_debug.txt: 人類可讀的錯誤分析報告")
        print(f"{'='*60}")

def main():
    """主程式"""
    if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        print("請先在 config.py 中設置您的 Gemini API Key")
        return
        
    print("螢幕監控整合測試程式")
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
    
    # 執行整合測試
    tester = IntegrationTester()
    tester.run_integration_test(test_runs)

if __name__ == "__main__":
    main()