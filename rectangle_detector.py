import cv2
import numpy as np
from typing import List, Dict, Tuple
import os
import json
from datetime import datetime
from PIL import Image, ImageDraw

class RectangleDetectionStrategy:
    """白色矩形框檢測策略"""
    
    def __init__(self, config=None):
        """初始化檢測參數"""
        self.config = config or self._get_default_config()
    
    def _get_default_config(self):
        """默認檢測參數"""
        return {
            "WHITE_THRESHOLD": 240,
            "MIN_RECTANGLE_AREA": 100,
            "MAX_RECTANGLE_AREA": 5000,
            "MIN_ASPECT_RATIO": 0.2,
            "MAX_ASPECT_RATIO": 10,
            "FILL_RATIO_THRESHOLD": 0.7,
            "TEXT_ASSIGNMENT_TOLERANCE": 5,
            "MORPHOLOGY_KERNEL_SIZE": 3,
            "CONTOUR_AREA_FILTER": True
        }
    
    def detect_white_rectangles(self, image):
        """檢測圖片中的白色矩形框"""
        try:
            # 轉換為OpenCV格式
            cv_image = self._convert_to_cv_format(image)
            gray = self._convert_to_grayscale(cv_image)
            
            # 1. 檢測白色區域
            white_mask = self._detect_white_regions(gray)
            
            # 2. 尋找輪廓
            contours = self._find_contours(white_mask)
            
            # 3. 過濾矩形輪廓
            rectangles = self._filter_rectangles(contours)
            
            # 4. 排序矩形（從左到右）
            sorted_rectangles = self._sort_rectangles(rectangles)
            
            return sorted_rectangles
            
        except Exception as e:
            print(f"矩形框檢測失敗: {e}")
            return []
    
    def _convert_to_cv_format(self, image):
        """轉換PIL圖片為OpenCV格式"""
        if hasattr(image, 'convert'):
            # PIL圖片
            return np.array(image.convert('RGB'))
        else:
            # 假設已經是numpy array
            return image
    
    def _convert_to_grayscale(self, cv_image):
        """轉換為灰度圖"""
        if len(cv_image.shape) == 3:
            return cv2.cvtColor(cv_image, cv2.COLOR_RGB2GRAY)
        else:
            return cv_image
    
    def _detect_white_regions(self, gray_image):
        """檢測白色區域"""
        # 白色閾值
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
    
    def _filter_rectangles(self, contours):
        """過濾出矩形輪廓"""
        rectangles = []
        
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
                        rectangles.append({
                            'bbox': (x, y, x+w, y+h),
                            'center': (x + w//2, y + h//2),
                            'area': area,
                            'aspect_ratio': aspect_ratio,
                            'fill_ratio': fill_ratio,
                            'contour': contour
                        })
        
        return rectangles
    
    def _sort_rectangles(self, rectangles):
        """按從左到右排序矩形"""
        return sorted(rectangles, key=lambda r: r['center'][0])
    
    def is_text_in_rectangle(self, text_bbox, rect_bbox):
        """檢查文字邊界框是否在矩形框內"""
        # 計算文字中心點
        if isinstance(text_bbox[0], (list, tuple)):
            # EasyOCR格式 [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            text_center_x = sum([point[0] for point in text_bbox]) / 4
            text_center_y = sum([point[1] for point in text_bbox]) / 4
        else:
            # 簡單邊界框格式 (x1, y1, x2, y2)
            text_center_x = (text_bbox[0] + text_bbox[2]) / 2
            text_center_y = (text_bbox[1] + text_bbox[3]) / 2
        
        # 檢查中心點是否在矩形框內（允許一定容錯）
        x1, y1, x2, y2 = rect_bbox
        tolerance = self.config["TEXT_ASSIGNMENT_TOLERANCE"]
        
        return (x1 - tolerance <= text_center_x <= x2 + tolerance and 
                y1 - tolerance <= text_center_y <= y2 + tolerance)


class RectangleDetectionDebugger:
    """矩形框檢測調試工具"""
    
    @staticmethod
    def visualize_rectangles(image, rectangles, ocr_results=None, output_path=None):
        """視覺化檢測到的矩形框"""
        # 創建可視化圖片
        if hasattr(image, 'copy'):
            vis_image = image.copy()
        else:
            vis_image = Image.fromarray(image)
            
        draw = ImageDraw.Draw(vis_image)
        
        # 顏色列表
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
        
        # 繪製矩形框
        for i, rectangle in enumerate(rectangles):
            bbox = rectangle['bbox']
            color = colors[i % len(colors)]
            
            # 繪製矩形框
            draw.rectangle(bbox, outline=color, width=2)
            
            # 標註序號和資訊
            info_text = f"段落{i+1}\nArea:{rectangle['area']:.0f}\nRatio:{rectangle['aspect_ratio']:.2f}"
            draw.text((bbox[0], bbox[1]-45), info_text, fill=color)
        
        # 繪製OCR文字框（如果提供）
        if ocr_results:
            for (text_bbox, text, confidence) in ocr_results:
                # 繪製文字邊界框
                if isinstance(text_bbox[0], (list, tuple)):
                    # EasyOCR格式
                    points = [(int(point[0]), int(point[1])) for point in text_bbox]
                    draw.polygon(points, outline='yellow', width=1)
                    
                    # 標註文字和信心度
                    text_info = f"{text[:10]}({confidence:.2f})"
                    draw.text((points[0][0], points[0][1]-15), text_info, fill='yellow')
        
        if output_path:
            vis_image.save(output_path)
        
        return vis_image
    
    @staticmethod
    def save_detection_report(image, rectangles, ocr_results, segments, output_dir):
        """保存檢測報告"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. 保存可視化圖片
        vis_image = RectangleDetectionDebugger.visualize_rectangles(
            image, rectangles, ocr_results)
        vis_path = os.path.join(output_dir, f"detection_visual_{timestamp}.png")
        vis_image.save(vis_path)
        
        # 2. 保存詳細報告
        # 轉換數據確保JSON序列化兼容性
        def convert_to_serializable(obj):
            """轉換numpy類型為Python原生類型"""
            if hasattr(obj, 'tolist'):
                return obj.tolist()
            elif isinstance(obj, (np.int32, np.int64, np.float32, np.float64)):
                return obj.item()
            elif isinstance(obj, (list, tuple)):
                return [convert_to_serializable(item) for item in obj]
            elif isinstance(obj, dict):
                return {key: convert_to_serializable(value) for key, value in obj.items()}
            else:
                return obj
        
        report = {
            'timestamp': timestamp,
            'detection_summary': {
                'rectangles_detected': len(rectangles),
                'ocr_texts_found': len(ocr_results) if ocr_results else 0,
                'segments_created': len(segments) if segments else 0,
                'has_rectangles': len(rectangles) > 0,
                'fallback_used': len(rectangles) == 0
            },
            'detection_parameters': {
                'white_threshold': 240,
                'min_rectangle_area': 100,
                'max_rectangle_area': 5000,
                'min_aspect_ratio': 0.2,
                'max_aspect_ratio': 10,
                'fill_ratio_threshold': 0.7
            },
            'rectangles': [
                {
                    'id': i,
                    'bbox': convert_to_serializable(rect['bbox']),
                    'center': convert_to_serializable(rect['center']),
                    'area': int(rect['area']),
                    'aspect_ratio': round(float(rect['aspect_ratio']), 3),
                    'fill_ratio': round(float(rect.get('fill_ratio', 0)), 3),
                    'width': int(rect['bbox'][2] - rect['bbox'][0]),
                    'height': int(rect['bbox'][3] - rect['bbox'][1]),
                    'position_type': RectangleDetectionDebugger._classify_position(rect['center'], image.size if hasattr(image, 'size') else (800, 600))
                }
                for i, rect in enumerate(rectangles)
            ],
            'ocr_results': [
                {
                    'id': i,
                    'text': str(text),
                    'confidence': round(float(confidence), 3),
                    'bbox': convert_to_serializable(bbox),
                    'center_x': float(RectangleDetectionDebugger._get_text_center_x(bbox)),
                    'assigned_to_rectangle': RectangleDetectionDebugger._find_text_assignment(bbox, rectangles)
                }
                for i, (bbox, text, confidence) in enumerate(ocr_results if ocr_results else [])
            ],
            'segments': [
                {
                    'segment_id': i,
                    'rectangle_info': convert_to_serializable(segment.get('rectangle_info', {})),
                    'texts_count': len(segment.get('individual_texts', [])),
                    'combined_text': str(segment.get('combined_text', '')),
                    'individual_texts': [
                        {
                            'text': str(text_item['text']),
                            'confidence': round(float(text_item['confidence']), 3),
                            'position': float(RectangleDetectionDebugger._get_text_center_x(text_item['bbox']))
                        }
                        for text_item in segment.get('individual_texts', [])
                    ]
                }
                for i, segment in enumerate(segments if segments else [])
            ],
            'analysis_result': {
                'method_used': 'rectangle_detection' if len(rectangles) > 0 else 'fallback_ocr',
                'success': True,
                'notes': []
            }
        }
        
        report_path = os.path.join(output_dir, f"detection_report_{timestamp}.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"檢測報告已保存:")
        print(f"  視覺化圖片: {vis_path}")
        print(f"  詳細報告: {report_path}")
        
        return vis_path, report_path
    
    @staticmethod
    def _classify_position(center, image_size):
        """分類矩形位置"""
        width, height = image_size
        x, y = center
        
        # 分為左、中、右三個區域
        if x < width * 0.33:
            return "left"
        elif x < width * 0.67:
            return "center"
        else:
            return "right"
    
    @staticmethod
    def _get_text_center_x(bbox):
        """獲取文字的中心X座標"""
        if isinstance(bbox[0], (list, tuple)):
            # EasyOCR格式 [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            return sum([point[0] for point in bbox]) / 4
        else:
            # 簡單邊界框格式 (x1, y1, x2, y2)
            return (bbox[0] + bbox[2]) / 2
    
    @staticmethod
    def _find_text_assignment(text_bbox, rectangles):
        """找出文字被分配到哪個矩形"""
        text_center_x = RectangleDetectionDebugger._get_text_center_x(text_bbox)
        
        for i, rect in enumerate(rectangles):
            x1, y1, x2, y2 = rect['bbox']
            if x1 <= text_center_x <= x2:
                return i
        return -1  # 未分配到任何矩形