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
        """從文字中提取頻道編號"""
        # 匹配常見的頻道格式
        patterns = [
            r'CHO(\d+)',           # CHO123
            r'\[頻道(\d+)\]',      # [頻道1]
            r'ch(\d+)',            # ch1
            r'CH(\d+)',            # CH1
            r'頻道(\d+)',          # 頻道1
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if pattern.startswith('CHO') or pattern.startswith('CH'):
                    return f"CHO{match.group(1)}"
                else:
                    return f"頻道{match.group(1)}"
        
        return "未知"
    
    def extract_player_name(self, text: str) -> str:
        """從文字中提取玩家名稱（基本實現）"""
        # 嘗試找到冒號前的玩家名稱
        patterns = [
            r'^([^:\s]+)\s*:\s*',      # 玩家名: 內容
            r'([A-Za-z0-9_]+)\s*:\s*', # 英文玩家名: 內容
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                name = match.group(1).strip()
                # 過濾掉頻道編號
                if not re.match(r'^(CHO\d+|CH\d+|頻道\d+)$', name):
                    return name
        
        return "未知"
    
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