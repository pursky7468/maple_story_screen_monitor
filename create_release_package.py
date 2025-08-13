#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
創建客戶發布包腳本
自動打包所有必要文件供客戶使用
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def create_release_package():
    """創建發布包"""
    
    # 發布包名稱
    timestamp = datetime.now().strftime("%Y%m%d")
    package_name = f"MapleStory_TradeMonitor_v1.0_{timestamp}"
    
    # 創建發布目錄
    release_dir = Path(package_name)
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()
    
    # 核心文件列表
    core_files = [
        "screen_monitor.py",
        "ocr_rectangle_analyzer.py", 
        "real_time_merger.py",
        "roi_selector.py",
        "text_analyzer.py",
        "gemini_analyzer.py",
        "ocr_analyzer.py",
        "config.py",
        "install_ocr.py"
    ]
    
    # 安裝文件列表  
    install_files = [
        "install.bat",
        "setup.py",
        "requirements.txt"
    ]
    
    # 文檔文件列表
    doc_files = [
        "USER_MANUAL.md",
        "RELEASE_NOTES.md", 
        "README.md",
        "CLAUDE.md",
        "DEVELOPER_HANDOVER.md",
        "PROJECT_SUMMARY.md"
    ]
    
    print(f"開始創建發布包: {package_name}")
    print("=" * 50)
    
    # 複製核心文件
    core_dir = release_dir / "core"
    core_dir.mkdir()
    
    print("複製核心程式文件...")
    for file in core_files:
        if Path(file).exists():
            shutil.copy2(file, core_dir / file)
            print(f"   OK: {file}")
        else:
            print(f"   WARN: 找不到文件 {file}")
    
    # 複製安裝文件
    print("\n複製安裝文件...")
    for file in install_files:
        if Path(file).exists():
            shutil.copy2(file, release_dir / file)
            print(f"   OK: {file}")
        else:
            print(f"   WARN: 找不到文件 {file}")
    
    # 複製文檔文件  
    docs_dir = release_dir / "docs"
    docs_dir.mkdir()
    
    print("\n複製文檔文件...")
    for file in doc_files:
        if Path(file).exists():
            shutil.copy2(file, docs_dir / file)
            print(f"   OK: {file}")
        else:
            print(f"   WARN: 找不到文件 {file}")
    
    # 創建 generated_files 目錄（空目錄，安裝時生成）
    generated_dir = release_dir / "generated_files"
    generated_dir.mkdir()
    
    # 創建說明文件
    readme_content = """# Generated Files 目錄

此目錄在安裝完成後會包含：

- config_user.py      # 用戶配置文件（可編輯）
- 啟動監控.bat        # 快速啟動腳本

請勿刪除此目錄。
"""
    
    with open(generated_dir / "README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    # 創建快速開始指南
    quick_start = """# 快速開始指南

## 1. 安裝系統
雙擊執行 install.bat，等待安裝完成（約5-10分鐘）

## 2. 設置監控物品  
編輯 generated_files/config_user.py，添加您要出售的物品：

```python
SELLING_ITEMS = {
    "披風幸運60%": ["披風幸運60%", "披風幸60%", "披幸60"],
    "母礦": ["母礦", "青銅母礦", "鋼鐵母礦"],
    # 添加更多物品...
}
```

## 3. 開始監控
雙擊執行 generated_files/啟動監控.bat

## 4. 選擇監控區域
- 程式啟動後會提示選擇ROI區域
- 用滑鼠框選遊戲的聊天視窗
- 確保包含完整的交易廣播訊息

## 5. 享受自動監控！
- 程式會自動偵測交易機會
- 找到匹配時會彈出提示窗
- 所有結果會保存為HTML報告

## 詳細說明
請參考 docs/USER_MANUAL.md 獲取完整使用指南。

祝您遊戲愉快！
"""
    
    with open(release_dir / "快速開始.md", "w", encoding="utf-8") as f:
        f.write(quick_start)
    
    print("\n創建額外文件...")
    print("   OK: 快速開始.md")
    print("   OK: generated_files/README.txt")
    
    # 創建ZIP壓縮包
    zip_name = f"{package_name}.zip"
    print(f"\n創建ZIP壓縮包: {zip_name}")
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(release_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, release_dir.parent)
                zipf.write(file_path, arc_path)
    
    # 顯示統計信息
    total_files = sum([len(files) for r, d, files in os.walk(release_dir)])
    zip_size = os.path.getsize(zip_name) / 1024 / 1024  # MB
    
    print("\n" + "=" * 50)
    print("發布包創建完成！")
    print("=" * 50)
    print(f"發布目錄: {release_dir}")
    print(f"壓縮包: {zip_name}")
    print(f"包含文件: {total_files} 個")
    print(f"壓縮包大小: {zip_size:.1f} MB")
    print("=" * 50)
    print()
    print("交付清單:")
    print(f"   - {zip_name}")
    print("   - 包含完整安裝程式")
    print("   - 包含用戶手冊")
    print("   - 一鍵安裝部署")
    print("   - 即開即用")
    print()
    print("客戶使用步驟:")
    print("   1. 解壓縮ZIP文件")
    print("   2. 執行 install.bat 安裝")
    print("   3. 編輯配置文件設置監控物品")
    print("   4. 執行 啟動監控.bat 開始使用")
    print()
    print("發布包準備就緒，可交付客戶使用！")

if __name__ == "__main__":
    create_release_package()