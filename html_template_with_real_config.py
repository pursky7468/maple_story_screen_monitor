#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML模板生成器 - 真正的配置編輯功能
包含完整的增刪改查功能
"""

def get_enhanced_html_template():
    """獲取包含真實配置功能的HTML模板"""
    return """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MapleStory 交易監控系統</title>
    <style>
        body {{ font-family: 'Microsoft JhengHei', Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        
        /* 主標題 */
        .header {{ background: #2c3e50; color: white; padding: 15px; margin-bottom: 20px; border-radius: 8px; }}
        .header h2 {{ margin: 0; }}
        
        /* 配置面板樣式 */
        .config-panel {{ background: white; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); overflow: hidden; }}
        .config-header {{ background: #34495e; color: white; padding: 12px 15px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; user-select: none; }}
        .config-header:hover {{ background: #2c3e50; }}
        .config-toggle {{ font-size: 1.2em; transition: transform 0.3s; }}
        .config-toggle.rotated {{ transform: rotate(180deg); }}
        .config-content {{ padding: 20px; display: none; }}
        .config-content.show {{ display: block; }}
        
        /* 配置區域 */
        .config-section {{ margin-bottom: 25px; }}
        .config-section h4 {{ margin: 0 0 15px 0; color: #2c3e50; border-bottom: 2px solid #ecf0f1; padding-bottom: 5px; }}
        
        /* 物品網格 */
        .items-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; margin-bottom: 15px; }}
        .item-card {{ border: 1px solid #ddd; border-radius: 6px; padding: 15px; background: #f8f9fa; transition: border-color 0.3s; }}
        .item-card:hover {{ border-color: #3498db; }}
        .item-name {{ font-weight: bold; color: #2c3e50; margin-bottom: 8px; font-size: 1.1em; }}
        .item-keywords {{ font-size: 0.9em; color: #666; line-height: 1.4; margin-bottom: 10px; }}
        .item-actions {{ display: flex; gap: 8px; }}
        
        /* 按鈕樣式 */
        .btn {{ padding: 6px 12px; border: none; border-radius: 4px; cursor: pointer; font-size: 0.85em; transition: all 0.3s; }}
        .btn:hover {{ transform: translateY(-1px); box-shadow: 0 2px 4px rgba(0,0,0,0.2); }}
        .btn-primary {{ background: #3498db; color: white; }}
        .btn-success {{ background: #27ae60; color: white; }}
        .btn-warning {{ background: #f39c12; color: white; }}
        .btn-danger {{ background: #e74c3c; color: white; }}
        
        /* 添加物品表單 */
        .add-item-form {{ background: #e8f4fd; border: 1px dashed #3498db; border-radius: 6px; padding: 15px; margin-bottom: 15px; display: none; }}
        .form-row {{ display: flex; gap: 10px; margin-bottom: 10px; align-items: center; flex-wrap: wrap; }}
        .form-input {{ padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.9em; }}
        .form-input[name="itemName"] {{ min-width: 150px; }}
        .form-input[name="keywords"] {{ min-width: 200px; flex: 1; }}
        
        /* 編輯表單 */
        .edit-form {{ background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 4px; padding: 10px; margin-top: 10px; }}
        .edit-form input {{ width: 100%; margin-bottom: 8px; padding: 6px; border: 1px solid #ddd; border-radius: 4px; }}
        
        /* 統計卡片 */
        .stats {{ display: flex; gap: 15px; margin-bottom: 20px; }}
        .stat {{ background: white; padding: 15px; border-radius: 8px; text-align: center; flex: 1; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .stat-number {{ font-size: 1.5em; font-weight: bold; color: #e74c3c; }}
        
        /* 匹配結果 */
        .match-list {{ display: flex; flex-direction: column; gap: 15px; }}
        .match-card {{ background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #e74c3c; }}
        .match-header {{ background: #fff3cd; padding: 12px 15px; border-bottom: 1px solid #f39c12; }}
        .match-content {{ padding: 15px; }}
        .field-row {{ margin-bottom: 12px; }}
        .field-label {{ font-weight: bold; color: #2c3e50; min-width: 80px; display: inline-block; }}
        .field-value {{ color: #34495e; }}
        .player-name {{ color: #2980b9; font-weight: bold; }}
        .channel-name {{ color: #27ae60; font-weight: bold; }}
        .items-list {{ color: #e74c3c; font-weight: bold; }}
        .full-text {{ background: #ecf0f1; padding: 10px; border-radius: 4px; font-family: Consolas, monospace; font-size: 12px; line-height: 1.4; }}
        .screenshot {{ max-width: 200px; max-height: 100px; border: 1px solid #ddd; border-radius: 4px; cursor: pointer; float: right; margin-left: 15px; }}
        .timestamp {{ color: #7f8c8d; font-size: 0.9em; float: right; }}
        
        /* 提示訊息 */
        .alert {{ padding: 12px; border-radius: 4px; margin: 10px 0; }}
        .alert-success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .alert-warning {{ background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }}
        .alert-error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
        
        /* 載入中 */
        .loading {{ opacity: 0.6; pointer-events: none; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>🎮 MapleStory 交易監控系統</h2>
        <p>實時監控與配置管理界面</p>
    </div>
    
    <!-- 配置面板 -->
    <div class="config-panel">
        <div class="config-header" onclick="toggleConfigPanel()">
            <span>⚙️ 監控設定</span>
            <span class="config-toggle" id="configToggle">▼</span>
        </div>
        <div class="config-content" id="configContent">
            <div class="config-section">
                <h4>📋 當前監控物品</h4>
                <div id="currentItemsSection">
                    <!-- 動態生成物品清單 -->
                </div>
                
                <!-- 添加新物品表單 -->
                <div class="add-item-form" id="addItemForm">
                    <div class="form-row">
                        <input type="text" name="itemName" class="form-input" placeholder="物品名稱" maxlength="50">
                        <input type="text" name="keywords" class="form-input" placeholder="關鍵字 (用逗號分隔)" maxlength="200">
                        <button class="btn btn-success" onclick="saveNewItem()">✓ 保存</button>
                        <button class="btn btn-warning" onclick="cancelAddItem()">✗ 取消</button>
                    </div>
                </div>
                
                <button class="btn btn-primary" onclick="showAddItemForm()">+ 添加新物品</button>
                <button class="btn btn-success" onclick="reloadConfig()">🔄 重新載入配置</button>
            </div>
        </div>
    </div>
    
    <!-- 統計信息 -->
    <div class="stats">
        <div class="stat">
            <div class="stat-number">{total_tests}</div>
            <div>總測試數</div>
        </div>
        <div class="stat">
            <div class="stat-number">{matched_count}</div>
            <div>匹配交易</div>
        </div>
        <div class="stat">
            <div class="stat-number">{match_rate:.1f}%</div>
            <div>匹配率</div>
        </div>
    </div>
    
    <!-- 匹配結果列表 -->
    <div class="match-list">
        {match_cards}
    </div>
    
    <!-- 狀態提示區域 -->
    <div id="alertArea"></div>
    
    <script>
        let configPanelOpen = false;
        let currentConfig = {current_config};
        const API_BASE = 'http://localhost:8899';
        
        // 切換配置面板
        function toggleConfigPanel() {{
            configPanelOpen = !configPanelOpen;
            const content = document.getElementById('configContent');
            const toggle = document.getElementById('configToggle');
            
            if (configPanelOpen) {{
                content.classList.add('show');
                toggle.classList.add('rotated');
                loadCurrentItems();
            }} else {{
                content.classList.remove('show');
                toggle.classList.remove('rotated');
            }}
        }}
        
        // 載入當前物品配置
        async function loadCurrentItems() {{
            const container = document.getElementById('currentItemsSection');
            container.innerHTML = '<p style="text-align: center; color: #666;">載入中...</p>';
            
            try {{
                const response = await fetch(`${{API_BASE}}/api/items`);
                const result = await response.json();
                
                if (result.success) {{
                    currentConfig.SELLING_ITEMS = result.items;
                    renderItemsList(result.items);
                }} else {{
                    container.innerHTML = '<p style="color: #e74c3c; text-align: center;">載入配置失敗</p>';
                }}
            }} catch (error) {{
                console.error('載入配置失敗:', error);
                container.innerHTML = '<p style="color: #e74c3c; text-align: center;">無法連接到配置服務</p>';
            }}
        }}
        
        // 渲染物品清單
        function renderItemsList(items) {{
            const container = document.getElementById('currentItemsSection');
            container.innerHTML = '';
            
            if (!items || Object.keys(items).length === 0) {{
                container.innerHTML = '<p style="color: #666; text-align: center; padding: 20px;">尚未設定監控物品</p>';
                return;
            }}
            
            const itemsGrid = document.createElement('div');
            itemsGrid.className = 'items-grid';
            
            for (const [itemName, keywords] of Object.entries(items)) {{
                const itemCard = document.createElement('div');
                itemCard.className = 'item-card';
                itemCard.innerHTML = `
                    <div class="item-name">${{itemName}}</div>
                    <div class="item-keywords">關鍵字: ${{keywords.join(', ')}}</div>
                    <div class="item-actions">
                        <button class="btn btn-warning" onclick="editItem('${{itemName}}')">📝 編輯</button>
                        <button class="btn btn-danger" onclick="deleteItem('${{itemName}}')">🗑️ 刪除</button>
                    </div>
                    <div class="edit-form" id="editForm_${{itemName}}" style="display: none;">
                        <input type="text" value="${{keywords.join(', ')}}" id="editKeywords_${{itemName}}" placeholder="關鍵字 (用逗號分隔)">
                        <button class="btn btn-success" onclick="saveEdit('${{itemName}}')">✓ 保存</button>
                        <button class="btn btn-warning" onclick="cancelEdit('${{itemName}}')">✗ 取消</button>
                    </div>
                `;
                itemsGrid.appendChild(itemCard);
            }}
            
            container.appendChild(itemsGrid);
        }}
        
        // 顯示添加物品表單
        function showAddItemForm() {{
            document.getElementById('addItemForm').style.display = 'block';
            document.querySelector('input[name="itemName"]').focus();
        }}
        
        // 取消添加物品
        function cancelAddItem() {{
            document.getElementById('addItemForm').style.display = 'none';
            clearAddItemForm();
        }}
        
        // 清空添加物品表單
        function clearAddItemForm() {{
            document.querySelector('input[name="itemName"]').value = '';
            document.querySelector('input[name="keywords"]').value = '';
        }}
        
        // 保存新物品
        async function saveNewItem() {{
            const itemName = document.querySelector('input[name="itemName"]').value.trim();
            const keywordsText = document.querySelector('input[name="keywords"]').value.trim();
            
            if (!itemName) {{
                showAlert('請輸入物品名稱', 'error');
                return;
            }}
            
            if (!keywordsText) {{
                showAlert('請輸入關鍵字', 'error');
                return;
            }}
            
            const keywords = keywordsText.split(',').map(k => k.trim()).filter(k => k);
            if (keywords.length === 0) {{
                showAlert('請輸入有效的關鍵字', 'error');
                return;
            }}
            
            try {{
                const response = await fetch(`${{API_BASE}}/api/items/add`, {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{
                        itemName: itemName,
                        keywords: keywords
                    }})
                }});
                
                const result = await response.json();
                
                if (result.success) {{
                    showAlert(result.message, 'success');
                    cancelAddItem();
                    loadCurrentItems(); // 重新載入列表
                }} else {{
                    showAlert(result.error || '添加失敗', 'error');
                }}
            }} catch (error) {{
                console.error('添加物品失敗:', error);
                showAlert('無法連接到配置服務', 'error');
            }}
        }}
        
        // 編輯物品
        function editItem(itemName) {{
            const editForm = document.getElementById(`editForm_${{itemName}}`);
            editForm.style.display = 'block';
            document.getElementById(`editKeywords_${{itemName}}`).focus();
        }}
        
        // 取消編輯
        function cancelEdit(itemName) {{
            const editForm = document.getElementById(`editForm_${{itemName}}`);
            editForm.style.display = 'none';
        }}
        
        // 保存編輯
        async function saveEdit(itemName) {{
            const keywordsText = document.getElementById(`editKeywords_${{itemName}}`).value.trim();
            
            if (!keywordsText) {{
                showAlert('請輸入關鍵字', 'error');
                return;
            }}
            
            const keywords = keywordsText.split(',').map(k => k.trim()).filter(k => k);
            if (keywords.length === 0) {{
                showAlert('請輸入有效的關鍵字', 'error');
                return;
            }}
            
            try {{
                const response = await fetch(`${{API_BASE}}/api/items/update`, {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{
                        itemName: itemName,
                        keywords: keywords
                    }})
                }});
                
                const result = await response.json();
                
                if (result.success) {{
                    showAlert(result.message, 'success');
                    loadCurrentItems(); // 重新載入列表
                }} else {{
                    showAlert(result.error || '更新失敗', 'error');
                }}
            }} catch (error) {{
                console.error('更新物品失敗:', error);
                showAlert('無法連接到配置服務', 'error');
            }}
        }}
        
        // 刪除物品
        async function deleteItem(itemName) {{
            if (!confirm(`確定要刪除物品 "${{itemName}}" 嗎？`)) {{
                return;
            }}
            
            try {{
                const response = await fetch(`${{API_BASE}}/api/items/delete?itemName=${{encodeURIComponent(itemName)}}`, {{
                    method: 'DELETE'
                }});
                
                const result = await response.json();
                
                if (result.success) {{
                    showAlert(result.message, 'success');
                    loadCurrentItems(); // 重新載入列表
                }} else {{
                    showAlert(result.error || '刪除失敗', 'error');
                }}
            }} catch (error) {{
                console.error('刪除物品失敗:', error);
                showAlert('無法連接到配置服務', 'error');
            }}
        }}
        
        // 重新載入配置
        async function reloadConfig() {{
            loadCurrentItems();
            showAlert('配置已重新載入', 'success');
        }}
        
        // 顯示提示訊息
        function showAlert(message, type = 'success') {{
            const alertArea = document.getElementById('alertArea');
            const alert = document.createElement('div');
            alert.className = `alert alert-${{type}}`;
            alert.textContent = message;
            
            alertArea.appendChild(alert);
            
            setTimeout(() => {{
                alert.remove();
            }}, 3000);
        }}
        
        // 點擊圖片放大功能
        document.querySelectorAll('.screenshot').forEach(img => {{
            img.onclick = function() {{
                const modal = document.createElement('div');
                modal.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);z-index:1000;display:flex;justify-content:center;align-items:center;cursor:pointer;';
                const bigImg = document.createElement('img');
                bigImg.src = this.src;
                bigImg.style.cssText = 'max-width:90%;max-height:90%;';
                modal.appendChild(bigImg);
                modal.onclick = () => document.body.removeChild(modal);
                document.body.appendChild(modal);
            }};
        }});
        
        // 頁面載入完成
        window.onload = function() {{
            console.log("MapleStory 交易監控系統界面已載入");
            
            // 檢查API服務是否可用
            fetch(`${{API_BASE}}/api/config`)
                .then(() => {{
                    console.log("✅ 配置API服務可用");
                }})
                .catch(() => {{
                    showAlert('警告：配置API服務未啟動，配置編輯功能將不可用', 'warning');
                }});
        }};
        
        // 自動刷新功能 (配置面板開啟時不刷新)
        setTimeout(() => {{
            if (!configPanelOpen) {{
                location.reload();
            }}
        }}, {refresh_interval} * 1000);
    </script>
</body>
</html>"""

def get_current_config():
    """獲取當前配置"""
    try:
        from config import SELLING_ITEMS, SCAN_INTERVAL
        return {
            "SELLING_ITEMS": SELLING_ITEMS,
            "SCAN_INTERVAL": SCAN_INTERVAL
        }
    except ImportError:
        return {
            "SELLING_ITEMS": {},
            "SCAN_INTERVAL": 2
        }