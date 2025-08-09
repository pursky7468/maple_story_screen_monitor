from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import json
import re

class AnalysisResult:
    """分析結果的標準化數據結構"""
    
    def __init__(self, 
                 full_text: str = "",
                 is_match: bool = False,
                 player_name: str = "未知",
                 channel_number: str = "未知",
                 matched_items: List[Dict] = None,
                 matched_keywords: List[str] = None,
                 confidence: float = 0.0,
                 analysis_method: str = "unknown"):
        self.full_text = full_text
        self.is_match = is_match
        self.player_name = player_name
        self.channel_number = channel_number
        self.matched_items = matched_items or []
        self.matched_keywords = matched_keywords or []
        self.confidence = confidence
        self.analysis_method = analysis_method
        
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "full_text": self.full_text,
            "is_match": self.is_match,
            "player_name": self.player_name,
            "channel_number": self.channel_number,
            "matched_items": self.matched_items,
            "matched_keywords": self.matched_keywords,
            "confidence": self.confidence,
            "analysis_method": self.analysis_method
        }
    
    def to_json(self) -> str:
        """轉換為JSON格式"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

class TextAnalyzer(ABC):
    """文字分析器的抽象基類"""
    
    def __init__(self, selling_items: Dict[str, List[str]]):
        self.selling_items = selling_items
        self.strategy_type = "BASE"  # 策略類型標識
        
    @abstractmethod
    def analyze_image(self, image) -> str:
        """分析圖片並返回原始結果"""
        pass
    
    @abstractmethod
    def parse_result(self, raw_result: str) -> AnalysisResult:
        """解析原始結果為標準化格式"""
        pass
    
    def analyze(self, image) -> tuple[AnalysisResult, str]:
        """完整分析流程，返回(分析結果, 原始回應)"""
        try:
            raw_result = self.analyze_image(image)
            parsed_result = self.parse_result(raw_result)
            return parsed_result, raw_result
        except Exception as e:
            error_result = AnalysisResult(
                full_text=f"分析錯誤: {str(e)}",
                is_match=False,
                analysis_method=self.__class__.__name__
            )
            return error_result, f"ERROR: {str(e)}"
    
    def get_error_type(self, error_message: str) -> str:
        """根據策略類型返回適當的錯誤類型"""
        return "ANALYSIS_ERROR"  # 基礎錯誤類型
    
    def is_quota_error(self, error_message: str) -> bool:
        """檢查是否為配額錯誤（由子類重寫）"""
        return False  # 基礎實現不檢查配額錯誤
    
    def extract_channel_number(self, text: str) -> str:
        """從文字中提取頻道編號（增強版）"""
        # 擴展的頻道格式匹配模式
        patterns = [
            r'CHO(\d+)',           # CHO123
            r'CH(\d+)',            # CH123  
            r'\[頻道(\d+)\]',      # [頻道1]
            r'頻道(\d+)',          # 頻道1
            r'ch(\d+)',            # ch1 (小寫)
            r'(\d+)頻道',          # 1頻道
            r'Channel\s*(\d+)',    # Channel 1
            r'CHAN\s*(\d+)',       # CHAN 1
            r'(\d+)CH',            # 1CH
            r'頻道\s*(\d+)',       # 頻道 1 (有空格)
            r'CHO\s*(\d+)',        # CHO 123 (有空格)
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                channel_num = match.group(1)
                # 根據模式決定返回格式
                if 'CHO' in pattern:
                    return f"CHO{channel_num}"
                elif 'CH' in pattern:
                    return f"CH{channel_num}"
                else:
                    return f"頻道{channel_num}"
        
        return "未知"
    
    def extract_player_name(self, text: str) -> str:
        """從文字中提取玩家名稱（增強版）"""
        # 擴展的玩家名稱匹配模式
        patterns = [
            r'^([^:\s]{2,12})\s*[:：]\s*',              # 玩家名: 或 玩家名：
            r'([A-Za-z0-9_]{3,12})\s*[:：]\s*',         # 英文玩家名:
            r'([一-龯]{2,6})\s*[:：]\s*',              # 中文玩家名:
            r'([A-Za-z][A-Za-z0-9_]{2,11})\s*[:：]',   # 字母開頭的玩家名
            r'(\w{3,12})\s*說\s*[:：]',                # 玩家名 說:
            r'<([^>]+)>\s*[:：]',                       # <玩家名>:
            r'【([^】]+)】\s*[:：]',                    # 【玩家名】:
            r'\[([^\]]+)\]\s*[:：]',                   # [玩家名]:
            r'([^:\s]+)\s*[:：]\s*收',                  # 玩家名: 收...
            r'([^:\s]+)\s*[:：]\s*買',                  # 玩家名: 買...
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                name = match.group(1).strip()
                # 驗證玩家名稱的有效性
                if self.is_valid_player_name(name):
                    return name
        
        return "未知"
    
    def is_valid_player_name(self, name: str) -> bool:
        """驗證玩家名稱是否有效"""
        if len(name) < 2 or len(name) > 12:
            return False
        
        # 排除常見的非玩家名稱
        invalid_names = [
            'CHO', 'CH', '頻道', 'Channel', 'CHAN',
            '收購', '買', '賣', '出售', '交易',
            '時間', '日期', '系統', 'System'
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
            
        return True
    
    def find_matching_items(self, text: str) -> tuple[List[Dict], List[str]]:
        """在文字中尋找匹配的商品"""
        matched_items = []
        all_matched_keywords = []
        
        text_upper = text.upper()
        
        for item_name, keywords in self.selling_items.items():
            found_keywords = []
            
            for keyword in keywords:
                if keyword.upper() in text_upper:
                    found_keywords.append(keyword)
                    all_matched_keywords.append(keyword)
            
            if found_keywords:
                matched_items.append({
                    "item_name": item_name,
                    "keywords_found": found_keywords
                })
        
        return matched_items, list(set(all_matched_keywords))
    
    def check_purchase_intent(self, text: str) -> bool:
        """檢查文字是否包含收購意圖"""
        purchase_keywords = [
            "收購", "收", "買", "要", "需要", 
            "WTB", "wtb", "Want to buy",
            "徵", "徵收", "求購"
        ]
        
        text_upper = text.upper()
        return any(keyword.upper() in text_upper for keyword in purchase_keywords)