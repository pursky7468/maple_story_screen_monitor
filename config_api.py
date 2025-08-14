#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理API
提供HTTP API接口來管理config.py配置
"""

import os
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import re


class ConfigManager:
    """配置文件管理器"""
    
    def __init__(self, config_file='config.py'):
        self.config_file = config_file
        self.config_lock = threading.Lock()
    
    def get_config(self):
        """獲取當前配置"""
        try:
            # 動態導入config模組
            import importlib
            import config
            importlib.reload(config)  # 重新載入以獲取最新配置
            
            return {
                'SELLING_ITEMS': config.SELLING_ITEMS,
                'INACTIVE_ITEMS': getattr(config, 'INACTIVE_ITEMS', {}),
                'SCAN_INTERVAL': config.SCAN_INTERVAL,
                'GEMINI_API_KEY': config.GEMINI_API_KEY[:10] + '...' if len(config.GEMINI_API_KEY) > 10 else config.GEMINI_API_KEY
            }
        except Exception as e:
            print(f"獲取配置失敗: {e}")
            return {'SELLING_ITEMS': {}, 'INACTIVE_ITEMS': {}, 'SCAN_INTERVAL': 2, 'GEMINI_API_KEY': ''}
    
    def update_config_section(self, section_name, items_dict):
        """更新配置文件中的指定區域"""
        with self.config_lock:
            try:
                # 讀取當前config.py文件
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 構造新的字典字符串
                items_str = f"{section_name} = {{\n"
                for item_name, keywords in items_dict.items():
                    # 轉義引號和特殊字符
                    safe_item_name = item_name.replace('"', '\\"')
                    safe_keywords = [kw.replace('"', '\\"') for kw in keywords]
                    keywords_str = ', '.join([f'"{kw}"' for kw in safe_keywords])
                    items_str += f'    "{safe_item_name}": [{keywords_str}],\n'
                items_str += "}"
                
                # 使用正則表達式替換指定區域
                pattern = rf'{section_name}\s*=\s*\{{[^}}]*\}}'
                new_content = re.sub(pattern, items_str, content, flags=re.DOTALL)
                
                # 如果沒有找到該區域，則添加到文件末尾
                if new_content == content:
                    new_content += f"\n\n{items_str}\n"
                
                # 寫入新內容
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"[OK] {section_name}配置已保存到 {self.config_file}")
                return True
                
            except Exception as e:
                print(f"[ERROR] 保存{section_name}配置失敗: {e}")
                return False
    
    def update_selling_items(self, selling_items):
        """更新SELLING_ITEMS配置"""
        return self.update_config_section('SELLING_ITEMS', selling_items)
    
    def update_inactive_items(self, inactive_items):
        """更新INACTIVE_ITEMS配置"""
        return self.update_config_section('INACTIVE_ITEMS', inactive_items)
    
    def add_item(self, item_name, keywords):
        """添加新的監控物品"""
        current_config = self.get_config()
        selling_items = current_config.get('SELLING_ITEMS', {})
        selling_items[item_name] = keywords
        return self.update_selling_items(selling_items)
    
    def remove_item(self, item_name):
        """刪除監控物品"""
        current_config = self.get_config()
        selling_items = current_config.get('SELLING_ITEMS', {})
        inactive_items = current_config.get('INACTIVE_ITEMS', {})
        
        removed = False
        if item_name in selling_items:
            del selling_items[item_name]
            self.update_selling_items(selling_items)
            removed = True
        if item_name in inactive_items:
            del inactive_items[item_name]
            self.update_inactive_items(inactive_items)
            removed = True
        
        return removed
    
    def update_item(self, item_name, keywords):
        """更新物品關鍵字"""
        current_config = self.get_config()
        selling_items = current_config.get('SELLING_ITEMS', {})
        inactive_items = current_config.get('INACTIVE_ITEMS', {})
        
        if item_name in selling_items:
            selling_items[item_name] = keywords
            return self.update_selling_items(selling_items)
        elif item_name in inactive_items:
            inactive_items[item_name] = keywords
            return self.update_inactive_items(inactive_items)
        
        return False
    
    def pause_item(self, item_name):
        """暫停物品監控 - 從SELLING_ITEMS移到INACTIVE_ITEMS"""
        current_config = self.get_config()
        selling_items = current_config.get('SELLING_ITEMS', {})
        inactive_items = current_config.get('INACTIVE_ITEMS', {})
        
        if item_name in selling_items:
            # 移動物品到暫停區域
            inactive_items[item_name] = selling_items[item_name]
            del selling_items[item_name]
            
            # 更新兩個區域
            success1 = self.update_selling_items(selling_items)
            success2 = self.update_inactive_items(inactive_items)
            
            return success1 and success2
        
        return False
    
    def resume_item(self, item_name):
        """恢復物品監控 - 從INACTIVE_ITEMS移到SELLING_ITEMS"""
        current_config = self.get_config()
        selling_items = current_config.get('SELLING_ITEMS', {})
        inactive_items = current_config.get('INACTIVE_ITEMS', {})
        
        if item_name in inactive_items:
            # 移動物品到活躍區域
            selling_items[item_name] = inactive_items[item_name]
            del inactive_items[item_name]
            
            # 更新兩個區域
            success1 = self.update_selling_items(selling_items)
            success2 = self.update_inactive_items(inactive_items)
            
            return success1 and success2
        
        return False


class ConfigAPIHandler(BaseHTTPRequestHandler):
    """配置API請求處理器"""
    
    config_manager = ConfigManager()
    
    def _send_json_response(self, data, status_code=200):
        """發送JSON響應"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(json_str.encode('utf-8'))
    
    def _send_error_response(self, message, status_code=400):
        """發送錯誤響應"""
        self._send_json_response({'error': message, 'success': False}, status_code)
    
    def do_OPTIONS(self):
        """處理CORS預檢請求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """處理GET請求"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/config':
            # 獲取當前配置
            config = self.config_manager.get_config()
            self._send_json_response({'config': config, 'success': True})
            
        elif parsed_path.path == '/api/items':
            # 獲取監控物品列表
            config = self.config_manager.get_config()
            items = config.get('SELLING_ITEMS', {})
            self._send_json_response({'items': items, 'success': True})
            
        else:
            self._send_error_response('Not Found', 404)
    
    def do_POST(self):
        """處理POST請求"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            parsed_path = urlparse(self.path)
            
            if parsed_path.path == '/api/items/add':
                # 添加新物品
                item_name = data.get('itemName', '').strip()
                keywords = data.get('keywords', [])
                
                if not item_name:
                    self._send_error_response('物品名稱不能為空')
                    return
                
                if not keywords:
                    self._send_error_response('關鍵字不能為空')
                    return
                
                success = self.config_manager.add_item(item_name, keywords)
                if success:
                    self._send_json_response({
                        'message': f'物品 "{item_name}" 已添加',
                        'success': True
                    })
                else:
                    self._send_error_response('添加物品失敗')
            
            elif parsed_path.path == '/api/items/update':
                # 更新物品
                item_name = data.get('itemName', '').strip()
                keywords = data.get('keywords', [])
                
                if not item_name:
                    self._send_error_response('物品名稱不能為空')
                    return
                
                success = self.config_manager.update_item(item_name, keywords)
                if success:
                    self._send_json_response({
                        'message': f'物品 "{item_name}" 已更新',
                        'success': True
                    })
                else:
                    self._send_error_response('更新物品失敗')
                    
            elif parsed_path.path == '/api/items/pause':
                # 暫停物品監控
                item_name = data.get('itemName', '').strip()
                
                if not item_name:
                    self._send_error_response('物品名稱不能為空')
                    return
                
                success = self.config_manager.pause_item(item_name)
                if success:
                    self._send_json_response({
                        'message': f'物品 "{item_name}" 已暫停監控',
                        'success': True
                    })
                else:
                    self._send_error_response('暫停監控失敗')
                    
            elif parsed_path.path == '/api/items/resume':
                # 恢復物品監控
                item_name = data.get('itemName', '').strip()
                
                if not item_name:
                    self._send_error_response('物品名稱不能為空')
                    return
                
                success = self.config_manager.resume_item(item_name)
                if success:
                    self._send_json_response({
                        'message': f'物品 "{item_name}" 已恢復監控',
                        'success': True
                    })
                else:
                    self._send_error_response('恢復監控失敗')
            
            else:
                self._send_error_response('Not Found', 404)
                
        except Exception as e:
            print(f"處理POST請求失敗: {e}")
            self._send_error_response(f'請求處理失敗: {str(e)}')
    
    def do_DELETE(self):
        """處理DELETE請求"""
        try:
            parsed_path = urlparse(self.path)
            query_params = parse_qs(parsed_path.query)
            
            if parsed_path.path == '/api/items/delete':
                item_name = query_params.get('itemName', [None])[0]
                
                if not item_name:
                    self._send_error_response('物品名稱不能為空')
                    return
                
                success = self.config_manager.remove_item(item_name)
                if success:
                    self._send_json_response({
                        'message': f'物品 "{item_name}" 已刪除',
                        'success': True
                    })
                else:
                    self._send_error_response('刪除物品失敗')
            
            else:
                self._send_error_response('Not Found', 404)
                
        except Exception as e:
            print(f"處理DELETE請求失敗: {e}")
            self._send_error_response(f'請求處理失敗: {str(e)}')
    
    def log_message(self, format, *args):
        """靜默日誌"""
        pass


def start_config_api_server(port=8899):
    """啟動配置API服務器"""
    try:
        server = HTTPServer(('localhost', port), ConfigAPIHandler)
        print(f"[INFO] 配置API服務器已啟動: http://localhost:{port}")
        print("API端點:")
        print(f"   GET  http://localhost:{port}/api/config")
        print(f"   GET  http://localhost:{port}/api/items")
        print(f"   POST http://localhost:{port}/api/items/add")
        print(f"   POST http://localhost:{port}/api/items/update")
        print(f"   POST http://localhost:{port}/api/items/pause")
        print(f"   POST http://localhost:{port}/api/items/resume")
        print(f"   DELETE http://localhost:{port}/api/items/delete")
        
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] 配置API服務器已停止")
    except Exception as e:
        print(f"[ERROR] 啟動配置API服務器失敗: {e}")


if __name__ == '__main__':
    start_config_api_server()