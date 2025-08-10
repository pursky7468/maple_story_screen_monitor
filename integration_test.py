import os
import time
import json
import numpy as np
from datetime import datetime
from screen_monitor import ScreenMonitor, convert_to_json_serializable
from roi_selector import ROISelector
from gemini_analyzer import GeminiAnalyzer
from real_time_merger import setup_real_time_merger, log_test_result
from config import *

class IntegrationTester:
    def __init__(self):
        self.test_folder = None
        self.roi_coordinates = None
        self.real_time_merger = None
        
    def setup_test_environment(self, test_runs):
        """設置測試環境"""
        # 創建測試資料夾，使用時間命名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.test_folder = f"integration_test_{timestamp}"
        
        if not os.path.exists(self.test_folder):
            os.makedirs(self.test_folder)
            
        print(f"測試資料夾已創建: {self.test_folder}")
        
        # 設置實時合併器
        self.real_time_merger = setup_real_time_merger(self.test_folder)
        print("實時結果合併器已啟用")
        
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
            json.dump(convert_to_json_serializable(test_info), f, ensure_ascii=False, indent=2)
            
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
    
    def get_analyzer_choice(self):
        """獲取分析器選擇"""
        print("\n請選擇要測試的分析方法：")
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
    
    def create_analyzer(self, analyzer_type: str):
        """創建分析器實例"""
        if analyzer_type == "gemini":
            if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
                print("錯誤：請先在 config.py 中設置您的 Gemini API Key")
                return None
            try:
                from gemini_analyzer import GeminiAnalyzer
                return GeminiAnalyzer(GEMINI_API_KEY, SELLING_ITEMS)
            except Exception as e:
                print(f"Gemini分析器初始化失敗: {e}")
                return None
        
        elif analyzer_type == "ocr":
            try:
                from ocr_analyzer import OCRAnalyzer
                return OCRAnalyzer(SELLING_ITEMS)
            except ImportError as e:
                print(f"❌ OCR依賴缺失: {e}")
                print("\n安裝OCR依賴：")
                print("方法1 (推薦)：python install_ocr.py")
                print("方法2 (手動)：pip install easyocr")
                print("\n注意：首次使用OCR會自動下載語言模型，需要網路連線")
                return None
            except Exception as e:
                print(f"❌ OCR初始化失敗: {e}")
                return None
        
        
        return None
    
    def run_single_test(self, test_id, monitor, fallback_analyzer=None):
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
        
        # 使用策略模式處理錯誤（完全隔離的錯誤判斷）
        if analysis_result == "ERROR" or str(analysis_result).startswith("ERROR"):
            # 讓分析器自己決定錯誤類型
            error_type = monitor.analyzer.get_error_type(str(analysis_result))
            
            # 如果是API配額錯誤且有備用分析器，自動切換
            if error_type == "API_QUOTA_EXCEEDED" and fallback_analyzer:
                print(f"⚠️  測試 {test_id}: API配額已用盡，切換到OCR分析")
                
                # 使用備用分析器重新分析
                fallback_start_time = datetime.now()
                fallback_result, fallback_analysis_result = fallback_analyzer.analyze_image(roi_image), None
                
                # OCR分析器直接返回結構化結果
                if not (isinstance(fallback_result, str) and fallback_result.startswith("ERROR")):
                    parsed_fallback = fallback_analyzer.parse_result(fallback_result)
                    fallback_end_time = datetime.now()
                    
                    print(f"✅ 測試 {test_id}: 已切換到OCR完成分析")
                    
                    # 保存分析結果（標記為使用備用分析器）
                    analysis_path = os.path.join(self.test_folder, f"test_{test_id:03d}_{timestamp}_analysis.json")
                    fallback_test_result = {
                        "test_id": test_id,
                        "timestamp": timestamp,
                        "screenshot_path": screenshot_path,
                        "analysis_start_time": analysis_start_time.isoformat(),
                        "analysis_end_time": fallback_end_time.isoformat(),
                        "analysis_duration_ms": (fallback_end_time - fallback_start_time).total_seconds() * 1000,
                        "primary_analyzer": monitor.analyzer.strategy_type,
                        "fallback_analyzer": fallback_analyzer.strategy_type,
                        "fallback_used": True,
                        "primary_error": str(analysis_result),
                        "parsed_result": parsed_fallback.to_dict()
                    }
                    
                    with open(analysis_path, 'w', encoding='utf-8') as f:
                        json.dump(convert_to_json_serializable(fallback_test_result), f, ensure_ascii=False, indent=2)
                    
                    # 進行匹配檢查
                    is_match = parsed_fallback.is_match
                    match_details = fallback_analyzer.format_match_info(parsed_fallback) if hasattr(fallback_analyzer, 'format_match_info') else ""
                    
                    print(f"測試 {test_id} 完成 (使用OCR備用):")
                    print(f"  截圖: {screenshot_path}")
                    print(f"  分析: {analysis_path}")
                    print(f"  匹配: {'是' if is_match else '否'}")
                    if is_match and match_details:
                        print(f"  詳情: {match_details[:100]}...")
                    
                    # 記錄到實時合併器
                    if self.real_time_merger:
                        log_test_result(self.real_time_merger, test_id, screenshot_path, parsed_fallback.to_dict(), None)
                        
                    return {
                        "test_id": test_id,
                        "timestamp": timestamp,
                        "screenshot_path": screenshot_path,
                        "analysis_path": analysis_path,
                        "is_match": is_match,
                        "analysis_duration_ms": (fallback_end_time - fallback_start_time).total_seconds() * 1000,
                        "fallback_used": True,
                        "primary_analyzer": monitor.analyzer.strategy_type,
                        "fallback_analyzer": fallback_analyzer.strategy_type,
                        "success": True
                    }
            
            # 根據錯誤類型生成適當的錯誤信息
            if error_type == "API_QUOTA_EXCEEDED":
                error_message = "API配額已用盡"
                print(f"⚠️  測試 {test_id}: {error_message}")
            else:
                error_message = f"{monitor.analyzer.strategy_type}分析失敗"
                print(f"❌ 測試 {test_id}: {error_message}")
            
            error_info = {
                "error": error_message,
                "error_type": error_type,
                "strategy_type": monitor.analyzer.strategy_type,
                "raw_response": str(analysis_result),
                "fallback_available": fallback_analyzer is not None,
                "fallback_attempted": error_type == "API_QUOTA_EXCEEDED" and fallback_analyzer is not None
            }
            
            # 記錄到實時合併器
            if self.real_time_merger:
                log_test_result(self.real_time_merger, test_id, screenshot_path, None, error_info)
            
            return {
                "test_id": test_id,
                "timestamp": timestamp,
                "screenshot_path": screenshot_path,
                "error": error_message,
                "error_type": error_type,
                "strategy_type": monitor.analyzer.strategy_type,
                "analysis_duration_ms": (analysis_end_time - analysis_start_time).total_seconds() * 1000,
                "fallback_available": fallback_analyzer is not None,
                "success": False
            }
        
        # 保存分析結果
        analysis_path = os.path.join(self.test_folder, f"test_{test_id:03d}_{timestamp}_analysis.json")
        
        try:
            # 使用策略模式處理結果解析（避免硬編碼判斷）
            if monitor.analyzer.strategy_type == "GEMINI":
                json_content = monitor.analyzer.extract_json_from_response(analysis_result)
                parsed_result = json.loads(json_content)
            else:
                # 其他分析器直接返回結構化結果
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
                json.dump(convert_to_json_serializable(test_result), f, ensure_ascii=False, indent=2)
                
        except json.JSONDecodeError as e:
            # 使用策略模式處理JSON解析錯誤
            if monitor.analyzer.strategy_type == "GEMINI":
                extracted_json = monitor.analyzer.extract_json_from_response(analysis_result)
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
                json.dump(convert_to_json_serializable(test_result), f, ensure_ascii=False, indent=2)
                
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
        
        # 記錄到實時合併器
        if self.real_time_merger:
            log_test_result(self.real_time_merger, test_id, screenshot_path, result.to_dict() if hasattr(result, 'to_dict') else result, None)
            
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
        
        # 讓使用者選擇分析策略
        analyzer_type = self.get_analyzer_choice()
        analyzer = self.create_analyzer(analyzer_type)
        if analyzer is None:
            print("分析器創建失敗，測試結束")
            return
        
        # 創建備用分析器（當主分析器是Gemini時，使用OCR作為備用）
        fallback_analyzer = None
        if analyzer_type == "gemini":
            try:
                from ocr_analyzer import OCRAnalyzer
                from config import SELLING_ITEMS
                fallback_analyzer = OCRAnalyzer(SELLING_ITEMS)
                print("✅ OCR備用分析器已創建，將在API配額用盡時自動切換")
            except Exception as e:
                print(f"⚠️  無法創建OCR備用分析器: {e}")
                print("將繼續使用單一分析器模式")
        
        # 創建監控器（關閉提示窗功能）
        monitor = ScreenMonitor(roi_coordinates, analyzer, save_screenshots=False, show_alerts=False)
        
        # 更新測試摘要中的ROI資訊和分析方法
        with open(summary_file, 'r', encoding='utf-8') as f:
            summary = json.load(f)
        summary["roi_coordinates"] = roi_coordinates
        summary["analyzer_type"] = analyzer_type
        summary["analyzer_class"] = analyzer.__class__.__name__
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(convert_to_json_serializable(summary), f, ensure_ascii=False, indent=2)
        
        # 執行測試循環
        results = []
        match_count = 0
        quota_exceeded_count = 0
        
        for i in range(1, test_runs + 1):
            try:
                result = self.run_single_test(i, monitor, fallback_analyzer)
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
        fallback_used_tests = [r for r in completed_tests if r.get("fallback_used", False)]
        
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
            "fallback_used_count": len(fallback_used_tests),
            "fallback_usage_rate": f"{len(fallback_used_tests)/len(results)*100:.1f}%" if results else "0%",
            "average_analysis_time_ms": round(avg_analysis_time, 2),
            "min_analysis_time_ms": min(analysis_times) if analysis_times else 0,
            "max_analysis_time_ms": max(analysis_times) if analysis_times else 0,
            "error_breakdown": error_stats,
            "has_fallback_analyzer": fallback_analyzer is not None
        }
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(convert_to_json_serializable(summary), f, ensure_ascii=False, indent=2)
        
        # 顯示詳細測試結果
        stats = summary["statistics"]
        print(f"\n{'='*60}")
        print("整合測試完成！")
        print(f"{'='*60}")
        print(f"測試資料夾: {self.test_folder}")
        print(f"分析方法: {summary.get('analyzer_class', '未知')} ({summary.get('analyzer_type', '未知')})")
        print(f"執行結果: {len(results)}/{test_runs} 次測試")
        print(f"成功率: {stats['success_rate']}")
        print(f"失敗次數: {stats['total_failed']}")
        print(f"匹配次數: {stats['total_matches']}")
        print(f"匹配率: {stats['match_rate']}")
        if stats.get('has_fallback_analyzer', False):
            print(f"OCR備用使用: {stats['fallback_used_count']} 次 ({stats['fallback_usage_rate']})")
        print(f"平均分析時間: {stats['average_analysis_time_ms']} 毫秒")
        print(f"分析時間範圍: {stats['min_analysis_time_ms']}-{stats['max_analysis_time_ms']} 毫秒")
        
        if stats['error_breakdown']:
            print(f"\n錯誤統計:")
            for error_type, count in stats['error_breakdown'].items():
                print(f"  - {error_type}: {count} 次")
        
        # 生成最終的合併報告
        if self.real_time_merger:
            self.real_time_merger.generate_quick_html()
            print(f"\n🎯 合併報告已生成:")
            print(f"  - quick_view.html: 快速查看器（推薦）")
            print(f"  - combined_results.json: 合併的JSON數據")
        
        print(f"\n📁 檔案說明:")
        print(f"  - test_summary.json: 完整測試摘要")
        print(f"  - quick_view.html: 圖片+結果合併查看器 🌟")
        print(f"  - combined_results.json: 合併的測試數據")
        print(f"  - *_screenshot.png: 測試截圖")
        print(f"  - *_analysis.json: 成功解析的結果")
        print(f"  - *_error.json: JSON解析錯誤的詳細分析")
        print(f"  - *_debug.txt: 人類可讀的錯誤分析報告")
        print(f"{'='*60}")
        
        if self.real_time_merger and len(self.real_time_merger.merged_results) > 0:
            print(f"💡 調試建議：")
            print(f"   1. 打開 {self.test_folder}/quick_view.html 查看測試結果")
            print(f"   2. 點擊圖片可以放大查看")
            print(f"   3. 合併報告包含了截圖和分析結果，便於調試")
            print(f"{'='*60}")

def main():
    """主程式"""
    print("螢幕監控整合測試程式")
    print("=" * 40)
    print("支援的分析方法：")
    print("- Gemini AI (需要設置API Key)")
    print("- OCR 本地識別 (需要安裝easyocr)")
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