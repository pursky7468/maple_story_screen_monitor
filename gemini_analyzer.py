import google.generativeai as genai
import json
import io
from text_analyzer import TextAnalyzer, AnalysisResult

class GeminiAnalyzer(TextAnalyzer):
    """使用Gemini API的文字分析器"""
    
    def __init__(self, api_key: str, selling_items: dict):
        super().__init__(selling_items)
        self.strategy_type = "GEMINI"
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    def analyze_image(self, image) -> str:
        """使用Gemini分析圖片"""
        try:
            # 將PIL圖片轉換為bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # 生成商品清單文字
            selling_list = '\n'.join([f"- {item_name}: {', '.join(keywords)}" 
                                    for item_name, keywords in self.selling_items.items()])
            
            prompt = f"""
            你是一位楓之谷遊戲中的商人，
            你手中有以下商品要賣出：
            {selling_list}
            
            請分析這張圖片中的所有文字內容，並檢查是否有玩家在收購你手中的任何商品。
            請以JSON格式回傳分析結果，格式如下：
            {{
                "full_text": "圖片中的完整文字內容",
                "is_match": true/false,
                "player_name": "玩家名稱（如果有匹配的話）",
                "channel_number": "頻道編號（通常在文字開頭）",
                "matched_items": [
                    {{
                        "item_name": "商品名稱",
                        "keywords_found": ["找到的相關關鍵字"]
                    }}
                ],
                "matched_keywords": ["所有找到的關鍵字"]
            }}
            
            注意事項：
            - full_text 必須包含圖片中所有識別到的文字
            - is_match 判斷是否有人在收購你手中的任何商品
            - player_name 提取說話者的玩家名稱
            - channel_number 提取頻道編號（通常格式如 [頻道1] 或 ch1 等）
            - matched_items 列出匹配的商品及其找到的關鍵字
            - matched_keywords 列出所有找到的相關關鍵字
            - 你必須嚴格確認百分比的數字內容，例如如果你要賣的東西是披風幸運60%，但玩家是要收購披風幸運10%，這是不成立匹配。
            
            請確保回傳的是有效的JSON格式，不要包含任何其他文字。
            """
            
            # 使用新的API格式
            response = self.model.generate_content([
                prompt,
                {
                    "mime_type": "image/png",
                    "data": img_byte_arr
                }
            ])
            return response.text.strip()
            
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def extract_json_from_response(self, response_text: str) -> str:
        """從回應中提取JSON內容"""
        # 移除可能的markdown代碼塊標記
        response_text = response_text.strip()
        
        # 檢查是否有```json代碼塊
        if response_text.startswith('```json'):
            # 找到開始和結束位置
            start_marker = '```json'
            end_marker = '```'
            
            start_idx = response_text.find(start_marker) + len(start_marker)
            end_idx = response_text.rfind(end_marker)
            
            if start_idx > len(start_marker) - 1 and end_idx > start_idx:
                json_content = response_text[start_idx:end_idx].strip()
            else:
                # 如果沒找到結束標記，取開始標記之後的所有內容
                json_content = response_text[start_idx:].strip()
        elif response_text.startswith('```'):
            # 處理其他類型的代碼塊
            lines = response_text.split('\n')
            json_lines = []
            in_code_block = False
            
            for line in lines:
                if line.strip().startswith('```') and not in_code_block:
                    in_code_block = True
                elif line.strip() == '```' and in_code_block:
                    break
                elif in_code_block:
                    json_lines.append(line)
            
            json_content = '\n'.join(json_lines).strip()
        else:
            # 沒有代碼塊，直接使用原始內容
            json_content = response_text
        
        # 嘗試找到JSON對象的開始和結束
        json_start = json_content.find('{')
        json_end = json_content.rfind('}')
        
        if json_start >= 0 and json_end > json_start:
            json_content = json_content[json_start:json_end + 1]
        
        return json_content
    
    def parse_result(self, raw_result: str) -> AnalysisResult:
        """解析Gemini的JSON回應"""
        if raw_result.startswith("ERROR"):
            return AnalysisResult(
                full_text=raw_result,
                is_match=False,
                analysis_method="Gemini",
                confidence=0.0
            )
        
        try:
            # 提取JSON內容
            json_content = self.extract_json_from_response(raw_result)
            result_data = json.loads(json_content)
            
            return AnalysisResult(
                full_text=result_data.get("full_text", ""),
                is_match=result_data.get("is_match", False),
                player_name=result_data.get("player_name", "未知"),
                channel_number=result_data.get("channel_number", "未知"),
                matched_items=result_data.get("matched_items", []),
                matched_keywords=result_data.get("matched_keywords", []),
                confidence=1.0 if result_data.get("is_match", False) else 0.0,
                analysis_method="Gemini"
            )
            
        except json.JSONDecodeError as e:
            # JSON解析失敗，返回錯誤結果
            return AnalysisResult(
                full_text=f"JSON解析錯誤: {str(e)}",
                is_match=False,
                analysis_method="Gemini",
                confidence=0.0
            )
    
    def get_error_type(self, error_message: str) -> str:
        """Gemini策略的錯誤類型"""
        if self.is_quota_error(error_message):
            return "API_QUOTA_EXCEEDED"
        elif "429" in error_message:
            return "API_RATE_LIMITED"
        else:
            return "LLM_ERROR"
    
    def is_quota_error(self, error_message: str) -> bool:
        """檢查是否為Gemini API配額錯誤"""
        error_lower = error_message.lower()
        return "quota" in error_lower or "429" in error_message