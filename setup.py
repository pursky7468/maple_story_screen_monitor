#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MapleStory 交易機會監控系統安裝程式
自動化安裝所有依賴和設置環境
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """檢查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ 錯誤：需要 Python 3.8 或更高版本")
        print(f"   當前版本：Python {version.major}.{version.minor}.{version.micro}")
        print("   請從 https://www.python.org/downloads/ 下載並安裝最新版本")
        return False
    
    print(f"✅ Python 版本檢查通過：{version.major}.{version.minor}.{version.micro}")
    return True

def install_requirements():
    """安裝Python依賴"""
    print("\n📦 開始安裝Python依賴包...")
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    if not requirements_file.exists():
        print("❌ 找不到 requirements.txt 文件")
        return False
    
    try:
        # 升級pip
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        print("✅ pip 已升級到最新版本")
        
        # 安裝依賴
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)], 
                      check=True, capture_output=True)
        print("✅ 所有Python依賴包安裝完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 安裝依賴失敗：{e}")
        print("   請檢查網路連接或手動執行：pip install -r requirements.txt")
        return False

def setup_ocr():
    """設置OCR語言模型"""
    print("\n🔤 開始設置OCR語言模型...")
    
    try:
        # 檢查EasyOCR是否可用
        import easyocr
        
        # 初始化OCR（這會自動下載語言模型）
        print("   正在下載繁體中文語言模型（約100MB）...")
        reader = easyocr.Reader(['ch_tra', 'en'], verbose=False)
        print("✅ OCR語言模型設置完成")
        return True
        
    except ImportError:
        print("❌ EasyOCR未正確安裝")
        return False
    except Exception as e:
        print(f"❌ OCR設置失敗：{e}")
        return False

def create_config():
    """創建用戶配置文件"""
    print("\n⚙️  創建用戶配置文件...")
    
    config_template = '''# MapleStory 交易機會監控系統配置文件
# 請根據您的需求修改以下設置

# Gemini AI API密鑰（可選，用於高精度分析）
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"

# ROI座標將在程式啟動時由使用者選擇
ROI_COORDINATES = None

# 監控商品設置 - 添加您想要出售的物品
SELLING_ITEMS = {
    "披風幸運60%": ["披風幸運60%", "披風幸運60%卷軸", "披風幸60%", "披風幸運60", "披幸60"],
    "母礦": ["母礦", "青銅母礦", "鋼鐵母礦", "紫礦石母礦", "鋰礦石母礦"],
    "耳環智力10%": ["耳環智力10%", "耳智10", "耳環智力10"],
    "耳環智力60%": ["耳環智力60%", "耳智60", "耳環智力60"],
    # 在此添加更多您想要監控的物品...
    # "物品名稱": ["關鍵字1", "關鍵字2", "縮寫"],
}

# 掃描間隔（秒）
SCAN_INTERVAL = 2

# 截圖保存設定
SAVE_SCREENSHOTS = False  # 是否保存截圖

# Rectangle detection parameters for OCR_Rectangle analyzer
RECTANGLE_DETECTION_CONFIG = {
    "WHITE_THRESHOLD": 245,              # White detection threshold
    "MIN_RECTANGLE_AREA": 100,           # Minimum rectangle area
    "MAX_RECTANGLE_AREA": 5000,          # Maximum rectangle area
    "MIN_ASPECT_RATIO": 0.2,             # Minimum aspect ratio
    "MAX_ASPECT_RATIO": 10,              # Maximum aspect ratio
    "FILL_RATIO_THRESHOLD": 0.7,         # Rectangle fill ratio threshold
    "TEXT_ASSIGNMENT_TOLERANCE": 5,      # Text assignment tolerance in pixels
}

# OCR Debug settings for OCR_Rectangle analyzer
OCR_DEBUG_CONFIG = {
    "ENABLE_RECTANGLE_DEBUG": False,     # Enable rectangle detection debugging
    "DEBUG_OUTPUT_DIR": "rectangle_debug", # Debug output directory
}
'''
    
    config_file = Path(__file__).parent / "config_user.py"
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_template)
        print(f"✅ 用戶配置文件已創建：{config_file}")
        print("   請編輯 config_user.py 來設置您要監控的物品")
        return True
    except Exception as e:
        print(f"❌ 創建配置文件失敗：{e}")
        return False

def create_run_script():
    """創建運行腳本"""
    print("\n🚀 創建啟動腳本...")
    
    if platform.system() == "Windows":
        script_content = '''@echo off
chcp 65001 > nul
echo 🎮 MapleStory 交易機會監控系統
echo ================================
echo.
echo 正在啟動監控程式...
python screen_monitor.py
pause
'''
        script_file = Path(__file__).parent / "啟動監控.bat"
        
    else:  # Linux/Mac
        script_content = '''#!/bin/bash
echo "🎮 MapleStory 交易機會監控系統"
echo "================================"
echo ""
echo "正在啟動監控程式..."
python3 screen_monitor.py
read -p "按任意鍵退出..."
'''
        script_file = Path(__file__).parent / "啟動監控.sh"
    
    try:
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        if not platform.system() == "Windows":
            os.chmod(script_file, 0o755)  # 給執行權限
            
        print(f"✅ 啟動腳本已創建：{script_file}")
        return True
    except Exception as e:
        print(f"❌ 創建啟動腳本失敗：{e}")
        return False

def main():
    """主安裝程序"""
    print("🎮 MapleStory 交易機會監控系統 - 自動安裝程式")
    print("=" * 60)
    print("本程式將自動安裝所有必要的組件和依賴")
    print("請確保您有穩定的網路連接")
    print("=" * 60)
    print()
    
    # 檢查Python版本
    if not check_python_version():
        input("\n按Enter鍵退出...")
        sys.exit(1)
    
    # 安裝依賴
    if not install_requirements():
        input("\n安裝失敗，按Enter鍵退出...")
        sys.exit(1)
    
    # 設置OCR
    if not setup_ocr():
        print("⚠️  OCR設置失敗，但程式仍可使用Gemini AI分析")
    
    # 創建配置文件
    if not create_config():
        print("⚠️  配置文件創建失敗，請手動編輯config.py")
    
    # 創建運行腳本
    if not create_run_script():
        print("⚠️  啟動腳本創建失敗，請手動運行 python screen_monitor.py")
    
    print("\n" + "=" * 60)
    print("🎉 安裝完成！")
    print("=" * 60)
    print("📋 後續步驟：")
    print("1. 編輯 config_user.py 設置您要監控的物品")
    print("2. 執行「啟動監控.bat」開始使用")
    print("3. 首次運行時選擇遊戲聊天視窗作為監控區域")
    print("4. 享受自動化交易機會監控！")
    print("=" * 60)
    print()
    input("按Enter鍵完成安裝...")

if __name__ == "__main__":
    main()