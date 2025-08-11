#!/usr/bin/env python3
"""
測試玩家名稱提取功能
"""

import re
from text_analyzer import TextAnalyzer

class TestAnalyzer(TextAnalyzer):
    """測試用分析器"""
    def __init__(self):
        super().__init__({})
        
    def analyze_image(self, image):
        return "test"
        
    def parse_result(self, raw_result):
        return None

def test_player_name_patterns():
    """測試玩家名稱匹配模式"""
    analyzer = TestAnalyzer()
    
    # 測試案例
    test_cases = [
        # 基於實際OCR結果
        "hihi5217: 收購披敏",
        "hihi5217 說: 收披風",
        "【hihi5217】: 買東西",
        "[hihi5217]: 收東西",
        "<hihi5217>: 想買",
        "hihi5217：收購物品",  # 中文冒號
        
        # 其他常見格式
        "玩家ABC: 收購",
        "test123: 收",
        "中文玩家: 買東西",
        "Player_Name: WTB item",
        
        # 從實際OCR結果中提取的字串
        "hihi5217 TH1E收= 1623自由一六營營在專門6|7/8|9處3/8/15|22者 康康門康康60%6處",
        "hihi5217 收購披敏",
        "收購 hihi5217 披風敏捷",
        "CHO241 hihi5217: 收購披敏"
    ]
    
    print("=== 測試玩家名稱提取 ===")
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n測試 {i}: '{text}'")
        
        # 使用現有的提取方法
        player_name = analyzer.extract_player_name(text)
        print(f"  提取結果: '{player_name}'")
        
        # 測試新的改進模式
        improved_name = extract_player_name_improved(text)
        print(f"  改進結果: '{improved_name}'")

def extract_player_name_improved(text: str) -> str:
    """改進的玩家名稱提取函數"""
    
    # 第一優先：標準格式 "玩家名: " 或 "玩家名："
    patterns_high_priority = [
        r'^([A-Za-z0-9_\u4e00-\u9fff]{2,12})\s*[:：]\s*',     # 開頭的玩家名:
        r'([A-Za-z][A-Za-z0-9_]{2,11})\s*[:：]\s*',         # 字母開頭的玩家名:
        r'([A-Za-z0-9_]{3,12})\s*[:：]\s*收',               # 玩家名: 收...
        r'([A-Za-z0-9_]{3,12})\s*[:：]\s*買',               # 玩家名: 買...
        r'<([A-Za-z0-9_\u4e00-\u9fff]{2,12})>\s*[:：]',     # <玩家名>:
        r'【([A-Za-z0-9_\u4e00-\u9fff]{2,12})】\s*[:：]',   # 【玩家名】:
        r'\[([A-Za-z0-9_\u4e00-\u9fff]{2,12})\]\s*[:：]',   # [玩家名]:
    ]
    
    # 第二優先：上下文中的玩家名
    patterns_medium_priority = [
        r'CHO\d+\s+([A-Za-z0-9_]{3,12})\s*[:：]',           # CHO123 玩家名:
        r'([A-Za-z0-9_]{3,12})\s+(?:收購|收|買|要)',         # 玩家名 收購
        r'^([A-Za-z0-9_]{3,12})\s+\w+',                    # 開頭的玩家名
    ]
    
    # 高優先級模式
    for pattern in patterns_high_priority:
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            name = match.group(1).strip()
            if is_valid_player_name_improved(name):
                return name
    
    # 中等優先級模式
    for pattern in patterns_medium_priority:
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            name = match.group(1).strip()
            if is_valid_player_name_improved(name):
                return name
    
    return "未知"

def is_valid_player_name_improved(name: str) -> bool:
    """改進的玩家名稱驗證"""
    if len(name) < 2 or len(name) > 12:
        return False
    
    # 排除常見的非玩家名稱
    invalid_names = [
        'CHO', 'CH', '頻道', 'Channel', 'CHAN', 'TH1E', 
        '收購', '買', '賣', '出售', '交易',
        '時間', '日期', '系統', 'System', '處'
    ]
    
    for invalid in invalid_names:
        if invalid.upper() in name.upper():
            return False
    
    # 排除純數字
    if name.isdigit():
        return False
    
    # 排除頻道格式
    if re.match(r'^(CHO\d+|CH\d+|頻道\d+|\d+頻道)$', name):
        return False
    
    # 確保至少包含字母或數字
    if not re.search(r'[A-Za-z0-9]', name):
        return False
        
    return True

def test_ocr_result_parsing():
    """測試實際OCR結果解析"""
    print("\n=== 測試實際OCR結果 ===")
    
    # 模擬OCR識別結果
    ocr_results = [
        {
            'text': 'hihi5217',
            'confidence': 0.996,
            'bbox': [[10, 5], [80, 5], [80, 20], [10, 20]]
        },
        {
            'text': 'TH1E收=',
            'confidence': 0.355,
            'bbox': [[85, 5], [140, 5], [140, 20], [85, 20]]
        },
        {
            'text': '1623自由一六營營在專門6|7/8|9處3/8/15|22者 康康門康康60%6處',
            'confidence': 0.552,
            'bbox': [[145, 5], [900, 5], [900, 20], [145, 20]]
        }
    ]
    
    # 重建完整文字
    full_text = ' '.join([item['text'] for item in ocr_results])
    print(f"完整文字: '{full_text}'")
    
    # 測試提取
    analyzer = TestAnalyzer()
    original_name = analyzer.extract_player_name(full_text)
    improved_name = extract_player_name_improved(full_text)
    
    print(f"原始方法: '{original_name}'")
    print(f"改進方法: '{improved_name}'")
    
    # 分析個別文字片段
    print("\n分析個別OCR結果:")
    for i, item in enumerate(ocr_results):
        text = item['text']
        conf = item['confidence']
        print(f"  {i+1}. '{text}' (信心度: {conf})")
        
        # 檢查是否像玩家名
        if is_valid_player_name_improved(text):
            print(f"     -> 可能是玩家名")
        else:
            print(f"     -> 不是玩家名")

if __name__ == "__main__":
    test_player_name_patterns()
    test_ocr_result_parsing()
    
    print("\n=== 問題分析 ===")
    print("1. OCR能夠識別出玩家名稱 'hihi5217'")
    print("2. 但名稱後面沒有標準的冒號格式")
    print("3. 需要改進名稱提取邏輯，處理無冒號的情況")
    print("4. 應該優先提取高信心度的獨立詞語作為玩家名")