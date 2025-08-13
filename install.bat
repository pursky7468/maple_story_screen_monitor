@echo off
chcp 65001 > nul
title MapleStory 交易機會監控系統 - 一鍵安裝

echo.
echo ╔════════════════════════════════════════════╗
echo ║     🎮 MapleStory 交易機會監控系統         ║
echo ║           一鍵安裝程式 v1.0               ║
echo ╚════════════════════════════════════════════╝
echo.
echo 🚀 歡迎使用 MapleStory 交易機會監控系統！
echo.
echo 本程式將為您自動安裝所有必要的組件：
echo   ✓ Python 依賴包
echo   ✓ OCR 語言模型 (~100MB)
echo   ✓ 系統配置文件
echo   ✓ 啟動腳本
echo.
echo ⚠️  安裝注意事項：
echo   • 請確保已安裝 Python 3.8 或更高版本
echo   • 請確保有穩定的網路連接
echo   • 安裝過程可能需要 5-10 分鐘
echo.
set /p choice="是否開始安裝？(Y/N): "
if /i "%choice%" neq "Y" (
    echo 安裝已取消
    pause
    exit /b
)

echo.
echo 🔍 檢查 Python 環境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤：未找到 Python 或 Python 未添加到系統 PATH
    echo.
    echo 請先安裝 Python 3.8+ 並確保添加到系統 PATH：
    echo   1. 訪問 https://www.python.org/downloads/
    echo   2. 下載並安裝最新版本的 Python
    echo   3. 安裝時勾選 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo ✅ Python 環境檢查完成
echo.
echo 🚀 開始執行安裝程式...
echo.

python setup.py

echo.
echo 🎉 安裝流程完成！
echo.
echo 📂 安裝文件說明：
echo   • config_user.py    - 用戶配置文件（請編輯此文件設置監控物品）
echo   • 啟動監控.bat      - 一鍵啟動腳本
echo   • USER_MANUAL.md    - 詳細使用說明
echo.
echo 🔧 下一步操作：
echo   1. 編輯 config_user.py 設置您要監控的物品
echo   2. 雙擊「啟動監控.bat」開始使用
echo.
pause