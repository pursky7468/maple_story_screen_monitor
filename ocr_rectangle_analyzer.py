try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    easyocr = None

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    cv2 = None

from text_analyzer import TextAnalyzer, AnalysisResult
import numpy as np
from PIL import Image, ImageEnhance
import os
from typing import List, Tuple, Optional
import re

class OCRRectangleAnalyzer(TextAnalyzer):
    """使用白框檢測的OCR分析策略"""
    
    def __init__(self, selling_items: dict, languages: List[str] = None, 
                 save_debug_images: bool = False, debug_folder: str = "rectangle_debug"):
        super().__init__(selling_items)
        self.strategy_type = "OCR_RECTANGLE"
        self.save_debug_images = save_debug_images
        self.debug_folder = debug_folder
        
        if not EASYOCR_AVAILABLE:
            raise ImportError("EasyOCR未安裝。請執行: pip install easyocr")
        
        if not OPENCV_AVAILABLE:
            raise ImportError("OpenCV未安裝。請執行: pip install opencv-python")
        
        if languages is None:
            languages = ['ch_tra', 'en']  # 繁體中文和英文
        
        try:
            self.reader = easyocr.Reader(languages)
            print(f"OCR_Rectangle初始化成功，支援語言: {languages}")
        except Exception as e:
            print(f"OCR_Rectangle初始化失敗: {e}")
            raise
        
        # 創建調試資料夾
        if self.save_debug_images and not os.path.exists(self.debug_folder):
            os.makedirs(self.debug_folder)
    
    def analyze_image(self, image) -> dict:
        """使用白框檢測的OCR分析圖片"""
        if self.reader is None:
            return {"error": "OCR未正確初始化"}
        
        try:
            # 1. 圖像預處理和二值化
            binary_image, processed_image = self.preprocess_image(image)
            
            # 2. 白框檢測
            white_rectangles = self.detect_white_rectangles(binary_image)
            
            # 3. 創建遮罩（挖除白框區域）
            masked_image = self.create_masked_image(processed_image, white_rectangles)
            
            # 4. 保存調試圖像
            if self.save_debug_images:
                self.save_debug_images_func(image, binary_image, masked_image, white_rectangles)
            
            # 5. 對遮罩後的圖像進行OCR
            ocr_results = self.perform_ocr_on_masked_image(masked_image)
            
            # 6. 分析OCR結果，分割前後兩段文字
            front_text, rear_text = self.segment_ocr_results(ocr_results)
            
            return {
                "front_text": front_text,
                "rear_text": rear_text,
                "full_text": f"{front_text} {rear_text}".strip(),
                "ocr_results": ocr_results,
                "white_rectangles": white_rectangles
            }
            
        except Exception as e:
            return {"error": f"OCR_Rectangle分析失敗: {str(e)}"}
    
    def parse_result(self, raw_result: dict) -> AnalysisResult:
        """解析OCR_Rectangle結果為標準化格式"""
        if "error" in raw_result:
            return AnalysisResult(
                full_text=raw_result["error"],
                is_match=False,
                analysis_method="OCR_Rectangle",
                confidence=0.0
            )
        
        try:
            front_text = raw_result.get("front_text", "")
            rear_text = raw_result.get("rear_text", "")
            full_text = raw_result.get("full_text", "")
            
            # 從前段文字提取玩家名稱
            player_name = self.extract_player_name_from_front(front_text)
            
            # 從後段文字提取頻道編號和商品匹配
            channel_number, has_purchase_intent, matched_items, matched_keywords = self.process_rear_segment(rear_text)
            
            # 計算平均信心度
            avg_confidence = self.calculate_average_confidence(raw_result.get("ocr_results", []))
            
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
                analysis_method="OCR_Rectangle"
            )
            
        except Exception as e:
            return AnalysisResult(
                full_text=f"OCR_Rectangle解析錯誤: {str(e)}",
                is_match=False,
                analysis_method="OCR_Rectangle",
                confidence=0.0
            )
    
    def preprocess_image(self, image) -> Tuple[np.ndarray, Image.Image]:
        """圖像預處理和二值化"""
        # 轉換為PIL圖像以便處理
        if isinstance(image, np.ndarray):
            pil_image = Image.fromarray(image)
        else:
            pil_image = image.copy()
        
        # 增強對比度和銳利度
        enhancer = ImageEnhance.Contrast(pil_image)
        enhanced = enhancer.enhance(1.5)
        enhancer = ImageEnhance.Sharpness(enhanced)
        processed_image = enhancer.enhance(1.2)
        
        # 轉換為numpy array進行二值化
        img_array = np.array(processed_image)
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # 二值化處理（門檻值255，只保留純白色）
        _, binary = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)
        
        return binary, processed_image
    
    def detect_white_rectangles(self, binary_image: np.ndarray) -> List[Tuple]:
        """檢測白色矩形邊界"""
        # 尋找輪廓
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        rectangles = []
        for contour in contours:
            # 計算輪廓的邊界矩形
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            
            # 過濾太小或太大的矩形
            if 100 < area < 5000:
                # 檢查是否接近矩形（縱橫比合理）
                aspect_ratio = w / h if h > 0 else 0
                if 0.2 < aspect_ratio < 10:
                    rectangles.append((x, y, w, h))
        
        return rectangles
    
    def create_masked_image(self, processed_image: Image.Image, white_rectangles: List[Tuple]) -> Image.Image:
        """創建遮罩圖像，挖除白框區域"""
        img_array = np.array(processed_image)
        mask = np.ones(img_array.shape[:2], dtype=np.uint8) * 255
        
        # 在白框區域創建黑色遮罩
        for x, y, w, h in white_rectangles:
            mask[y:y+h, x:x+w] = 0
        
        # 應用遮罩
        if len(img_array.shape) == 3:
            masked_array = img_array.copy()
            masked_array[mask == 0] = [0, 0, 0]  # 白框區域設為黑色
        else:
            masked_array = img_array.copy()
            masked_array[mask == 0] = 0
        
        return Image.fromarray(masked_array)
    
    def perform_ocr_on_masked_image(self, masked_image: Image.Image) -> List[dict]:
        """對遮罩後的圖像進行OCR"""
        img_array = np.array(masked_image)
        
        # 使用EasyOCR進行文字識別
        results = self.reader.readtext(img_array, min_size=5, text_threshold=0.6, low_text=0.3)
        
        ocr_results = []
        for (bbox, text, confidence) in results:
            if confidence > 0.1:  # 使用較低閾值以獲取更多文字
                ocr_results.append({
                    'text': text.strip(),
                    'confidence': confidence,
                    'bbox': bbox
                })
        
        # 按x座標排序（從左到右）
        ocr_results.sort(key=lambda x: x['bbox'][0][0])
        
        return ocr_results
    
    def segment_ocr_results(self, ocr_results: List[dict]) -> Tuple[str, str]:
        """分割OCR結果為前後兩段文字"""
        if not ocr_results:
            return "", ""
        
        all_texts = [result['text'] for result in ocr_results]
        full_text = ' '.join(all_texts)
        
        # 尋找合適的分割點
        if len(all_texts) >= 2:
            # 找到第一個可能是玩家名稱的文字作為前段
            front_candidates = []
            rear_texts = []
            
            for i, text in enumerate(all_texts):
                if self.is_likely_player_name(text) and i < len(all_texts) // 2:
                    # 前半部分可能是玩家名稱
                    front_candidates.append(text)
                else:
                    rear_texts.append(text)
            
            if front_candidates:
                front_text = front_candidates[0]  # 取第一個可能的玩家名稱
                rear_text = ' '.join(rear_texts)
            else:
                # 如果沒有明顯的玩家名稱，簡單按位置分割
                split_index = len(all_texts) // 2
                front_text = ' '.join(all_texts[:split_index])
                rear_text = ' '.join(all_texts[split_index:])
        else:
            # 只有一個文字，全部當作前段
            front_text = all_texts[0] if all_texts else ""
            rear_text = ""
        
        return front_text, rear_text
    
    def extract_player_name_from_front(self, front_text: str) -> str:
        """從前段文字提取玩家名稱"""
        if not front_text:
            return "未知"
        
        # 清理文字
        cleaned_text = front_text.strip()
        
        # 如果長度合理，直接使用
        if 2 <= len(cleaned_text) <= 12 and self.is_valid_player_name(cleaned_text):
            return cleaned_text
        
        # 嘗試使用父類的標準提取方法
        standard_name = self.extract_player_name(front_text)
        if standard_name != "未知":
            return standard_name
        
        # 如果都失敗，返回清理後的文字或未知
        return cleaned_text if cleaned_text else "未知"
    
    def process_rear_segment(self, rear_text: str) -> Tuple[str, bool, List[dict], List[str]]:
        """處理後段文字，提取頻道編號、檢查收購意圖和匹配商品（使用上下文分析）"""
        if not rear_text:
            return "未知", False, [], []
        
        # 0. 清理冒號：移除後段文字開頭的冒號
        cleaned_rear_text = self.remove_leading_colon(rear_text)
        
        # 1. 提取頻道編號（從原始文字中提取，因為頻道可能在冒號前）
        channel_number = self.extract_channel_number(rear_text)
        
        # 2. 使用新的上下文分析進行智能匹配
        is_match, matched_items, matched_keywords, context_info = self.analyze_context_matching(cleaned_rear_text)
        
        return channel_number, is_match, matched_items, matched_keywords
    
    def check_selling_intent(self, text: str) -> tuple[bool, list]:
        """檢查文字是否包含出售意圖，返回(是否有出售意圖, 出售關鍵字位置列表)"""
        selling_keywords = [
            "出售", "賣", "售", "銷售", "便宜賣", "急售",
            "WTS", "wts", "Want to sell", "selling",
            "處理", "清倉", "割愛"
        ]
        
        text_upper = text.upper()
        positions = []
        
        for keyword in selling_keywords:
            start_pos = 0
            while True:
                pos = text_upper.find(keyword.upper(), start_pos)
                if pos == -1:
                    break
                positions.append({
                    'keyword': keyword,
                    'start': pos,
                    'end': pos + len(keyword),
                    'type': 'sell'
                })
                start_pos = pos + 1
        
        return len(positions) > 0, positions
    
    def check_purchase_intent_with_positions(self, text: str) -> tuple[bool, list]:
        """檢查文字是否包含收購意圖，返回(是否有收購意圖, 收購關鍵字位置列表)"""
        purchase_keywords = [
            "收購", "收", "買", "要", "需要", 
            "WTB", "wtb", "Want to buy",
            "徵", "徵收", "求購"
        ]
        
        text_upper = text.upper()
        positions = []
        
        for keyword in purchase_keywords:
            start_pos = 0
            while True:
                pos = text_upper.find(keyword.upper(), start_pos)
                if pos == -1:
                    break
                positions.append({
                    'keyword': keyword,
                    'start': pos,
                    'end': pos + len(keyword),
                    'type': 'buy'
                })
                start_pos = pos + 1
        
        return len(positions) > 0, positions
    
    def find_matching_items_with_positions(self, text: str) -> tuple[list, list, list]:
        """在文字中尋找匹配的商品，返回(匹配商品, 關鍵字, 商品位置)"""
        matched_items = []
        all_matched_keywords = []
        item_positions = []
        
        text_upper = text.upper()
        
        for item_name, keywords in self.selling_items.items():
            found_keywords = []
            
            for keyword in keywords:
                start_pos = 0
                while True:
                    pos = text_upper.find(keyword.upper(), start_pos)
                    if pos == -1:
                        break
                    
                    found_keywords.append(keyword)
                    all_matched_keywords.append(keyword)
                    item_positions.append({
                        'item_name': item_name,
                        'keyword': keyword,
                        'start': pos,
                        'end': pos + len(keyword)
                    })
                    start_pos = pos + 1
            
            if found_keywords:
                matched_items.append({
                    "item_name": item_name,
                    "keywords_found": list(set(found_keywords))  # 去重
                })
        
        return matched_items, list(set(all_matched_keywords)), item_positions
    
    def analyze_context_matching(self, text: str) -> tuple[bool, list, list, dict]:
        """使用上下文分析進行智能匹配"""
        # 1. 獲取買賣意圖和位置
        has_purchase, purchase_positions = self.check_purchase_intent_with_positions(text)
        has_selling, selling_positions = self.check_selling_intent(text)
        
        # 2. 獲取商品匹配和位置
        matched_items, matched_keywords, item_positions = self.find_matching_items_with_positions(text)
        
        # 3. 如果沒有匹配的商品，直接返回
        if not matched_items:
            return False, [], [], {
                'analysis': 'no_items_found',
                'purchase_positions': purchase_positions,
                'selling_positions': selling_positions,
                'item_positions': item_positions
            }
        
        # 4. 如果只有收購意圖，沒有出售意圖
        if has_purchase and not has_selling:
            return True, matched_items, matched_keywords, {
                'analysis': 'purchase_only',
                'purchase_positions': purchase_positions,
                'selling_positions': selling_positions,
                'item_positions': item_positions
            }
        
        # 5. 如果只有出售意圖，沒有收購意圖
        if has_selling and not has_purchase:
            return False, [], [], {
                'analysis': 'selling_only',
                'purchase_positions': purchase_positions,
                'selling_positions': selling_positions,
                'item_positions': item_positions
            }
        
        # 6. 如果兩種意圖都有，需要分析商品在哪個section
        if has_purchase and has_selling:
            valid_items = []
            valid_keywords = []
            
            for item_pos in item_positions:
                item_start = item_pos['start']
                
                # 找到最近的收購和出售關鍵字
                closest_purchase = self.find_closest_intent(item_start, purchase_positions)
                closest_selling = self.find_closest_intent(item_start, selling_positions)
                
                # 判斷商品更靠近哪種意圖
                if closest_purchase and closest_selling:
                    purchase_distance = abs(item_start - closest_purchase['start'])
                    selling_distance = abs(item_start - closest_selling['start'])
                    
                    # 如果商品更靠近收購關鍵字，且距離明顯更近
                    if purchase_distance < selling_distance:
                        self.add_valid_item(item_pos, valid_items, valid_keywords)
                elif closest_purchase:  # 只找到收購關鍵字
                    self.add_valid_item(item_pos, valid_items, valid_keywords)
                # 如果只找到出售關鍵字或者更靠近出售關鍵字，不添加
            
            return len(valid_items) > 0, valid_items, valid_keywords, {
                'analysis': 'mixed_intents',
                'purchase_positions': purchase_positions,
                'selling_positions': selling_positions,
                'item_positions': item_positions,
                'valid_items': valid_items
            }
        
        # 7. 如果沒有任何買賣意圖
        return False, [], [], {
            'analysis': 'no_intent',
            'purchase_positions': purchase_positions,
            'selling_positions': selling_positions,
            'item_positions': item_positions
        }
    
    def find_closest_intent(self, item_position: int, intent_positions: list) -> dict:
        """找到最接近商品位置的意圖關鍵字"""
        if not intent_positions:
            return None
        
        closest = None
        min_distance = float('inf')
        
        for intent in intent_positions:
            distance = abs(item_position - intent['start'])
            if distance < min_distance:
                min_distance = distance
                closest = intent
        
        return closest
    
    def add_valid_item(self, item_pos: dict, valid_items: list, valid_keywords: list):
        """添加有效的商品到結果列表"""
        item_name = item_pos['item_name']
        keyword = item_pos['keyword']
        
        # 檢查是否已經有這個商品
        existing_item = None
        for item in valid_items:
            if item['item_name'] == item_name:
                existing_item = item
                break
        
        if existing_item:
            if keyword not in existing_item['keywords_found']:
                existing_item['keywords_found'].append(keyword)
        else:
            valid_items.append({
                'item_name': item_name,
                'keywords_found': [keyword]
            })
        
        if keyword not in valid_keywords:
            valid_keywords.append(keyword)
    
    def extract_channel_number(self, text: str) -> str:
        """從文字中提取頻道編號（OCR_Rectangle版本，只返回純數字）"""
        # 擴展的頻道格式匹配模式，但只返回數字部分
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
                # OCR_Rectangle策略：只返回純數字
                return channel_num
        
        # 如果沒有找到格式化的頻道，嘗試找獨立的數字
        # 修正：使用更適合中文環境的數字匹配模式
        # 匹配3-4位數字，後面跟非數字字符或字串結尾
        standalone_numbers = re.findall(r'(\d{3,4})(?=[^\d]|$)', text)
        if standalone_numbers:
            # 返回第一個合理範圍的數字（100-9999，排除過小的數字）
            for num in standalone_numbers:
                channel_int = int(num)
                # 頻道編號通常在100-9999範圍內
                if 100 <= channel_int <= 9999:
                    return num
        
        return "未知"
    
    def remove_leading_colon(self, text: str) -> str:
        """移除後段文字開頭的冒號和冒號前的內容，保留真正的廣播內容"""
        if not text:
            return text
        
        # 尋找冒號位置（支援中英文冒號）
        colon_patterns = [':', '：']
        
        for colon in colon_patterns:
            if colon in text:
                # 找到第一個冒號的位置
                colon_index = text.find(colon)
                # 返回冒號後的內容，去除前後空白
                cleaned_text = text[colon_index + 1:].strip()
                
                # 如果清理後的文字不為空，返回清理結果
                if cleaned_text:
                    return cleaned_text
        
        # 如果沒有找到冒號，返回原始文字
        return text.strip()
    
    def is_likely_player_name(self, text: str) -> bool:
        """判斷文字是否可能是玩家名稱"""
        if len(text) < 2 or len(text) > 15:
            return False
        
        # 排除明顯的非玩家名內容
        exclude_patterns = [
            r'^\d+$',                    # 純數字
            r'^CHO?\d+$',               # 頻道格式
            r'收購|買|賣|出售|WTB',      # 交易關鍵字
            r'^\W+$',                   # 純符號
        ]
        
        for pattern in exclude_patterns:
            if re.search(pattern, text):
                return False
        
        # 玩家名稱通常包含字母、數字或中文
        if re.search(r'[A-Za-z0-9\u4e00-\u9fff]', text):
            return True
        
        return False
    
    def calculate_average_confidence(self, ocr_results: List[dict]) -> float:
        """計算平均信心度"""
        if not ocr_results:
            return 0.0
        
        total_confidence = sum(result['confidence'] for result in ocr_results)
        return total_confidence / len(ocr_results)
    
    def save_debug_images_func(self, original_image, binary_image, masked_image, white_rectangles):
        """保存調試圖像"""
        import time
        timestamp = int(time.time() * 1000)
        
        try:
            # 保存二值化圖像
            binary_pil = Image.fromarray(binary_image)
            binary_path = os.path.join(self.debug_folder, f"{timestamp}_binary.png")
            binary_pil.save(binary_path)
            
            # 保存遮罩圖像
            masked_path = os.path.join(self.debug_folder, f"{timestamp}_masked.png")
            masked_image.save(masked_path)
            
            # 保存白框檢測結果圖像
            debug_image = np.array(original_image.copy() if hasattr(original_image, 'copy') else Image.fromarray(original_image))
            for x, y, w, h in white_rectangles:
                cv2.rectangle(debug_image, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            debug_pil = Image.fromarray(debug_image)
            debug_path = os.path.join(self.debug_folder, f"{timestamp}_rectangle_debug.png")
            debug_pil.save(debug_path)
            
            print(f"調試圖像已保存到 {self.debug_folder}")
            
        except Exception as e:
            print(f"保存調試圖像失敗: {e}")
    
    def get_error_type(self, error_message: str) -> str:
        """OCR_Rectangle策略的錯誤類型"""
        return "OCR_RECTANGLE_ERROR"
    
    def is_quota_error(self, error_message: str) -> bool:
        """OCR不會有配額錯誤"""
        return False