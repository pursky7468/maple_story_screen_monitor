#!/usr/bin/env python3
"""
單白色矩形框檢測和文字分割模組
專門用於處理一個裁剪影像中只有一個白色矩形框的情況
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
import easyocr
from PIL import Image

class SingleRectangleDetector:
    """單白色矩形框檢測器"""
    
    def __init__(self, config=None):
        """初始化檢測器"""
        default_config = self._get_default_config()
        if config:
            # 合併配置，保留默認值
            default_config.update(config)
        self.config = default_config
        
    def _get_default_config(self):
        """默認檢測參數 - 針對單矩形框優化"""
        return {
            "WHITE_THRESHOLD": 240,           # 白色閾值
            "MIN_RECTANGLE_AREA": 50,         # 最小矩形面積（更寬鬆）
            "MAX_RECTANGLE_AREA": 10000,      # 最大矩形面積
            "MIN_ASPECT_RATIO": 0.1,          # 最小長寬比（更寬鬆）
            "MAX_ASPECT_RATIO": 20,           # 最大長寬比（更寬鬆）
            "FILL_RATIO_THRESHOLD": 0.6,      # 填充比率閾值（更寬鬆）
            "MORPHOLOGY_KERNEL_SIZE": 2,      # 形態學核心大小
            "CONTOUR_SIMPLIFICATION": 0.02   # 輪廓簡化係數
        }
    
    def detect_single_rectangle(self, image) -> Optional[Dict]:
        """檢測單個白色矩形框"""
        try:
            # 轉換為OpenCV格式
            cv_image = self._convert_to_cv_format(image)
            gray = self._convert_to_grayscale(cv_image)
            
            # 檢測白色區域
            white_mask = self._detect_white_regions(gray)
            
            # 尋找輪廓
            contours = self._find_contours(white_mask)
            
            # 過濾並找到最佳矩形
            best_rectangle = self._find_best_rectangle(contours)
            
            return best_rectangle
            
        except Exception as e:
            print(f"單矩形框檢測失敗: {e}")
            return None
    
    def _convert_to_cv_format(self, image):
        """轉換PIL圖片為OpenCV格式"""
        if hasattr(image, 'convert'):
            # PIL圖片
            return cv2.cvtColor(np.array(image.convert('RGB')), cv2.COLOR_RGB2BGR)
        else:
            # 假設已經是numpy array
            return image
    
    def _convert_to_grayscale(self, cv_image):
        """轉換為灰度圖"""
        if len(cv_image.shape) == 3:
            return cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        else:
            return cv_image
    
    def _detect_white_regions(self, gray_image):
        """檢測白色區域"""
        threshold = self.config["WHITE_THRESHOLD"]
        _, white_mask = cv2.threshold(gray_image, threshold, 255, cv2.THRESH_BINARY)
        
        # 形態學處理：去除噪點，連接斷開的區域
        kernel_size = self.config["MORPHOLOGY_KERNEL_SIZE"]
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
        
        # 先閉運算連接近似區域，再開運算去除噪點
        white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_CLOSE, kernel)
        white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_OPEN, kernel)
        
        return white_mask
    
    def _find_contours(self, mask):
        """尋找輪廓"""
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return contours
    
    def _find_best_rectangle(self, contours) -> Optional[Dict]:
        """找到最佳的矩形候選"""
        if not contours:
            return None
            
        candidates = []
        
        min_area = self.config["MIN_RECTANGLE_AREA"]
        max_area = self.config["MAX_RECTANGLE_AREA"]
        min_aspect_ratio = self.config["MIN_ASPECT_RATIO"]
        max_aspect_ratio = self.config["MAX_ASPECT_RATIO"]
        fill_threshold = self.config["FILL_RATIO_THRESHOLD"]
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            if min_area < area < max_area:
                # 計算邊界矩形
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                
                if min_aspect_ratio < aspect_ratio < max_aspect_ratio:
                    # 檢查是否接近矩形
                    rect_area = w * h
                    fill_ratio = area / rect_area if rect_area > 0 else 0
                    
                    if fill_ratio > fill_threshold:
                        # 計算矩形的"品質分數"
                        score = self._calculate_rectangle_score(area, aspect_ratio, fill_ratio)
                        
                        candidates.append({
                            'bbox': (x, y, x+w, y+h),
                            'center': (x + w//2, y + h//2),
                            'area': area,
                            'width': w,
                            'height': h,
                            'aspect_ratio': aspect_ratio,
                            'fill_ratio': fill_ratio,
                            'score': score,
                            'contour': contour
                        })
        
        if not candidates:
            return None
        
        # 返回得分最高的矩形
        best_rectangle = max(candidates, key=lambda r: r['score'])
        return best_rectangle
    
    def _calculate_rectangle_score(self, area, aspect_ratio, fill_ratio):
        """計算矩形品質分數"""
        # 基礎分數是面積
        score = area
        
        # 填充比率越高越好
        score *= fill_ratio
        
        # 偏好適中的長寬比（接近1或適中值）
        ideal_aspect_ratio = 2.0  # 可以調整
        aspect_penalty = abs(np.log(aspect_ratio) - np.log(ideal_aspect_ratio))
        score *= (1 / (1 + aspect_penalty))
        
        return score


class SingleRectangleTextSplitter:
    """基於單矩形框的文字分割器"""
    
    def __init__(self, languages=['ch_tra', 'en']):
        """初始化OCR讀取器"""
        self.reader = easyocr.Reader(languages)
        
    def split_text_by_rectangle(self, image, rectangle_info=None) -> Dict:
        """根據矩形框分割文字為前後兩部分"""
        try:
            # 如果沒有提供矩形框信息，先檢測
            if rectangle_info is None:
                detector = SingleRectangleDetector()
                rectangle_info = detector.detect_single_rectangle(image)
            
            # 執行OCR獲取所有文字
            image_array = np.array(image)
            ocr_results = self.reader.readtext(image_array)
            
            if not ocr_results:
                return {
                    'rectangle_found': rectangle_info is not None,
                    'rectangle_info': rectangle_info,
                    'before_rectangle': {'texts': [], 'combined': ''},
                    'after_rectangle': {'texts': [], 'combined': ''},
                    'all_texts': [],
                    'split_success': False,
                    'error': 'No OCR results found'
                }
            
            # 如果沒有找到矩形框，返回所有文字在before部分
            if rectangle_info is None:
                all_text_items = [
                    {
                        'text': text,
                        'confidence': confidence,
                        'bbox': bbox,
                        'center_x': self._get_text_center_x(bbox)
                    }
                    for bbox, text, confidence in ocr_results
                ]
                
                return {
                    'rectangle_found': False,
                    'rectangle_info': None,
                    'before_rectangle': {
                        'texts': all_text_items,
                        'combined': ' '.join([item['text'] for item in all_text_items])
                    },
                    'after_rectangle': {'texts': [], 'combined': ''},
                    'all_texts': all_text_items,
                    'split_success': False,
                    'error': 'No rectangle found'
                }
            
            # 根據矩形框位置分割文字
            rectangle_center_x = rectangle_info['center'][0]
            before_texts = []
            after_texts = []
            all_text_items = []
            
            for bbox, text, confidence in ocr_results:
                text_center_x = self._get_text_center_x(bbox)
                text_item = {
                    'text': text,
                    'confidence': confidence,
                    'bbox': bbox,
                    'center_x': text_center_x
                }
                all_text_items.append(text_item)
                
                # 根據文字中心與矩形框中心的相對位置分類
                if text_center_x < rectangle_center_x:
                    before_texts.append(text_item)
                else:
                    after_texts.append(text_item)
            
            # 按照x座標排序
            before_texts.sort(key=lambda x: x['center_x'])
            after_texts.sort(key=lambda x: x['center_x'])
            
            result = {
                'rectangle_found': True,
                'rectangle_info': rectangle_info,
                'before_rectangle': {
                    'texts': before_texts,
                    'combined': ' '.join([item['text'] for item in before_texts])
                },
                'after_rectangle': {
                    'texts': after_texts,
                    'combined': ' '.join([item['text'] for item in after_texts])
                },
                'all_texts': all_text_items,
                'split_success': True,
                'error': None
            }
            
            return result
            
        except Exception as e:
            return {
                'rectangle_found': False,
                'rectangle_info': None,
                'before_rectangle': {'texts': [], 'combined': ''},
                'after_rectangle': {'texts': [], 'combined': ''},
                'all_texts': [],
                'split_success': False,
                'error': str(e)
            }
    
    def _get_text_center_x(self, bbox):
        """獲取文字的中心X座標"""
        if isinstance(bbox[0], (list, tuple)):
            # EasyOCR格式 [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            return sum([point[0] for point in bbox]) / 4
        else:
            # 簡單邊界框格式 (x1, y1, x2, y2)
            return (bbox[0] + bbox[2]) / 2


class SingleRectangleAnalyzer:
    """完整的單矩形框分析器 - 整合檢測和分割功能"""
    
    def __init__(self, detection_config=None, ocr_languages=['ch_tra', 'en']):
        """初始化分析器"""
        self.detector = SingleRectangleDetector(detection_config)
        self.text_splitter = SingleRectangleTextSplitter(ocr_languages)
        
    def analyze_single_rectangle_image(self, image) -> Dict:
        """完整分析包含單個白色矩形框的圖片"""
        print("開始單矩形框分析...")
        
        # 1. 檢測矩形框
        print("步驟1: 檢測白色矩形框...")
        rectangle_info = self.detector.detect_single_rectangle(image)
        
        if rectangle_info:
            print(f"[成功] 檢測到矩形框: 位置{rectangle_info['bbox']}, 面積{rectangle_info['area']:.0f}")
        else:
            print("[警告] 未檢測到白色矩形框，將使用全部文字")
        
        # 2. 執行OCR和文字分割
        print("步驟2: 執行OCR並分割文字...")
        split_result = self.text_splitter.split_text_by_rectangle(image, rectangle_info)
        
        # 3. 組織結果
        analysis_result = {
            'detection_success': rectangle_info is not None,
            'rectangle_info': rectangle_info,
            'text_split_result': split_result,
            'summary': self._generate_summary(split_result)
        }
        
        # 4. 輸出結果摘要
        self._print_analysis_summary(analysis_result)
        
        return analysis_result
    
    def _generate_summary(self, split_result):
        """生成分析摘要"""
        before_text = split_result['before_rectangle']['combined']
        after_text = split_result['after_rectangle']['combined']
        
        return {
            'rectangle_found': split_result['rectangle_found'],
            'total_texts': len(split_result['all_texts']),
            'before_rectangle_texts': len(split_result['before_rectangle']['texts']),
            'after_rectangle_texts': len(split_result['after_rectangle']['texts']),
            'before_text_preview': before_text[:50] + ('...' if len(before_text) > 50 else ''),
            'after_text_preview': after_text[:50] + ('...' if len(after_text) > 50 else ''),
            'split_success': split_result['split_success']
        }
    
    def _print_analysis_summary(self, analysis_result):
        """打印分析摘要"""
        summary = analysis_result['summary']
        split_result = analysis_result['text_split_result']
        
        print("\n=== 單矩形框分析結果 ===")
        print(f"矩形框檢測: {'成功' if summary['rectangle_found'] else '失敗'}")
        print(f"文字分割: {'成功' if summary['split_success'] else '失敗'}")
        print(f"總計文字數: {summary['total_texts']}")
        
        if summary['rectangle_found']:
            print(f"矩形框前文字: {summary['before_rectangle_texts']} 個")
            print(f"矩形框後文字: {summary['after_rectangle_texts']} 個")
            
            if split_result['before_rectangle']['combined']:
                print(f"前段文字: \"{split_result['before_rectangle']['combined']}\"")
            else:
                print("前段文字: (無)")
                
            if split_result['after_rectangle']['combined']:
                print(f"後段文字: \"{split_result['after_rectangle']['combined']}\"")
            else:
                print("後段文字: (無)")
        else:
            print(f"全部文字: \"{split_result['before_rectangle']['combined']}\"")
        
        if split_result.get('error'):
            print(f"錯誤信息: {split_result['error']}")


def test_single_rectangle_analyzer():
    """測試單矩形框分析器"""
    print("=== 單矩形框分析器測試 ===\n")
    
    # 測試圖片路徑
    test_images = [
        'demo_test_results/demo_test_002_screenshot.png',
        'demo_test_results/demo_test_003_screenshot.png'
    ]
    
    analyzer = SingleRectangleAnalyzer()
    
    for img_path in test_images:
        try:
            print(f"測試圖片: {img_path}")
            
            if not os.path.exists(img_path):
                print(f"圖片不存在，跳過: {img_path}\n")
                continue
                
            # 載入圖片
            image = Image.open(img_path)
            print(f"圖片尺寸: {image.size}")
            
            # 執行分析
            result = analyzer.analyze_single_rectangle_image(image)
            
            print("\n" + "="*50 + "\n")
            
        except Exception as e:
            print(f"測試失敗: {e}")
            import traceback
            traceback.print_exc()
            print("\n" + "="*50 + "\n")


if __name__ == "__main__":
    import os
    test_single_rectangle_analyzer()