try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    easyocr = None

from text_analyzer import TextAnalyzer, AnalysisResult
import re
from typing import List, Tuple

class OCRAnalyzer(TextAnalyzer):
    """使用EasyOCR的文字分析器"""
    
    def __init__(self, selling_items: dict, languages: List[str] = None):
        super().__init__(selling_items)
        self.strategy_type = "OCR"
        
        if not EASYOCR_AVAILABLE:
            raise ImportError("EasyOCR未安裝。請執行: pip install easyocr")
        
        if languages is None:
            languages = ['ch_tra', 'en']  # 繁體中文和英文
        
        try:
            self.reader = easyocr.Reader(languages)
            print(f"OCR初始化成功，支援語言: {languages}")
        except Exception as e:
            print(f"OCR初始化失敗: {e}")
            raise
    
    def analyze_image(self, image) -> str:
        """使用OCR分析圖片"""
        if self.reader is None:
            return "ERROR: OCR未正確初始化"
        
        try:
            # 將PIL圖片轉換為numpy array
            import numpy as np
            image_array = np.array(image)
            
            # 使用EasyOCR進行文字識別
            results = self.reader.readtext(image_array)
            
            # 提取文字內容
            extracted_text = []
            for (bbox, text, confidence) in results:
                if confidence > 0.5:  # 只保留信心度高於50%的結果
                    extracted_text.append({
                        'text': text.strip(),
                        'confidence': confidence,
                        'bbox': bbox
                    })
            
            # 按照y座標排序文字（從上到下）
            extracted_text.sort(key=lambda x: x['bbox'][0][1])
            
            return extracted_text
            
        except Exception as e:
            return f"ERROR: OCR分析失敗 - {str(e)}"
    
    def parse_result(self, raw_result) -> AnalysisResult:
        """解析OCR結果"""
        if isinstance(raw_result, str) and raw_result.startswith("ERROR"):
            return AnalysisResult(
                full_text=raw_result,
                is_match=False,
                analysis_method="OCR",
                confidence=0.0
            )
        
        try:
            # 合併所有識別到的文字
            if isinstance(raw_result, list):
                full_text_parts = []
                total_confidence = 0.0
                
                for item in raw_result:
                    full_text_parts.append(item['text'])
                    total_confidence += item['confidence']
                
                full_text = ' '.join(full_text_parts)
                avg_confidence = total_confidence / len(raw_result) if raw_result else 0.0
            else:
                full_text = str(raw_result)
                avg_confidence = 0.5
            
            # 提取基本資訊
            channel_number = self.extract_channel_number(full_text)
            player_name = self.extract_player_name(full_text)
            
            # 檢查收購意圖
            has_purchase_intent = self.check_purchase_intent(full_text)
            
            # 尋找匹配商品
            matched_items, matched_keywords = self.find_matching_items(full_text)
            
            # 判斷是否匹配
            is_match = has_purchase_intent and len(matched_items) > 0
            
            return AnalysisResult(
                full_text=full_text,
                is_match=is_match,
                player_name=player_name,
                channel_number=channel_number,
                matched_items=matched_items,
                matched_keywords=matched_keywords,
                confidence=avg_confidence,
                analysis_method="OCR"
            )
            
        except Exception as e:
            return AnalysisResult(
                full_text=f"OCR解析錯誤: {str(e)}",
                is_match=False,
                analysis_method="OCR",
                confidence=0.0
            )
    
    def get_error_type(self, error_message: str) -> str:
        """OCR策略的錯誤類型"""
        return "OCR_ERROR"
    
    def is_quota_error(self, error_message: str) -> bool:
        """OCR不會有配額錯誤"""
        return False
    
    def enhance_text_recognition(self, image):
        """增強文字識別效果的預處理"""
        from PIL import Image, ImageEnhance, ImageFilter
        import numpy as np
        
        # 轉換為灰度圖
        if image.mode != 'L':
            image = image.convert('L')
        
        # 增強對比度
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # 增強銳利度
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.5)
        
        # 應用高斯模糊減少噪點
        image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        return image
    
    def format_match_info(self, result) -> str:
        """格式化匹配信息用於顯示"""
        if not result.is_match:
            return "無匹配"
        
        info_parts = []
        
        if result.player_name:
            info_parts.append(f"玩家: {result.player_name}")
        
        if result.channel_number:
            info_parts.append(f"頻道: {result.channel_number}")
        
        if result.matched_items:
            items = ", ".join(result.matched_items[:3])  # 最多顯示3個物品
            if len(result.matched_items) > 3:
                items += f" 等{len(result.matched_items)}項物品"
            info_parts.append(f"物品: {items}")
        
        if result.matched_keywords:
            keywords = ", ".join(result.matched_keywords[:3])
            info_parts.append(f"關鍵字: {keywords}")
        
        return " | ".join(info_parts)
    
    def get_text_regions(self, image) -> List[Tuple]:
        """獲取文字區域的詳細資訊"""
        if self.reader is None:
            return []
        
        try:
            import numpy as np
            image_array = np.array(image)
            results = self.reader.readtext(image_array, detail=1)
            
            text_regions = []
            for (bbox, text, confidence) in results:
                if confidence > 0.3:  # 降低閾值以獲取更多文字
                    # 計算邊界框的中心點和尺寸
                    x_coords = [point[0] for point in bbox]
                    y_coords = [point[1] for point in bbox]
                    
                    center_x = sum(x_coords) / 4
                    center_y = sum(y_coords) / 4
                    width = max(x_coords) - min(x_coords)
                    height = max(y_coords) - min(y_coords)
                    
                    text_regions.append({
                        'text': text.strip(),
                        'confidence': confidence,
                        'bbox': bbox,
                        'center': (center_x, center_y),
                        'size': (width, height)
                    })
            
            return text_regions
            
        except Exception as e:
            print(f"獲取文字區域失敗: {e}")
            return []