#!/usr/bin/env python3
"""OCR依賴安裝腳本"""

import subprocess
import sys
import os

def run_command(command, description):
    """執行命令並顯示結果"""
    print(f"\n🔄 {description}...")
    print(f"執行: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description}成功")
        if result.stdout:
            print(f"輸出: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description}失敗")
        print(f"錯誤: {e.stderr.strip()}")
        return False

def check_python_version():
    """檢查Python版本"""
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("⚠️  警告：建議使用Python 3.8或更新版本")
        return False
    
    print("✅ Python版本符合要求")
    return True

def install_ocr_dependencies():
    """安裝OCR依賴"""
    print("螢幕監控程式 - OCR依賴安裝")
    print("=" * 50)
    
    # 檢查Python版本
    if not check_python_version():
        choice = input("是否繼續安裝？(y/n): ")
        if choice.lower() not in ['y', 'yes']:
            return False
    
    # 升級pip
    print("\n📦 準備安裝依賴...")
    run_command(f"{sys.executable} -m pip install --upgrade pip", "升級pip")
    
    # 安裝基本依賴
    basic_packages = [
        "numpy>=1.21.0",
        "opencv-python>=4.5.0", 
        "Pillow>=8.0.0",
        "easyocr>=1.6.0"
    ]
    
    print("\n📋 安裝清單:")
    for package in basic_packages:
        print(f"  - {package}")
    
    confirm = input("\n確認安裝以上套件？(y/n): ")
    if confirm.lower() not in ['y', 'yes']:
        print("安裝已取消")
        return False
    
    # 逐個安裝套件
    success_count = 0
    for package in basic_packages:
        if run_command(f"{sys.executable} -m pip install {package}", 
                      f"安裝 {package.split('>=')[0]}"):
            success_count += 1
        else:
            print(f"⚠️  {package} 安裝失敗，但繼續安裝其他套件...")
    
    print(f"\n📊 安裝結果: {success_count}/{len(basic_packages)} 個套件安裝成功")
    
    if success_count == len(basic_packages):
        print("🎉 所有依賴安裝完成！")
        return True
    else:
        print("⚠️  部分依賴安裝失敗，可能影響OCR功能")
        return False

def test_installation():
    """測試安裝結果"""
    print("\n🧪 測試OCR功能...")
    
    try:
        import easyocr
        print(f"✅ EasyOCR安裝成功，版本: {easyocr.__version__}")
        
        print("🔄 初始化OCR引擎...")
        reader = easyocr.Reader(['en'], verbose=False)
        print("✅ OCR引擎初始化成功")
        
        return True
    except ImportError as e:
        print(f"❌ EasyOCR導入失敗: {e}")
        return False
    except Exception as e:
        print(f"❌ OCR測試失敗: {e}")
        return False

def main():
    """主程式"""
    print("歡迎使用OCR依賴安裝程式！")
    print("\n此程式將安裝以下套件：")
    print("- EasyOCR (文字識別)")
    print("- OpenCV (圖像處理)")  
    print("- NumPy (數值計算)")
    print("- Pillow (圖像庫)")
    
    print("\n⚠️  注意事項：")
    print("1. 首次安裝可能需要較長時間")
    print("2. EasyOCR會自動下載語言模型（~100MB）")
    print("3. 需要穩定的網路連線")
    
    choice = input("\n是否開始安裝？(y/n): ")
    if choice.lower() not in ['y', 'yes']:
        print("安裝已取消")
        return
    
    # 安裝依賴
    install_success = install_ocr_dependencies()
    
    if install_success:
        # 測試安裝
        if test_installation():
            print("\n🎉 安裝完成！您現在可以使用OCR功能了")
            print("\n使用方式：")
            print("python screen_monitor.py  # 選擇OCR分析方法")
            print("python test_ocr.py        # 測試OCR功能")
        else:
            print("\n⚠️  安裝完成但測試失敗，請檢查安裝狀態")
    else:
        print("\n❌ 安裝失敗，請手動安裝依賴")
        print("\n手動安裝指令：")
        print("pip install easyocr opencv-python numpy Pillow")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n安裝被中斷")
    except Exception as e:
        print(f"\n❌ 安裝程式發生錯誤: {e}")
        print("請嘗試手動安裝：pip install easyocr")