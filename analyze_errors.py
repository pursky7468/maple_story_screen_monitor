import os
import json
import glob
from collections import Counter

def analyze_test_errors(test_folder):
    """分析測試資料夾中的錯誤"""
    print(f"分析測試資料夾: {test_folder}")
    
    # 尋找所有錯誤檔案
    error_files = glob.glob(os.path.join(test_folder, "*_error.json"))
    debug_files = glob.glob(os.path.join(test_folder, "*_debug.txt"))
    
    print(f"找到 {len(error_files)} 個錯誤檔案")
    
    if not error_files:
        print("沒有發現JSON解析錯誤")
        return
    
    # 分析錯誤類型
    error_types = []
    error_messages = []
    common_issues = []
    
    for error_file in error_files:
        try:
            with open(error_file, 'r', encoding='utf-8') as f:
                error_data = json.load(f)
                
            error_analysis = error_data.get('error_analysis', {})
            error_types.append(error_analysis.get('error_type', '未知'))
            error_messages.append(error_analysis.get('error_message', ''))
            common_issues.extend(error_analysis.get('common_issues', []))
            
        except Exception as e:
            print(f"無法讀取錯誤檔案 {error_file}: {e}")
    
    # 統計結果
    print(f"\n{'='*50}")
    print("錯誤分析報告")
    print(f"{'='*50}")
    
    print(f"錯誤類型統計:")
    type_counts = Counter(error_types)
    for error_type, count in type_counts.most_common():
        print(f"  - {error_type}: {count} 次")
    
    print(f"\n常見問題統計:")
    issue_counts = Counter(common_issues)
    for issue, count in issue_counts.most_common():
        print(f"  - {issue}: {count} 次")
    
    print(f"\n錯誤訊息統計:")
    message_counts = Counter(error_messages)
    for message, count in message_counts.most_common(10):  # 只顯示前10個
        print(f"  - {message}: {count} 次")
    
    # 分析第一個錯誤的詳細資訊
    if error_files:
        first_error = error_files[0]
        print(f"\n詳細錯誤範例 ({os.path.basename(first_error)}):")
        print("-" * 30)
        
        with open(first_error, 'r', encoding='utf-8') as f:
            error_data = json.load(f)
        
        print(f"測試ID: {error_data.get('test_id', 'N/A')}")
        print(f"時間戳: {error_data.get('timestamp', 'N/A')}")
        
        error_analysis = error_data.get('error_analysis', {})
        print(f"錯誤訊息: {error_analysis.get('error_message', 'N/A')}")
        print(f"原始回應長度: {error_analysis.get('raw_response_length', 'N/A')} 字符")
        print(f"提取JSON長度: {error_analysis.get('extracted_json_length', 'N/A')} 字符")
        
        if error_analysis.get('common_issues'):
            print("發現的問題:")
            for issue in error_analysis['common_issues']:
                print(f"  - {issue}")
        
        # 顯示部分原始回應
        raw_response = error_data.get('raw_response', '')
        if raw_response:
            print(f"\n原始回應前200字符:")
            print(repr(raw_response[:200]))
        
        # 顯示提取的JSON
        extracted_json = error_data.get('extracted_json', '')
        if extracted_json:
            print(f"\n提取的JSON前200字符:")
            print(repr(extracted_json[:200]))

def find_test_folders():
    """尋找所有測試資料夾"""
    folders = glob.glob("integration_test_*")
    return sorted(folders, reverse=True)  # 最新的在前面

def main():
    """主程式"""
    print("測試錯誤分析工具")
    print("=" * 40)
    
    # 尋找測試資料夾
    test_folders = find_test_folders()
    
    if not test_folders:
        print("找不到測試資料夾")
        print("請先執行 integration_test.py 生成測試數據")
        return
    
    print("找到以下測試資料夾:")
    for i, folder in enumerate(test_folders, 1):
        print(f"  {i}. {folder}")
    
    # 讓用戶選擇資料夾
    while True:
        try:
            choice = input(f"\n請選擇要分析的資料夾 (1-{len(test_folders)}) 或按Enter選擇最新的: ").strip()
            
            if not choice:  # 按Enter選擇最新的
                selected_folder = test_folders[0]
                break
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(test_folders):
                selected_folder = test_folders[choice_num - 1]
                break
            else:
                print(f"請輸入1到{len(test_folders)}之間的數字")
                
        except ValueError:
            print("請輸入有效的數字")
    
    # 分析選定的資料夾
    analyze_test_errors(selected_folder)

if __name__ == "__main__":
    main()