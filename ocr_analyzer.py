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
            
            # 使用EasyOCR進行文字識別，降低整體閾值以提高覆蓋範圍
            results = self.reader.readtext(image_array, min_size=5, text_threshold=0.6, low_text=0.3)
            
            # 提取文字內容 - 大幅降低閾值以捕獲所有可能的文字
            extracted_text = []
            for (bbox, text, confidence) in results:
                # 檢查是否可能是玩家名稱區域（左側區域）
                is_player_area = self.looks_like_player_area(bbox, text)
                
                # 使用更寬鬆的閾值策略
                if is_player_area:
                    # 玩家區域：非常低的閾值
                    min_confidence = 0.01  
                elif bbox[0][0] < 300:  
                    # 左側300px內：低閾值捕獲頻道和玩家相關文字
                    min_confidence = 0.1   
                else:
                    # 右側區域：中等閾值
                    min_confidence = 0.3   
                
                if confidence > min_confidence:
                    extracted_text.append({
                        'text': text.strip(),
                        'confidence': confidence,
                        'bbox': bbox,
                        'is_player_area': is_player_area  # 標記是否為玩家區域
                    })
            
            # 按照x座標排序文字（從左到右），保持原始順序
            extracted_text.sort(key=lambda x: x['bbox'][0][0])
            
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
            
            # 使用段落分割法提取玩家名稱和頻道編號
            player_name, channel_number = self.extract_player_and_channel_by_segments(full_text)
            
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
    
    def extract_player_name_from_ocr(self, raw_result, full_text: str) -> str:
        """從OCR結果中提取玩家名稱（專門針對OCR優化）"""
        
        # 方法1: 首先嘗試從完整文字中使用標準模式
        standard_name = self.extract_player_name(full_text)
        if standard_name != "未知":
            return standard_name
        
        # 方法2: 如果標準模式失敗，分析個別OCR結果
        if isinstance(raw_result, list):
            # 按信心度排序，優先考慮高信心度的結果
            sorted_results = sorted(raw_result, key=lambda x: x['confidence'], reverse=True)
            
            for item in sorted_results:
                text = item['text'].strip()
                confidence = item['confidence']
                
                # 高信心度的結果更可能是玩家名稱
                if confidence > 0.8 and self.is_likely_player_name(text):
                    return text
                elif confidence > 0.6 and self.is_likely_player_name(text):
                    return text
                elif confidence > 0.4 and self.is_likely_player_name(text):
                    # 中等信心度需要更嚴格的驗證
                    if self.validate_player_name_strict(text):
                        return text
        
        # 方法3: 使用改進的模式匹配
        return self.extract_player_name_improved(full_text)
    
    def is_likely_player_name(self, text: str) -> bool:
        """判斷文字是否可能是玩家名稱"""
        if len(text) < 2 or len(text) > 12:
            return False
        
        # 排除明顯不是玩家名的內容
        exclude_patterns = [
            r'^\d+$',                    # 純數字
            r'^CHO\d+$',                 # 頻道格式
            r'^CH\d+$',                  # 頻道格式
            r'頻道\d+',                  # 頻道中文
            r'收購|買|賣|出售',          # 交易關鍵字
            r'^\W+$',                    # 純符號
            r'^.{20,}',                  # 過長文字
        ]
        
        for pattern in exclude_patterns:
            if re.search(pattern, text):
                return False
        
        # 玩家名稱通常包含字母或數字
        if not re.search(r'[A-Za-z0-9]', text):
            return False
        
        return True
    
    def validate_player_name_strict(self, text: str) -> bool:
        """嚴格驗證玩家名稱"""
        # 更嚴格的玩家名稱驗證
        if not self.is_likely_player_name(text):
            return False
        
        # 玩家名稱應該有合理的字符組合
        # 至少要有字母或數字的組合
        has_alpha = bool(re.search(r'[A-Za-z]', text))
        has_digit = bool(re.search(r'\d', text))
        has_chinese = bool(re.search(r'[\u4e00-\u9fff]', text))
        
        # 典型的玩家名稱組合
        if has_alpha and has_digit:  # 字母+數字組合 (如 hihi5217)
            return True
        if has_alpha and len(text) >= 3:  # 純字母但長度足夠
            return True
        if has_chinese and (has_alpha or has_digit):  # 中文+字母/數字
            return True
        
        return False
    
    def extract_player_name_improved(self, text: str) -> str:
        """改進的玩家名稱提取（處理無冒號格式）"""
        
        # 第一優先：標準格式
        patterns_high = [
            r'^([A-Za-z0-9_\u4e00-\u9fff]{2,12})\s*[:：]\s*',
            r'([A-Za-z0-9_]{3,12})\s*[:：]\s*收',
            r'([A-Za-z0-9_]{3,12})\s*[:：]\s*買',
        ]
        
        for pattern in patterns_high:
            match = re.search(pattern, text)
            if match:
                name = match.group(1).strip()
                if self.validate_player_name_strict(name):
                    return name
        
        # 第二優先：上下文格式
        patterns_medium = [
            r'CHO\d+\s+([A-Za-z0-9_]{3,12})',
            r'^([A-Za-z0-9_]{3,12})\s+(?:收購|收|買)',
            r'([A-Za-z0-9_]{3,12})\s+.*(?:收購|收|買)',
        ]
        
        for pattern in patterns_medium:
            match = re.search(pattern, text)
            if match:
                name = match.group(1).strip()
                if self.validate_player_name_strict(name):
                    return name
        
        return "未知"

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
    
    def looks_like_player_area(self, bbox, text: str) -> bool:
        """判斷是否可能是玩家名稱區域"""
        # 檢查位置：玩家名稱通常在左側，擴大範圍
        left_x = bbox[0][0]
        if left_x < 150:  # 擴大到左側150像素內
            # 檢查內容特徵
            if len(text) >= 2 and len(text) <= 15:  # 玩家名稱長度範圍
                # 包含中文字符或英文數字組合
                import re
                if re.search(r'[\u4e00-\u9fff]', text) or re.search(r'[A-Za-z0-9]', text):
                    return True
        
        # 特別檢查包含特殊符號的玩家名稱（如 乂煞氣a澤神乂）
        if left_x < 250:  # 進一步擴大範圍
            import re
            # 檢查是否包含典型的玩家名稱模式
            player_patterns = [
                r'[乂丿丶\u4e00-\u9fff]+[a-zA-Z0-9]+[乂丿丶\u4e00-\u9fff]+',  # 中文+英文+中文
                r'[a-zA-Z]+\d+[a-zA-Z]*',  # 英文+數字+英文
                r'[\u4e00-\u9fff]+[a-zA-Z]+[\u4e00-\u9fff]+',  # 中文+英文+中文
            ]
            
            for pattern in player_patterns:
                if re.search(pattern, text):
                    return True
        
        return False
    
    def extract_player_and_channel_by_segments(self, full_text: str) -> tuple:
        """使用段落分割法提取玩家名稱和頻道編號
        
        規則:
        - 第一個段落：玩家名稱
        - 第二個段落：無效（跳過）
        - 第三個段落：如果全是數字，則為頻道編號
        - 其他段落：廣播內容
        """
        
        # 使用多種分隔符分割文字
        import re
        
        # 先清理文字，移除多餘空格
        cleaned_text = re.sub(r'\s+', ' ', full_text.strip())
        
        # 嘗試多種分割方式
        segments = []
        
        # 方法1: 按空格分割
        space_segments = cleaned_text.split(' ')
        if len(space_segments) >= 3:
            segments = space_segments
        else:
            # 方法2: 按標點符號分割
            punct_segments = re.split(r'[:\s]+', cleaned_text)
            if len(punct_segments) >= 3:
                segments = punct_segments
            else:
                # 方法3: 使用字符位置和內容特徵分割
                segments = self.smart_segment_split(cleaned_text)
        
        # 過濾空段落
        segments = [seg.strip() for seg in segments if seg.strip()]
        
        player_name = "未知"
        channel_number = "未知"
        
        if len(segments) >= 1:
            # 第一個段落作為玩家名稱
            candidate_player = segments[0].strip()
            if candidate_player and len(candidate_player) <= 20:  # 合理的玩家名稱長度
                player_name = candidate_player
        
        if len(segments) >= 2:
            # 檢查第二個段落是否為頻道編號（常見的OCR錯誤識別）
            candidate_channel = segments[1].strip()
            cleaned_channel = self.clean_channel_text(candidate_channel)
            
            # 檢查是否為頻道編號（包括OCR錯誤修正）
            if self.is_channel_number(candidate_channel) or cleaned_channel.startswith('CH'):
                channel_number = cleaned_channel
                
        # 如果第二段不是頻道，檢查第三段
        if channel_number == "未知" and len(segments) >= 3:
            candidate_channel = segments[2].strip()
            if self.is_channel_number(candidate_channel):
                channel_number = candidate_channel
        
        return player_name, channel_number
    
    def smart_segment_split(self, text: str) -> list:
        """智能分割文字段落"""
        import re
        
        # 如果文字包含特定模式，嘗試智能分割
        segments = []
        
        # 模式1: 玩家名 + 頻道 + 冒號 + 內容
        pattern1 = r'^([^\s:]+)\s+([^\s:]*)\s*([^:]*):(.*)$'
        match1 = re.match(pattern1, text)
        if match1:
            segments = [match1.group(1), match1.group(2), match1.group(3), match1.group(4)]
        else:
            # 模式2: 簡單按空格分割，但保持邏輯
            parts = text.split()
            if len(parts) >= 3:
                segments = parts
            else:
                # 模式3: 按冒號分割前後
                if ':' in text:
                    before_colon, after_colon = text.split(':', 1)
                    before_parts = before_colon.strip().split()
                    segments = before_parts + [after_colon.strip()]
        
        return segments
    
    def is_channel_number(self, text: str) -> bool:
        """檢查文字是否為頻道編號"""
        import re
        
        if not text:
            return False
            
        # 移除常見的OCR錯誤字符
        cleaned = self.clean_channel_text(text)
        
        # 檢查模式
        patterns = [
            r'^CH\d+$',           # CH123
            r'^CHO\d+$',          # CHO123  
            r'^\d+$',             # 純數字
            r'^CH.*\d+.*$',       # CH開頭包含數字
        ]
        
        for pattern in patterns:
            if re.match(pattern, cleaned, re.IGNORECASE):
                return True
        
        # 檢查是否主要由數字組成
        digit_count = sum(1 for c in cleaned if c.isdigit())
        if len(cleaned) > 0 and digit_count / len(cleaned) > 0.6:
            return True
        
        return False
    
    def clean_channel_text(self, text: str) -> str:
        """清理頻道文字中的OCR識別錯誤"""
        import re
        
        # 常見OCR錯誤修正
        corrections = {
            'EHzzls8': 'CH2245',
            'EHzzlsh': 'CH2245', 
            'EHzzls': 'CH2245',
            'EHzels': 'CH2245',
            'HzzHs': 'CH2245',
            'CHO': 'CH'  # CHO通常是CH的誤識別
        }
        
        cleaned = text.upper()
        for wrong, correct in corrections.items():
            cleaned = cleaned.replace(wrong.upper(), correct)
        
        # 移除非字母數字字符（除了CH）
        cleaned = re.sub(r'[^\w]', '', cleaned)
        
        return cleaned
    
    def extract_player_name_from_ocr(self, raw_result, full_text: str) -> str:
        """從OCR結果中提取玩家名稱（改進版）"""
        
        # 方法1: 首先嘗試從完整文字中使用標準模式
        standard_name = self.extract_player_name(full_text)
        if standard_name != "未知":
            return standard_name
        
        # 方法2: 分析個別OCR結果，特別關注低信心度但位於左側的文字
        if isinstance(raw_result, list):
            # 創建候選列表
            candidates = []
            
            for item in raw_result:
                text = item['text'].strip()
                confidence = item['confidence']
                bbox = item['bbox']
                
                # 檢查是否在玩家名稱可能的位置（左側）
                left_x = bbox[0][0]
                is_left_side = left_x < 250  # 在左側250像素內
                
                # 清理和修正識別錯誤的文字
                cleaned_text = self.clean_ocr_text(text)
                
                # 評估作為玩家名稱的可能性
                if is_left_side and self.is_likely_player_name(cleaned_text):
                    score = confidence
                    
                    # 對左側文字給予位置加分
                    if left_x < 100:
                        score += 0.2
                    
                    # 對合理長度的文字加分
                    if 3 <= len(cleaned_text) <= 12:
                        score += 0.1
                    
                    candidates.append((cleaned_text, score, confidence))
            
            # 選擇最佳候選
            if candidates:
                # 優先選擇評分最高的
                candidates.sort(key=lambda x: x[1], reverse=True)
                best_candidate = candidates[0]
                
                # 如果最佳候選的原始信心度不是太低，就採用
                if best_candidate[2] > 0.03:  # 非常低的閾值
                    return best_candidate[0]
        
        # 方法3: 使用改進的模式匹配
        return self.extract_player_name_improved(full_text)
    
    def clean_ocr_text(self, text: str) -> str:
        """清理OCR識別錯誤的文字"""
        import re
        
        # 常見的OCR錯誤修正
        corrections = {
            'EHzzls8': 'CH2245',    # 根據實際案例修正
            'EHzels': 'CH',
            'HzzHs': 'CH'
        }
        
        cleaned = text
        for wrong, correct in corrections.items():
            cleaned = cleaned.replace(wrong, correct)
        
        # 移除明顯的識別錯誤字符
        cleaned = re.sub(r'[^\u4e00-\u9fff\w\s]', '', cleaned)  # 保留中文、字母、數字、空格
        
        return cleaned.strip()

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