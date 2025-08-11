#!/usr/bin/env python3
"""
診斷OCR文字識別覆蓋範圍的工具
分析為什麼OCR沒有識別到完整的文字內容
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import json
import numpy as np

def analyze_specific_image(image_path):
    """分析特定圖片的OCR識別問題"""
    print(f"=== 分析圖片: {os.path.basename(image_path)} ===")
    
    if not os.path.exists(image_path):
        print("[ERROR] 圖片不存在")
        return
    
    # 載入圖片
    image = Image.open(image_path)
    print(f"[INFO] 圖片尺寸: {image.size}")
    print(f"[INFO] 圖片模式: {image.mode}")
    
    # 顯示圖片的基本資訊
    img_array = np.array(image)
    print(f"[INFO] 圖片陣列形狀: {img_array.shape}")
    
    # 分析顏色分佈
    if len(img_array.shape) == 3:
        # RGB圖片
        avg_color = img_array.mean(axis=(0,1))
        print(f"[INFO] 平均顏色值: R={avg_color[0]:.1f}, G={avg_color[1]:.1f}, B={avg_color[2]:.1f}")
    else:
        # 灰階圖片
        avg_color = img_array.mean()
        print(f"[INFO] 平均灰階值: {avg_color:.1f}")
    
    # 嘗試OCR識別
    try:
        import easyocr
        reader = easyocr.Reader(['ch_tra', 'en'], verbose=False)
        
        # 進行OCR識別
        results = reader.readtext(np.array(image))
        
        print(f"\n[OCR結果] 識別到 {len(results)} 個文字區域:")
        total_text = ""
        for i, (bbox, text, confidence) in enumerate(results):
            print(f"  {i+1}. 文字: '{text}'")
            print(f"      信心度: {confidence:.3f}")
            print(f"      位置: {bbox}")
            print(f"      左上角: ({bbox[0][0]:.0f}, {bbox[0][1]:.0f})")
            print(f"      右下角: ({bbox[2][0]:.0f}, {bbox[2][1]:.0f})")
            print(f"      寬度: {bbox[2][0] - bbox[0][0]:.0f}, 高度: {bbox[2][1] - bbox[0][1]:.0f}")
            total_text += text + " "
            print()
        
        print(f"[合併文字] '{total_text.strip()}'")
        
        # 檢查是否有遺漏的區域
        if len(results) > 0:
            # 找到最左邊的識別區域
            leftmost_x = min(bbox[0][0] for bbox, _, _ in results)
            rightmost_x = max(bbox[2][0] for bbox, _, _ in results)
            
            print(f"\n[覆蓋範圍分析]")
            print(f"  圖片寬度: {image.size[0]} 像素")
            print(f"  OCR最左邊: {leftmost_x:.0f} 像素")
            print(f"  OCR最右邊: {rightmost_x:.0f} 像素") 
            print(f"  左邊未識別區域: 0 ~ {leftmost_x:.0f} ({leftmost_x/image.size[0]*100:.1f}%)")
            print(f"  右邊未識別區域: {rightmost_x:.0f} ~ {image.size[0]} ({(image.size[0]-rightmost_x)/image.size[0]*100:.1f}%)")
        
        # 嘗試不同的預處理方法
        print(f"\n[預處理測試]")
        test_preprocessing_methods(image, reader)
        
        # 生成標註圖片
        create_annotated_image(image, results, image_path)
        
        return results
        
    except ImportError:
        print("[ERROR] EasyOCR未安裝")
        return None
    except Exception as e:
        print(f"[ERROR] OCR分析失敗: {e}")
        return None

def test_preprocessing_methods(image, reader):
    """測試不同的預處理方法"""
    methods = {
        "原圖": image,
        "灰階": image.convert('L'),
        "高對比": ImageEnhance.Contrast(image.convert('L')).enhance(2.5),
        "銳化": ImageEnhance.Sharpness(image.convert('L')).enhance(2.0),
        "組合增強": None
    }
    
    # 組合增強
    combined = image.convert('L')
    combined = ImageEnhance.Contrast(combined).enhance(2.0)
    combined = ImageEnhance.Sharpness(combined).enhance(1.5)
    methods["組合增強"] = combined
    
    for method_name, processed_image in methods.items():
        if processed_image is None:
            continue
            
        try:
            results = reader.readtext(np.array(processed_image))
            total_coverage = 0
            leftmost = float('inf')
            
            if results:
                leftmost = min(bbox[0][0] for bbox, _, _ in results)
                total_coverage = sum(len(text) for _, text, _ in results)
            
            print(f"  {method_name}: {len(results)}個區域, 最左{leftmost:.0f}px, 總字數{total_coverage}")
            
            # 如果有改進，顯示詳細內容
            if len(results) > 1 or leftmost < 100:
                combined_text = ' '.join([text for _, text, _ in results])
                print(f"    內容: '{combined_text}'")
                
        except Exception as e:
            print(f"  {method_name}: 處理失敗 - {e}")

def create_annotated_image(image, ocr_results, original_path):
    """創建標註了OCR識別區域的圖片"""
    try:
        # 複製圖片
        annotated = image.copy()
        draw = ImageDraw.Draw(annotated)
        
        # 嘗試載入字體
        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except:
            font = ImageFont.load_default()
        
        # 標註每個識別區域
        colors = ['red', 'blue', 'green', 'orange', 'purple']
        for i, (bbox, text, confidence) in enumerate(ocr_results):
            color = colors[i % len(colors)]
            
            # 繪製邊框
            points = [(int(p[0]), int(p[1])) for p in bbox]
            draw.polygon(points, outline=color, width=2)
            
            # 標註文字和信心度
            label = f"{i+1}: {confidence:.2f}"
            draw.text((int(bbox[0][0]), int(bbox[0][1])-15), label, fill=color, font=font)
        
        # 保存標註圖片
        annotated_path = original_path.replace('.png', '_annotated.png')
        annotated.save(annotated_path)
        print(f"[INFO] 標註圖片已保存: {annotated_path}")
        
    except Exception as e:
        print(f"[WARNING] 無法創建標註圖片: {e}")

def analyze_monitoring_session():
    """分析監控會話的OCR問題"""
    session_folder = r"C:\Users\User\Desktop\螢幕監控程式\monitoring_session_20250810_085346"
    
    if not os.path.exists(session_folder):
        print("[ERROR] 監控會話資料夾不存在")
        return
    
    print(f"分析監控會話: {os.path.basename(session_folder)}")
    
    # 分析第一個截圖
    target_image = os.path.join(session_folder, "monitor_001_20250810_085346_670.png")
    if os.path.exists(target_image):
        results = analyze_specific_image(target_image)
        
        # 對比分析結果檔案
        analysis_file = os.path.join(session_folder, "analysis_20250810_085347_533.json")
        if os.path.exists(analysis_file):
            print(f"\n[對比分析檔案]")
            with open(analysis_file, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
            
            recorded_text = analysis_data['result']['full_text']
            recorded_player = analysis_data['result']['player_name']
            raw_ocr = analysis_data.get('raw_response', [])
            
            print(f"  檔案記錄的完整文字: '{recorded_text}'")
            print(f"  檔案記錄的玩家名稱: '{recorded_player}'")
            print(f"  原始OCR結果數量: {len(raw_ocr)}")
            
            # 對比實時OCR結果
            if results:
                live_text = ' '.join([text for _, text, _ in results])
                print(f"  實時OCR完整文字: '{live_text}'")
                print(f"  結果是否一致: {'是' if live_text.strip() == recorded_text.strip() else '否'}")
    
    print(f"\n[問題總結]")
    print("1. OCR沒有識別到圖片左側的玩家名稱 '乂煞氣a澤神乂'")
    print("2. OCR沒有識別到頻道號碼 'CH2245'")
    print("3. 只識別到從 '收' 字開始的後半段內容")
    print("4. 可能原因:")
    print("   - 左側文字顏色對比度不足")
    print("   - 字體或大小不符合OCR模型訓練數據")
    print("   - 特殊字符識別困難")
    print("   - 需要調整預處理參數")

if __name__ == "__main__":
    analyze_monitoring_session()